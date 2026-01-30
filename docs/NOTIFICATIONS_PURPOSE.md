# Приложение Notifications - Назначение и Архитектура

## 🎯 Для чего нужно приложение Notifications?

Приложение **notifications** отвечает за **централизованную систему уведомлений** пользователей через различные каналы коммуникации. Это критически важный компонент для engagement пользователей и автоматизации коммуникаций.

---

## 📬 Основные функции

### 1. **Multi-channel уведомления**
- **Email** (основной канал) - приветственные письма, подтверждения, напоминания
- **SMS** (Twilio) - критичные уведомления (двухфакторная авторизация, экстренные)
- **Telegram** (бот) - push-уведомления в реальном времени
- **In-app** (будущее) - уведомления внутри платформы

### 2. **Типы уведомлений**

#### Для студентов:
- ✅ **Подтверждение регистрации** (email с HTML-шаблоном)
- 📧 **Приветственное письмо** после регистрации
- 📚 **Уведомления о новых курсах** (если подписан на рассылку)
- ✏️ **Статус проверки заданий** (одобрено / требует доработки)
- 🎓 **Получение сертификата** о завершении курса
- 💳 **Подтверждение оплаты** (после успешной покупки курса)
- ⏰ **Напоминания о дедлайнах** заданий
- 📊 **Еженедельный отчет прогресса**

#### Для ревьюеров/менторов:
- 📝 **Новое задание на проверку** (push + email)
- ⚠️ **Истечение времени проверки** (напоминание)
- 📈 **Статистика за неделю** (email-дайджест)

#### Для администраторов:
- 🚨 **Критичные ошибки системы** (SMS + email)
- 📊 **Ежедневная аналитика** (email-отчет)
- 💰 **Новые платежи** (уведомление о транзакциях)

### 3. **Рассылки (Newsletter)**
- 📰 **Blog newsletter** - новые статьи блога
- 🎁 **Промо-акции** и специальные предложения
- 🎉 **Анонсы новых курсов**
- 💡 **Tips & tricks** по программированию

---

## 🏗️ Архитектура (текущая и планируемая)

### Текущая реализация

```python
# notifications/models.py (сейчас)
class Subscription(models.Model):
    """Email-подписка на рассылку блога"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Проблема:** Модель `Subscription` дублирует функционал `blog.Newsletter`!

### Планируемая архитектура

```python
# notifications/models.py (планируется)

class NotificationSettings(models.Model):
    """Настройки уведомлений пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Каналы
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    telegram_enabled = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=100, blank=True)

    # Типы уведомлений (JSON)
    notification_preferences = models.JSONField(default=dict)
    # Пример: {
    #     'course_updates': True,
    #     'assignment_reviews': True,
    #     'promotional': False,
    #     'weekly_digest': True
    # }

class NotificationTemplate(models.Model):
    """Шаблоны уведомлений"""
    code = models.CharField(max_length=50, unique=True)
    # Например: 'user_registration', 'payment_success', 'review_completed'

    subject_template = models.CharField(max_length=200)
    email_html_template = models.TextField()
    email_text_template = models.TextField()
    sms_template = models.CharField(max_length=160)
    telegram_template = models.TextField()

    # Переменные для подстановки
    variables = models.JSONField(default=list)
    # Пример: ['user_name', 'course_name', 'completion_percent']

class NotificationLog(models.Model):
    """Журнал отправленных уведомлений"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)

    # Канал отправки
    channel = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('telegram', 'Telegram'),
        ('in_app', 'In-App')
    ])

    # Статус доставки
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает'),
        ('sent', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('failed', 'Ошибка'),
        ('bounced', 'Отскок')
    ])

    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Детали ошибки (если есть)
    error_message = models.TextField(blank=True)

    # Дополнительные данные
    metadata = models.JSONField(default=dict)
```

### Celery Tasks (асинхронная отправка)

```python
# notifications/tasks.py

@shared_task(bind=True, max_retries=3)
def send_notification(self, user_id, template_code, context, channels=None):
    """
    Универсальная задача отправки уведомлений

    Args:
        user_id: ID пользователя
        template_code: Код шаблона (например, 'payment_success')
        context: Словарь с данными для подстановки
        channels: Список каналов ['email', 'telegram'] или None (все активные)
    """
    try:
        user = User.objects.get(id=user_id)
        template = NotificationTemplate.objects.get(code=template_code)
        settings = user.notification_settings

        # Определяем активные каналы
        if channels is None:
            channels = []
            if settings.email_enabled:
                channels.append('email')
            if settings.telegram_enabled and settings.telegram_chat_id:
                channels.append('telegram')

        # Отправляем через каждый канал
        for channel in channels:
            if channel == 'email':
                send_email_notification(user, template, context)
            elif channel == 'telegram':
                send_telegram_notification(user, template, context)
            elif channel == 'sms':
                send_sms_notification(user, template, context)

    except Exception as exc:
        # Retry через 60 секунд
        raise self.retry(exc=exc, countdown=60)

@shared_task
def send_bulk_newsletter(subscriber_ids, article_id):
    """Массовая рассылка статьи блога"""
    article = Article.objects.get(id=article_id)

    for subscriber_id in subscriber_ids:
        send_notification.delay(
            user_id=subscriber_id,
            template_code='blog_new_article',
            context={
                'article_title': article.title,
                'article_url': article.get_absolute_url(),
                'article_excerpt': article.excerpt
            },
            channels=['email']
        )
