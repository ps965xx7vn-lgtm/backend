# OAuth Authentication Setup

Настройка социальной авторизации через GitHub и Google для pylandschool.com

## Содержание

- [GitHub OAuth](#github-oauth)
- [Google OAuth2](#google-oauth2)
- [Переменные окружения](#переменные-окружения)
- [Проверка работы](#проверка-работы)
- [Troubleshooting](#troubleshooting)

---

## GitHub OAuth

### 1. Регистрация GitHub OAuth App

1. Перейдите на [GitHub Developer Settings](https://github.com/settings/developers)
2. Нажмите **"New OAuth App"**
3. Заполните форму:

```
Application name: PyLand School
Homepage URL: https://pylandschool.com
Authorization callback URL: https://pylandschool.com/social-auth/complete/github/
```

### 2. Дополнительные настройки

**Application description** (опционально):
```
Online programming school for Python, Docker, Git and more
```

**Application logo** (рекомендуется):
- Загрузите логотип PyLand (минимум 200x200px)

### 3. Получите credentials

После создания приложения вы получите:
- **Client ID** - публичный идентификатор приложения
- **Client Secret** - секретный ключ (нажмите "Generate a new client secret")

⚠️ **Важно**: Сохраните Client Secret сразу - он больше не будет показан!

### 4. Добавьте в .env

```bash
SOCIAL_AUTH_GITHUB_KEY=your_github_client_id
SOCIAL_AUTH_GITHUB_SECRET=your_github_client_secret
```

---

## Google OAuth2

### 1. Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Нажмите **"Select a project"** → **"New Project"**
3. Введите:
   - **Project name**: PyLand School
   - **Organization**: (оставьте пустым или выберите)
4. Нажмите **"Create"**

### 2. Настройка OAuth consent screen

1. В меню перейдите: **APIs & Services** → **OAuth consent screen**
2. Выберите **"External"** (для публичного доступа)
3. Заполните форму:

```
App name: PyLand School
User support email: support@pylandschool.com
Developer contact information: dev@pylandschool.com
Application home page: https://pylandschool.com
Application privacy policy: https://pylandschool.com/privacy-policy/
Application terms of service: https://pylandschool.com/terms-of-service/
```

4. **Scopes**: Добавьте следующие scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`

5. **Test users** (опционально для тестирования):
   - Добавьте email'ы для тестирования до публикации

### 3. Создание OAuth 2.0 Client ID

1. Перейдите: **APIs & Services** → **Credentials**
2. Нажмите **"Create Credentials"** → **"OAuth client ID"**
3. Выберите:
   - **Application type**: Web application
   - **Name**: PyLand School Web Client
4. **Authorized JavaScript origins**:
```
https://pylandschool.com
https://www.pylandschool.com
```
5. **Authorized redirect URIs**:
```
https://pylandschool.com/social-auth/complete/google-oauth2/
https://www.pylandschool.com/social-auth/complete/google-oauth2/
```

### 4. Получите credentials

После создания скачайте JSON или скопируйте:
- **Client ID** (заканчивается на `.apps.googleusercontent.com`)
- **Client Secret**

### 5. Добавьте в .env

```bash
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=123456789.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_client_secret
```

### 6. Публикация приложения (Production)

Для снятия ограничений:
1. Вернитесь в **OAuth consent screen**
2. Нажмите **"Publish App"**
3. Подтвердите публикацию

⚠️ **Примечание**: До публикации приложение будет в "Testing" режиме с ограничением 100 пользователей.

---

## Переменные окружения

### Production (.env)

```bash
# Site Configuration
SITE_URL=https://pylandschool.com
ALLOWED_HOSTS=pylandschool.com,www.pylandschool.com
CSRF_TRUSTED_ORIGINS=https://pylandschool.com,https://www.pylandschool.com

# Social Auth - GitHub
SOCIAL_AUTH_GITHUB_KEY=your_real_github_client_id
SOCIAL_AUTH_GITHUB_SECRET=your_real_github_client_secret

# Social Auth - Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=123456789-abcdefg.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_real_google_client_secret
```

### Development (local .env)

```bash
# Site Configuration
SITE_URL=http://127.0.0.1:8000
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Social Auth - GitHub (Development App)
SOCIAL_AUTH_GITHUB_KEY=dev_github_client_id
SOCIAL_AUTH_GITHUB_SECRET=dev_github_client_secret

# Social Auth - Google (Development)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=dev-123.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=dev_google_secret
```

**Для разработки создайте отдельные OAuth приложения** с callback URLs:
- GitHub: `http://127.0.0.1:8000/social-auth/complete/github/`
- Google: `http://127.0.0.1:8000/social-auth/complete/google-oauth2/`

---

## Проверка работы

### 1. Запустите сервер

```bash
poetry run python src/manage.py runserver
```

### 2. Проверьте URL'ы

Откройте в браузере (для локальной разработки):
- **GitHub login**: http://127.0.0.1:8000/social-auth/login/github/
- **Google login**: http://127.0.0.1:8000/social-auth/login/google-oauth2/

### 3. Тестирование процесса

1. Кликните на кнопку "Войти через GitHub/Google"
2. Вы будете перенаправлены на страницу авторизации GitHub/Google
3. Разрешите доступ к вашему профилю
4. Вас перенаправит обратно на сайт
5. Проверьте, что пользователь создан в Django Admin

### 4. Проверка в Django Admin

```bash
poetry run python src/manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Проверить пользователей созданных через OAuth
User.objects.filter(social_auth__isnull=False)

# Проверить связи с соцсетями
from social_django.models import UserSocialAuth
UserSocialAuth.objects.all()
```

---

## Troubleshooting

### Ошибка: "Redirect URI mismatch"

**Причина**: URL в настройках OAuth не совпадает с фактическим

**Решение**:
1. Проверьте `SITE_URL` в `.env`
2. Убедитесь что в GitHub/Google указан правильный callback URL
3. Для HTTPS проверьте что используется `https://` а не `http://`

### Ошибка: "Application does not exist"

**Причина**: Неверные Client ID или Secret

**Решение**:
1. Проверьте переменные окружения `SOCIAL_AUTH_GITHUB_KEY` и `SOCIAL_AUTH_GITHUB_SECRET`
2. Убедитесь что нет лишних пробелов в `.env` файле
3. Перезапустите сервер после изменения `.env`

### Пользователь создается но не авторизуется

**Причина**: Проблемы с session или middleware

**Решение**:
1. Проверьте что `social_django` в `INSTALLED_APPS`
2. Проверьте `AUTHENTICATION_BACKENDS` в settings.py
3. Очистите кеш браузера и cookies
4. Проверьте Django sessions в базе данных:
```python
from django.contrib.sessions.models import Session
Session.objects.all().count()
```

### Google OAuth: "Access blocked: This app's request is invalid"

**Причина**: Приложение в "Testing" режиме или не опубликовано

**Решение**:
1. Добавьте тестового пользователя в Google Console
2. Опубликуйте приложение (кнопка "Publish App")
3. Дождитесь верификации от Google (может занять несколько дней)

### GitHub OAuth: "The redirect_uri MUST match the registered callback URL"

**Причина**: Несоответствие протокола (http vs https) или домена

**Решение**:
1. Для production используйте ТОЛЬКО `https://pylandschool.com`
2. Для development создайте отдельное OAuth приложение с `http://127.0.0.1:8000`
3. Не используйте `localhost` и `127.0.0.1` одновременно - выберите один вариант

---

## Безопасность

### Best Practices

1. **Никогда не коммитьте** `.env` файл с реальными credentials
2. **Используйте разные credentials** для dev/staging/production
3. **Ротируйте secrets** регулярно (каждые 6 месяцев)
4. **Ограничьте доступ** к `.env` файлам на сервере (chmod 600)
5. **Используйте secrets management** (AWS Secrets Manager, HashiCorp Vault) для production

### GitHub Security

- Включите **Two-factor authentication** для GitHub аккаунта с OAuth приложениями
- Регулярно проверяйте **"Security log"** в настройках OAuth приложения
- Используйте **IP whitelist** если возможно

### Google Security

- Включите **2FA** для Google аккаунта
- Настройте **Security alerts** в Google Cloud Console
- Регулярно проверяйте **OAuth consent screen** → **Usage**
- Включите **Advanced Protection** для критичных аккаунтов

---

## Дополнительные ресурсы

- [Django Social Auth Documentation](https://python-social-auth.readthedocs.io/)
- [GitHub OAuth Apps](https://docs.github.com/en/apps/oauth-apps)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Django Authentication](https://docs.djangoproject.com/en/5.0/topics/auth/)

---

**Версия:** 1.0.0
**Обновлено:** 5 марта 2026
**Авторы:** PyLand Development Team
