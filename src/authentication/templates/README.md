# Authentication Templates

HTML шаблоны для web-интерфейса системы аутентификации.

## 📋 Структура

```text
templates/auth/
├── signin.html                 # Форма входа
├── signup.html                 # Форма регистрации
├── password_reset.html         # Запрос сброса пароля
├── password_reset_confirm.html # Подтверждение нового пароля
├── email_verification.html     # Страница подтверждения email
└── email/                      # Email шаблоны
    ├── verification.html       # Письмо верификации
    └── password_reset.html     # Письмо сброса пароля
```text
---

## Шаблоны страниц

### signin.html

Страница входа в систему.

**URL:** `/auth/signin/`
**View:** `SignInView`
**Form:** `UserLoginForm`

**Контекст:**

- `form` - Форма входа (email, password)
- `next` - URL для редиректа после входа

**Фичи:**

- CSRF protection
- "Запомнить меня" checkbox
- Ссылка на восстановление пароля
- Ссылка на регистрацию

### signup.html

Страница регистрации нового пользователя.

**URL:** `/auth/signup/`
**View:** `SignUpView`
**Form:** `UserRegisterForm`

**Контекст:**

- `form` - Форма регистрации (email, password, first_name, last_name)

**Фичи:**

- Email валидация
- Password strength requirements
- Password confirmation
- Автоматическая отправка verification email
- Редирект на страницу "проверьте email"

### password_reset.html

Запрос на сброс пароля.

**URL:** `/auth/password-reset/`
**View:** `PasswordResetView`

**Контекст:**

- `form` - Форма с полем email

**Процесс:**

1. Пользователь вводит email
2. Отправляется письмо со ссылкой
3. Ссылка ведет на password_reset_confirm

### password_reset_confirm.html

Установка нового пароля.

**URL:** `/auth/password-reset-confirm/<uidb64>/<token>/`
**View:** `PasswordResetConfirmView`

**Контекст:**

- `form` - Форма с новым паролем
- `validlink` - True если ссылка валидна

**Фичи:**

- Token validation
- Password strength check
- Password confirmation

### email_verification.html

Результат подтверждения email.

**URL:** `/auth/verify-email-confirm/<uidb64>/<token>/`
**View:** `VerifyEmailConfirmView`

**Контекст:**

- `success` - True если email подтвержден
- `error` - Сообщение об ошибке (если есть)

---

## Email шаблоны

### email/verification.html

Письмо для подтверждения email.

**Отправляется:** После регистрации
**Task:** `send_verification_email`

**Контекст:**

- `user` - Объект пользователя
- `activation_url` - Полная ссылка для активации
- `site_name` - Название сайта

**Содержание:**

```text
Привет, {{ user.first_name }}!

Спасибо за регистрацию на {{ site_name }}.

Подтвердите ваш email перейдя по ссылке:
{{ activation_url }}

Ссылка действительна 24 часа.
```text
### email/password_reset.html

Письмо для сброса пароля.

**Отправляется:** После запроса сброса
**Task:** `send_password_reset_email`

**Контекст:**

- `user` - Объект пользователя
- `reset_url` - Полная ссылка для сброса
- `site_name` - Название сайта

**Содержание:**

```text
Привет, {{ user.first_name }}!

Вы запросили сброс пароля на {{ site_name }}.

Установите новый пароль по ссылке:
{{ reset_url }}

Если это были не вы, проигнорируйте это письмо.

Ссылка действительна 24 часа.
```text
---

## Использование в коде

### Рендеринг шаблона во view

```python
from django.shortcuts import render

def my_view(request):
    return render(request, 'auth/signin.html', {
        'form': form,
        'next': request.GET.get('next', '/'),
    })
```text
### Отправка email с шаблоном

```python
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Рендерим HTML

html_content = render_to_string('auth/email/verification.html', {
    'user': user,
    'activation_url': '<https://example.com/verify/...',>
    'site_name': 'Pyland',
})

# Отправляем

email = EmailMessage(
    subject='Подтвердите email',
    body=html_content,
    from_email='noreply@pylandschool.com',
    to=[user.email],
)
email.content_subtype = 'html'
email.send()
```text
### Через Celery task

```python
from authentication.tasks import send_verification_email

send_verification_email.delay(
    user_id=user.id,
    activation_url='<https://example.com/verify/...',>
    subject='Подтвердите email',
    template_name='auth/email/verification.html'
)
```text
---

## Кастомизация

### Базовый шаблон

Все шаблоны extends от `base.html`:

```html
{% extends 'base.html' %}

{% block title %}Sign In - Pyland{% endblock %}

{% block content %}
    <!-- Ваш контент -->
{% endblock %}
```text
### CSS классы

Используются Bootstrap 5 классы:

- `.form-control` - Input fields
- `.btn.btn-primary` - Primary button
- `.alert.alert-danger` - Error messages
- `.card` - Form containers

### JavaScript

HTMX для динамических форм:

```html
<form hx-post="/api/auth/login" hx-target="#result">
    <!-- form fields -->
</form>
```text
---

## Безопасность

### CSRF Protection

Все POST формы должны включать:

```html
{% csrf_token %}
```text
### XSS Protection

Django автоматически экранирует переменные:

```html
{{ user.first_name }}  <!-- Safe -->
{{ user.first_name|safe }}  <!-- Unsafe! -->
```text
### Email Links Security

- Используйте signed tokens (Django's `signing`)
- Ограничивайте время жизни ссылок (24h)
- Инвалидируйте токены после использования

---

## Тестирование шаблонов

```python
from django.test import TestCase
from django.urls import reverse

class TestAuthTemplates(TestCase):
    def test_signin_template(self):
        response = self.client.get(reverse('authentication:signin'))
        self.assertTemplateUsed(response, 'auth/signin.html')
        self.assertContains(response, 'Sign In')

    def test_signup_template(self):
        response = self.client.get(reverse('authentication:signup'))
        self.assertTemplateUsed(response, 'auth/signup.html')
```text
---

## Локализация

Шаблоны поддерживают i18n:

```html
{% load i18n %}

<h1>{% trans "Sign In" %}</h1>
<button>{% trans "Submit" %}</button>
```text
Доступные языки:

- `ru` - Русский
- `en` - English
- `ka` - ქართული (Georgian)

---

## Troubleshooting

### Шаблон не найден

```python

# Проверить TEMPLATES в settings.py

TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,  # Должно быть True
    }
]
```text
### Email не рендерится

```python

# Проверить context

from django.template.loader import render_to_string

html = render_to_string('auth/email/verification.html', {
    'user': user,
    'activation_url': 'test_url',
    'site_name': 'Test',
})
print(html)  # Должен быть HTML
```text
### CSS не применяется

```html
<!-- Проверить static files -->
{% load static %}
<link rel="stylesheet" href="{% static 'css/auth.css' %}">
```text
---

## Best Practices

1. **Всегда используйте CSRF token** в POST формах
2. **Экранируйте пользовательский ввод** (Django делает автоматически)
3. **Используйте HTTPS** для форм с паролями
4. **Показывайте понятные ошибки** пользователям
5. **Responsive дизайн** - проверяйте на мобильных
6. **Accessibility** - используйте семантичный HTML
7. **Email templates** - plain text альтернатива для HTML

---

## Статус

✅ **Production Ready**

- Все шаблоны протестированы
- CSRF protection включен
- XSS protection активна
- Email templates работают
- Responsive design
- i18n поддержка
