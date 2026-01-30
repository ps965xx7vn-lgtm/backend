# Notifications Application

Приложение системы уведомлений платформы Pyland School.

## Описание

Notifications отвечает за централизованное управление подписками и отправку уведомлений пользователям через различные каналы: Email, SMS, Telegram.

## Модели

### Subscription
Централизованная система управления подписками для всей платформы:
- **email** - уникальный email адрес (в комбинации с типом подписки)
- **subscription_type** - тип подписки (выбор из SUBSCRIPTION_TYPE_CHOICES)
- **name** - имя подписчика (опционально)
- **is_active** - активность подписки
- **preferences** - дополнительные настройки (JSON)
- **created_at** - дата подписки
- **updated_at** - дата последнего обновления

#### Типы подписок (subscription_type)

Типы подписок **полностью соответствуют** настройкам уведомлений в модели Student:

1. **email_notifications** (📧) - Все email уведомления
   - По умолчанию включено для всех пользователей
   - Базовый тип подписки

2. **course_updates** (📚) - Обновления курсов
   - Новые уроки и материалы
   - Изменения в структуре курса

3. **lesson_reminders** (⏰) - Напоминания о уроках
   - Напоминания о невыполненных заданиях
   - Дедлайны и важные даты

4. **achievement_alerts** (🏆) - Уведомления о достижениях
   - Получение новых достижений
   - Прогресс в обучении

5. **weekly_summary** (📊) - Еженедельная сводка
   - Статистика прогресса за неделю
   - Рекомендации по обучению

6. **marketing_emails** (🎁) - Маркетинговые письма
   - Акции и специальные предложения
   - Новости платформы
   - По умолчанию выключено

#### Централизация подписок

**Важно:** Все подписки должны храниться **только** в модели `Subscription`.
Не допускается дублирование в других приложениях (blog, courses и т.д.).

#### Уникальность

Комбинация `(email, subscription_type)` уникальна - один email может иметь разные типы подписок.

### Методы класса Subscription

#### subscribe()
```python
subscription, created = Subscription.subscribe(
    email='user@example.com',
    subscription_type='email_notifications',
    name='John Doe',  # опционально
    preferences={'source': 'blog'}  # опционально
)
```

#### unsubscribe()
```python
Subscription.unsubscribe(
    email='user@example.com',
    subscription_type='email_notifications'
)
```

### Планируемые модели

#### NotificationSettings
Настройки уведомлений пользователя:
- **user** - пользователь
- **email_enabled** - включены ли email
- **sms_enabled** - включены ли SMS
- **telegram_enabled** - включен ли Telegram
- **notification_types** - типы уведомлений (JSON)

#### NotificationLog
Журнал отправленных уведомлений:
- **user** - получатель
- **notification_type** - тип уведомления
- **channel** - канал отправки
- **status** - статус доставки
- **sent_at** - дата отправки
- **delivered_at** - дата доставки

## Каналы отправки

### 1. Email (основной)
```python
from django.core.mail import send_mail

send_mail(
    subject='Тема',
    message='Текст',
    from_email='noreply@pyland.school',
    recipient_list=['user@example.com'],
)
```

### 2. SMS (через Twilio)
```python
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    body="Текст SMS",
    from_='+1234567890',
    to='+9876543210'
)
```

### 3. Telegram Bot
```python
import telegram

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
bot.send_message(
    chat_id=user.telegram_chat_id,
    text="Текст сообщения"
)
```

## Типы уведомлений

### Для студентов
- `course_updates` - обновления курса
- `lesson_reminders` - напоминания об уроках
- `submission_reviewed` - работа проверена
- `achievement_unlocked` - достижение получено
- `certificate_issued` - сертификат готов

### Для ревьюеров
- `new_submission` - новая работа на проверку
- `submission_resubmitted` - повторная отправка

### Для всех
- `weekly_summary` - еженедельная сводка
- `system_announcements` - объявления платформы
- `password_reset` - сброс пароля
- `email_verification` - подтверждение email

## Celery задачи

