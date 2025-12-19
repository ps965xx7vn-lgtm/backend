# Authentication App

Полнофункциональная система аутентификации и управления пользователями для Pyland.

## Обзор

Authentication app - это ядро системы управления пользователями Pyland, предоставляющее:

- ✅ Регистрацию и аутентификацию
- ✅ JWT токены для API
- ✅ Ролевую систему (6 ролей)
- ✅ Email верификацию
- ✅ Сброс пароля
- ✅ Профили пользователей
- ✅ Social authentication (Google, GitHub, etc.)

**Технологии:**

- Django 5.2.3
- Django Ninja 1.4.3 (REST API)
- ninja-jwt 5.3.7 (JWT auth)
- Pydantic 2.11.10 (валидация)
- Celery (async tasks)

---

## Возможности

### Для пользователей

- Регистрация с email верификацией
- Вход через email/password или social auth
- Управление профилем (аватар, персональная информация)
- Смена пароля
- Восстановление пароля через email
- Многоролевая система

### Для разработчиков

- REST API (OpenAPI документация)
- JWT authentication
- Готовые Pydantic schemas
- Management commands для setup
- Comprehensive test suite (90+ tests)
- Factory Boy factories для тестов

---

## Модели данных

### User (Пользователь)

Кастомная модель пользователя с email как username.

**Поля:**

- `email` - Email (unique, используется для входа)
- `first_name`, `last_name` - Имя и фамилия
- `is_active` - Активен ли аккаунт
- `email_verified` - Подтвержден ли email
- `date_joined` - Дата регистрации
- `roles` - M2M связь с Role

**Методы:**

- `get_full_name()` - Полное имя
- `get_short_name()` - Короткое имя (email)

### Role (Роль)

Роли пользователей в системе.

**Роли:**

1. **student** - Студент (по умолчанию)
2. **mentor** - Ментор (помощь студентам)
3. **reviewer** - Ревьюер (проверка работ)
4. **manager** - Менеджер (управление платформой)
5. **admin** - Администратор (полный доступ)
6. **support** - Поддержка (помощь пользователям)

### Profile Models

Расширенные профили для каждой роли:

- **Student** - Информация о студенте (пол, дата рождения, страна)
- **Mentor** - Профиль ментора (экспертные области)
- **Reviewer** - Профиль ревьюера (статистика проверок)
- **Manager** - Профиль менеджера
- **Admin** - Профиль администратора
- **Support** - Профиль саппорта

**Auto-создание:** Профили создаются автоматически при добавлении роли
(через Django signals).

---

## API Endpoints

Base URL: `/api/auth/`

### Регистрация и вход

**POST** `/register`

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```text
**Response:**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["student"]
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```text
**POST** `/login`

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```text
### Профиль

**GET** `/profile` - Получить профиль (требует JWT)

**PATCH** `/profile` - Обновить профиль

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "avatar": "base64_image_data"
}
```text
### Пароль

**POST** `/password/change` - Сменить пароль (требует JWT)

```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "confirm_new_password": "NewPass123!"
}
```text
**POST** `/password/reset` - Запросить сброс пароля

```json
{
  "email": "user@example.com"
}
```text
**POST** `/password/reset/confirm` - Подтвердить сброс пароля

```json
{
  "uid": "base64_encoded_uid",
  "token": "reset_token",
  "password": "NewPass123!",
  "confirm_password": "NewPass123!"
}
```text
### Email верификация

**POST** `/email/resend` - Отправить письмо верификации повторно (требует JWT)

**GET** `/email/verify/{uid}/{token}` - Подтвердить email

### Logout

**POST** `/logout` - Выход (инвалидация refresh token)

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```text
**Документация:** <http://localhost:8000/api/docs> (Swagger UI)

---

## Management Commands

### create_roles

Создает базовые роли пользователей.

```bash
cd src
poetry run python manage.py create_roles
```text
**Создает роли:**

- student (Студент)
- mentor (Ментор)
- reviewer (Ревьюер)
- manager (Менеджер)
- admin (Администратор)
- support (Поддержка)

**Безопасность:** Команда идемпотентна - можно запускать многократно.

### create_test_users

Создает тестовых пользователей для разработки.

```bash

# Базовые тестовые пользователи (по одному каждой роли)

poetry run python manage.py create_test_users

# + 10 дополнительных студентов

poetry run python manage.py create_test_users --count 10

# Удалить существующих и создать заново

poetry run python manage.py create_test_users --clear
```text
**Credentials:**

- `student@test.com` / `password123`
- `mentor@test.com` / `password123`
- `reviewer@test.com` / `password123`
- `manager@test.com` / `password123`
- `admin@test.com` / `password123`
- `support@test.com` / `password123`

### create_superadmin

Создает суперпользователя с предустановленными данными для быстрого развёртывания.

```bash
cd src
poetry run python manage.py create_superadmin
```text
**Credentials:**

- Email: `a@mail.ru`
- Password: `a`
- Права: superuser + staff
- Email verified: ✅

**Опции:**

```bash

# Пересоздать если уже существует

poetry run python manage.py create_superadmin --delete-existing
```text
**⚠️ Важно:** Используйте только для разработки/тестирования! В продакшене смените пароль.

---

## Тестирование

### Запуск тестов

```bash
cd src

# Все authentication тесты

./authentication/tests/run_tests.sh

# Или вручную

