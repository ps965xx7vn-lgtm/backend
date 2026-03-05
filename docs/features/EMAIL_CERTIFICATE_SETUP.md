# Настройка автоматической отправки сертификатов по email

## Обзор функциональности

При завершении курса студентом (когда проверяющий принял последнюю обязательную работу):
1. Автоматически создается сертификат
2. Генерируется PDF с QR-кодом
3. Отправляется красивый email с:
   - Ссылкой на скачивание PDF
   - Кнопкой верификации подлинности
   - Номером сертификата и кодом верификации

## Как это работает

### 1. Сигнал в `reviewers/signals.py`

```python
@receiver(post_save, sender=LessonSubmission)
def check_course_completion_and_issue_certificate(sender, instance, **kwargs):
    # Проверяет, все ли обязательные уроки пройдены
    # Если да - создает сертификат и отправляет email
```

### 2. Celery задача в `certificates/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def send_certificate_email(...):
    # Отправляет красивый HTML email
    # С возможностью повтора при ошибке
```

### 3. Email шаблон `certificates/emails/certificate_issued.html`

Красивый HTML шаблон с:
- Градиентным дизайном
- Двумя CTA кнопками
- Адаптивной версткой
- Информацией о сертификате

## Настройка SMTP для production

### Для Gmail

1. Создайте `.env` файл в корне проекта:

```bash
# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

2. Получите App Password для Gmail:
   - Перейдите в Google Account → Security
   - Включите 2-Step Verification
   - Создайте App Password для "Mail"
   - Используйте этот пароль в `EMAIL_HOST_PASSWORD`

### Для других провайдеров

**Yandex:**
```bash
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True  # Вместо TLS
```

**Mail.ru:**
```bash
EMAIL_HOST=smtp.mail.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
```

**SendGrid (рекомендуется для production):**
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

## Тестирование

### 1. Локальное тестирование (консольный backend)

В `.env` установите:
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Email будет выводиться в консоль, где запущен сервер.

### 2. Тестирование через Django shell

```python
from django.contrib.auth import get_user_model
from certificates.models import Certificate
from courses.models import Course
from certificates.tasks import send_certificate_email
from django.conf import settings

User = get_user_model()

# Получаем пользователя
user = User.objects.get(email='test@example.com')
student = user.student

# Получаем курс
course = Course.objects.first()

# Создаем сертификат
cert = Certificate.objects.create(
    student=student,
    course=course,
    completion_date=timezone.now().date()
)

# Генерируем PDF
from certificates.utils import generate_certificate_pdf
pdf_path = generate_certificate_pdf(cert)

# Отправляем email
pdf_url = f'{settings.SITE_URL}{settings.MEDIA_URL}{cert.pdf_file}'
send_certificate_email(
    student_email=user.email,
    student_name=user.get_full_name() or user.username,
    course_name=course.name,
    certificate_number=cert.certificate_number,
    verification_code=cert.verification_code,
    pdf_url=pdf_url
)
```

### 3. Автоматическое тестирование через signal

Просто одобрите последнюю обязательную работу студента через:
- Django admin
- Reviewers dashboard
- API endpoint

Сертификат автоматически создастся и отправится на email.

## Верификация сертификатов

После получения email студент может:

1. **Скачать PDF** - кликнув зеленую кнопку
2. **Проверить подлинность** - перейдя по синей кнопке на `/certificates/verify/`

На странице верификации:
- Красивый hero banner (как на blog)
- Форма ввода кода верификации
- Отображение всех данных сертификата
- QR-код для быстрой проверки

## Просмотр отправленных сертификатов

### Django Admin

```
http://127.0.0.1:8000/admin/certificates/certificate/
```

Показывает:
- Список всех сертификатов
- Дата выдачи
- Студент и курс
- Статус (действителен/отозван)
- Ссылка на PDF

### API Endpoint

```python
# GET /api/certificates/?student_id=123
# Возвращает все сертификаты студента
```

## Мониторинг

### Celery логи

```bash
# Смотрим логи Celery worker
celery -A pyland worker -l info

# Проверяем задачи в очереди
celery -A pyland inspect active
```

### Django логи

Все операции логируются в:
```
src/logs/certificate_email.log
```

С информацией:
- Кому отправлен email
- Номер сертификата
- Timestamp
- Статус (успех/ошибка)

## Troubleshooting

### Email не отправляется

1. **Проверьте настройки SMTP:**
   ```bash
   cd src
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

2. **Проверьте Celery работает:**
   ```bash
   celery -A pyland inspect active
   ```

3. **Проверьте Redis доступен:**
   ```bash
   redis-cli ping
   # Должен вернуть: PONG
   ```

### PDF не генерируется

1. **Проверьте Arial Unicode шрифт:**
   ```bash
   ls /System/Library/Fonts/Supplemental/Arial\ Unicode.ttf
   ```

2. **Проверьте права на media папку:**
   ```bash
   chmod 755 src/media/certificates/
   ```

### Fallback механизм

Если Celery недоступен, email отправится **синхронно** прямо из сигнала.
Это гарантирует, что студент получит сертификат даже при проблемах с Celery.

## Дальнейшие улучшения

1. **Email шаблоны для разных языков** (ru/en/ka)
2. **Push-уведомления** через Telegram bot
3. **SMS-уведомления** для важных сертификатов
4. **Email с напоминанием** через неделю о необходимости проверить сертификат
5. **Статистика открытий** email (через tracking pixels)

## Полезные команды

```bash
# Запустить Celery worker
cd src
celery -A pyland worker -l info

# Запустить Celery beat (для периодических задач)
celery -A pyland beat -l info

# Проверить конфигурацию email
python manage.py sendtestemail your-email@example.com

# Сгенерировать все отсутствующие PDF
python manage.py generate_missing_pdfs

# Переотправить email для сертификата
python manage.py resend_certificate_email --cert-number=CERT-20260203-E930
```

## Security

- **Verification codes** - генерируются с использованием SECRET_KEY
- **Unique certificate numbers** - формат CERT-YYYYMMDD-XXXX с UUID
- **QR codes** - содержат ссылку на публичную верификацию
- **PDF protection** - можно добавить watermark или encryption

## Production Checklist

- [ ] Настроены SMTP credentials в .env
- [ ] Celery worker запущен и мониторится
- [ ] Redis доступен и настроен persistence
- [ ] Email шаблон протестирован на разных клиентах (Gmail, Outlook, Apple Mail)
- [ ] Логирование настроено и мониторится
- [ ] Fallback механизм протестирован
- [ ] Retry политика настроена (max 3 попытки)
- [ ] Rate limiting настроен для email отправки
- [ ] Backup системы для Celery queue

---

**Автор:** Pyland Team
**Обновлено:** 2026-02-03
**Версия:** 1.0