### Асинхронная отправка
```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id, notification_type, data):
    try:
        user = User.objects.get(id=user_id)
        # Проверка настроек
        if not user.notification_settings.email_enabled:
            return
        # Отправка
        send_mail(...)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

### Периодические задачи
```python
@periodic_task(run_every=crontab(hour=9, minute=0))
def send_daily_reminders():
    """Ежедневные напоминания в 9:00"""
    ...

@periodic_task(run_every=crontab(day_of_week=1, hour=10))
def send_weekly_summary():
    """Еженедельная сводка по понедельникам в 10:00"""
    ...
```

## API Endpoints (планируется)

### Настройки
```
GET    /api/notifications/settings          - Получить настройки
PATCH  /api/notifications/settings          - Обновить настройки
```

### Подписка
```
POST   /api/notifications/subscribe         - Подписаться
POST   /api/notifications/unsubscribe       - Отписаться
```

### История
```
GET    /api/notifications/history           - История уведомлений
POST   /api/notifications/{id}/mark-read    - Отметить прочитанным
```

### Telegram
```
POST   /api/notifications/telegram/connect  - Подключить Telegram
POST   /api/notifications/telegram/disconnect - Отключить
```

## Views

### subscribe_view
Обработка подписки на email рассылку:
- Валидация email
- Проверка на дубликаты
- Сохранение в БД
- Flash message о результате
- Редирект на предыдущую страницу

## Шаблоны писем

### Структура
```
templates/emails/
├── base.html                  # Базовый шаблон
├── course_update.html         # Обновление курса
├── submission_reviewed.html   # Работа проверена
├── certificate_issued.html    # Сертификат готов
└── weekly_summary.html        # Еженедельная сводка
```

### Пример
```html
{% extends 'emails/base.html' %}
{% block content %}
<h2>Ваша работа проверена!</h2>
<p>Здравствуйте, {{ student.first_name }}!</p>
<p>Ваша работа по уроку "{{ lesson.name }}" была проверена.</p>
<p>Статус: <strong>{{ submission.status }}</strong></p>
<a href="{{ submission_url }}">Посмотреть замечания</a>
{% endblock %}
```

## Настройки уведомлений

### Пользовательские
В профиле студента:
- ✅ Email уведомления
- ✅ SMS уведомления
- ⬜ Telegram уведомления
- Выбор типов уведомлений

### Глобальные
В admin панели:
- Включение/выключение каналов
- Лимиты отправки
- Шаблоны по умолчанию

## Защита от спама

### Rate limiting
```python
from django.core.cache import cache

def check_notification_limit(user_id, notification_type):
    key = f"notification:{user_id}:{notification_type}"
    count = cache.get(key, 0)
    if count >= 10:  # Максимум 10 в час
        return False
    cache.set(key, count + 1, 3600)
    return True
```

### Unsubscribe link
Каждое письмо содержит ссылку отписки:
```python
unsubscribe_url = f"{settings.SITE_URL}/notifications/unsubscribe/{token}"
```

## Мониторинг

### Метрики
- Количество отправленных уведомлений
- Процент доставки
- Процент открытий (email)
- Процент кликов
- Ошибки отправки

### Логирование
```python
import logging
logger = logging.getLogger('notifications')

logger.info(f"Email sent to {user.email}: {notification_type}")
logger.error(f"Failed to send SMS to {user.phone}: {error}")
```

## Интеграция с сервисами

### SendGrid (Email)
```python
SENDGRID_API_KEY = env('SENDGRID_API_KEY')
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
```

### Twilio (SMS)
```python
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER')
```

### Telegram Bot
```python
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_WEBHOOK_URL = f"{SITE_URL}/api/notifications/telegram/webhook"
```

## Связанные приложения

- **authentication** - регистрация, сброс пароля
- **courses** - обновления курсов
- **students** - напоминания об уроках
- **reviewers** - уведомления о работах
- **certificates** - выдача сертификатов

## Тестирование

### Mock отправка
```python
from django.core import mail

def test_send_email():
    # Отправка
    send_notification(user, 'test')
    # Проверка
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'Test'
```

### Запуск тестов
```bash
pytest notifications/tests/ -v
```

## Авторы

Pyland Team, 2025