poetry run pytest authentication/tests/ -v
```text
### Статистика тестов

- **Всего тестов:** 104
- **Passing:** 90 (86.5%)
- **Skipped:** 14 (13.5%)
- **Coverage:** Все критичные пути

**Тестируется:**

- ✅ Models (35 tests)
- ✅ Forms (12 tests)
- ✅ Signals (11 tests)
- ✅ API endpoints (23 tests)
- ✅ Django views (18 tests)
- ✅ Integration flows (5 tests)

**Подробнее:** См. `tests/README.md`

---

## Использование

### Setup проекта

```bash

# 1. Создать роли

cd src
poetry run python manage.py create_roles

# 2. Создать superuser

poetry run python manage.py createsuperuser

# 3. (Опционально) Создать тестовых пользователей

poetry run python manage.py create_test_users

# 4. Запустить сервер

poetry run python manage.py runserver
```text
### В коде

#### Проверка роли пользователя

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='user@example.com')

# Проверить роль

if user.roles.filter(name='student').exists():
    print("Это студент")

# Получить все роли

user_roles = user.roles.all()
```text
#### Создание пользователя с ролью

```python
from authentication.models import User, Role

# Создать пользователя

user = User.objects.create_user(
    email='newuser@example.com',
    password='SecurePass123!',
    first_name='New',
    last_name='User'
)

# Добавить роль

student_role = Role.objects.get(name='student')
user.roles.add(student_role)

# Профиль создастся автоматически через signal

```text
#### JWT Authentication в API

```python
from ninja import Router
from ninja_jwt.authentication import JWTAuth

router = Router(auth=JWTAuth(), tags=['Protected'])

@router.get('/protected/')
def protected_endpoint(request):
    user = request.auth  # Текущий пользователь
    return {'user_id': user.id, 'email': user.email}
```text
#### Отправка email через Celery

```python
from authentication.tasks import send_verification_email

# Отправить асинхронно

send_verification_email.delay(
    user_id=user.id,
    activation_url='<https://example.com/verify/...',>
    subject='Подтвердите email',
    template_name='auth/email/verification.html'
)
```text
---

## Структура файлов

```text
authentication/
├── __init__.py                 # App config
├── README.md                   # Эта документация
├── models.py                   # User, Role, Profile модели
├── views.py                    # Django views
├── api.py                      # REST API (Django Ninja)
├── forms.py                    # Django forms
├── schemas.py                  # Pydantic schemas
├── signals.py                  # Django signals
├── tasks.py                    # Celery tasks
├── decorators.py               # Security decorators
├── admin.py                    # Django admin
├── urls.py                     # URL routing
├── apps.py                     # App configuration
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── create_roles.py     # Создание ролей
│       └── create_test_users.py # Создание тестовых пользователей
├── templates/
│   ├── README.md               # Документация шаблонов
│   └── auth/                   # HTML шаблоны
│       ├── signin.html
│       ├── signup.html
│       ├── password_reset.html
│       └── email/              # Email шаблоны
│           ├── verification.html
│           └── password_reset.html
├── tests/
│   ├── README.md               # Документация тестов
│   ├── run_tests.sh            # Тестовый runner
│   ├── conftest.py             # Fixtures
│   ├── factories.py            # Factory Boy
│   ├── test_models.py
│   ├── test_forms.py
│   ├── test_signals.py
│   ├── test_api.py
│   ├── test_views.py
│   └── test_integration.py
└── migrations/                 # Database migrations
```text
---

## Безопасность

### Реализованные меры

- ✅ **Password hashing** - Django PBKDF2
- ✅ **JWT токены** - Short-lived access, long-lived refresh
- ✅ **Email verification** - Обязательная верификация
- ✅ **CSRF protection** - Django default
- ✅ **Rate limiting** - Middleware готов
- ✅ **XSS protection** - Django template escaping
- ✅ **SQL injection protection** - Django ORM

### Best Practices

- Используйте сильные пароли (Django validators)
- Включите HTTPS в production
- Настройте rate limiting
- Регулярно ротируйте JWT secrets
- Мониторьте failed login attempts

---

## Конфигурация

### Settings.py

```python

# JWT Configuration

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Email Configuration

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Celery Configuration

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```text
---

## Troubleshooting

### JWT токен не работает

```bash

# Проверить что пользователь активен

user = User.objects.get(email='user@example.com')
print(user.is_active)  # Should be True

# Проверить expiry токена

from ninja_jwt.tokens import RefreshToken
refresh = RefreshToken.for_user(user)
print(refresh.access_token)
```text
### Email не отправляются

```bash

# Проверить Celery worker запущен

celery -A pyland worker -l info

# Проверить email settings

python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```text
### Роли не создаются автоматически

```bash

# Запустить команду вручную

poetry run python manage.py create_roles

# Проверить что роли созданы

python manage.py shell
>>> from authentication.models import Role
>>> Role.objects.count()  # Should be 6
```text
---

## Changelog

### v2.0 (2025-12-01)

- ✅ Complete test coverage (90+ tests)
- ✅ Pydantic 2.x schemas
- ✅ Management commands
- ✅ Comprehensive documentation
- ✅ JWT authentication
- ✅ Email verification
- ✅ Password reset flow

### v1.0 (2024)

- Initial release
- Basic authentication
- Role system

---

## Контакты и поддержка

**Документация:**

- API Docs: <http://localhost:8000/api/docs>
- Tests: `authentication/tests/README.md`
- Templates: `authentication/templates/README.md`

**Команда:** Pyland Team
**Версия:** 2.0
**Статус:** ✅ Production Ready