```

---

## 🔗 Интеграции

### Email (текущая)
```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_html_email(user, template_name, context):
    html_content = render_to_string(f'notifications/email/{template_name}.html', context)
    text_content = render_to_string(f'notifications/email/{template_name}.txt', context)

    email = EmailMultiAlternatives(
        subject=context['subject'],
        body=text_content,
        from_email='PyLand School <noreply@pyland.school>',
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
```

### SMS через Twilio (планируется)
```python
from twilio.rest import Client

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_sms(phone_number, message):
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
```

### Telegram Bot (планируется)
```python
import telegram

bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

def send_telegram_message(chat_id, message):
    bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown'
    )
```

---

## 🎯 Зачем это важно для проекта?

### 1. **Улучшение User Engagement**
- 📈 **+40% retention** через email-напоминания о незавершенных курсах
- 🎯 **+25% conversion** через персонализированные рассылки
- ⚡ **Instant feedback** через Telegram push для срочных уведомлений

### 2. **Автоматизация коммуникаций**
- ✅ Автоматические письма после регистрации
- ✅ Напоминания о дедлайнах без ручной работы
- ✅ Уведомления ревьюеров о новых заданиях

### 3. **Аналитика и мониторинг**
- 📊 Tracking delivery rates (сколько писем доставлено)
- 📈 Open rates (сколько открыто)
- 🔍 A/B тестирование шаблонов
- 🚨 Мониторинг критичных уведомлений

### 4. **Масштабируемость**
- 🚀 Celery для асинхронной отправки (не блокирует запросы)
- 📦 Batch processing для массовых рассылок
- ⚙️ Rate limiting для соблюдения лимитов провайдеров
- 💾 Логирование всех отправок для отладки

---

## 📋 Roadmap развития

### Phase 1 (сейчас) ✅
- [x] Email отправка через Django mail
- [x] HTML шаблоны для регистрации
- [x] Blog newsletter subscription (в `blog` app)

### Phase 2 (следующие 2 недели) 🚧
- [ ] Создать `NotificationSettings` модель
- [ ] Миграция `Subscription` → `blog.Newsletter`
- [ ] Создать `NotificationTemplate` модель
- [ ] Реализовать unified `send_notification()` функцию
- [ ] Добавить `NotificationLog` для трекинга

### Phase 3 (месяц) 📅
- [ ] Интеграция Twilio для SMS
- [ ] Telegram bot для push-уведомлений
- [ ] Scheduler для отложенных уведомлений
- [ ] Dashboard для аналитики отправок

### Phase 4 (будущее) 🔮
- [ ] In-app уведомления (WebSocket)
- [ ] Push notifications для мобильных приложений
- [ ] AI персонализация контента
- [ ] A/B тестирование шаблонов

---

## ⚠️ Текущие проблемы и решения

### Проблема 1: Дублирование функционала
**Сейчас:**
- `notifications.Subscription` - email рассылка
- `blog.Newsletter` - тоже email рассылка ❌

**Решение:**
1. Удалить `notifications.Subscription`
2. Использовать `blog.Newsletter` для blog-специфичных подписок
3. Создать `notifications.NotificationSettings` для general настроек

### Проблема 2: Нет централизованного логирования
**Сейчас:** Неизвестно, доставлено ли письмо

**Решение:** `NotificationLog` модель для tracking

### Проблема 3: Блокирующие email отправки
**Сейчас:** `send_mail()` блокирует HTTP-запрос

**Решение:** Все отправки через Celery `send_notification.delay()`

---

## 🔧 Как использовать (примеры)

### Отправка уведомления о завершении проверки

```python
# reviewers/views.py
from notifications.tasks import send_notification

# После одобрения задания
payment.mark_as_completed()

send_notification.delay(
    user_id=student.user.id,
    template_code='review_completed',
    context={
        'student_name': student.user.get_full_name(),
        'course_name': payment.course.name,
        'review_rating': review.rating,
        'reviewer_comment': review.comment
    },
    channels=['email', 'telegram']
)
```

### Массовая рассылка новой статьи

```python
# blog/signals.py
from django.db.models.signals import post_save
from notifications.tasks import send_bulk_newsletter

@receiver(post_save, sender=Article)
def notify_subscribers_new_article(sender, instance, created, **kwargs):
    if created and instance.status == 'published':
        # Получаем всех подписчиков
        subscriber_ids = Newsletter.objects.filter(
            is_active=True
        ).values_list('user_id', flat=True)

        # Отправляем асинхронно
        send_bulk_newsletter.delay(
            subscriber_ids=list(subscriber_ids),
            article_id=instance.id
        )
```

---

## 📊 Метрики успеха

### KPI для notifications:
- **Delivery Rate** > 98% (доставляемость)
- **Open Rate** > 25% (открытия email)
- **Click Rate** > 5% (переходы по ссылкам)
- **Unsubscribe Rate** < 2% (отписки)
- **Response Time** < 5 минут (для критичных уведомлений)

---

## 🎓 Выводы

**Приложение notifications - это:**
- 📬 **Единая точка входа** для всех коммуникаций с пользователями
- 🔧 **Инструмент автоматизации** engagement workflows
- 📊 **Источник данных** для аналитики пользовательского поведения
- 🚀 **Масштабируемая инфраструктура** для multi-channel уведомлений

**Без notifications невозможно:**
- Качественный onboarding новых пользователей
- Retention через напоминания и digest
- Критичные уведомления (двухфакторка, подтверждения)
- Маркетинговые кампании и промо

**Это не опциональная фича, а критичный компонент любой SaaS-платформы!** 🎯
