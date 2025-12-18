# GitHub Setup Instructions

## Шаги для публикации проекта

### 1. Создайте новый репозиторий на GitHub

Перейдите на https://github.com/new и создайте новый репозиторий:

- **Repository name:** `pyland-backend` (или любое другое название)
- **Description:** `Django 5.2 online school backend with multi-role system, CI/CD, and REST API`
- **Visibility:** Public или Private (на ваш выбор)
- **НЕ добавляйте:** README, .gitignore, license (уже есть в проекте)

### 2. Подключите локальный репозиторий к GitHub

После создания репозитория на GitHub выполните команды:

```bash
# Добавьте remote origin (замените YOUR_USERNAME на ваш username)
git remote add origin https://github.com/YOUR_USERNAME/pyland-backend.git

# Или если используете SSH:
# git remote add origin git@github.com:YOUR_USERNAME/pyland-backend.git

# Отправьте код на GitHub
git push -u origin main
```

### 3. Проверьте что CI запустился

После push перейдите на:
```
https://github.com/YOUR_USERNAME/pyland-backend/actions
```

Должны запуститься 2 workflow:
- ✅ **CI** - тесты, security checks, code quality
- ✅ **PR Checks** - запустится при создании Pull Request

### 4. Добавьте секреты для Codecov (опционально)

Если хотите загружать coverage на Codecov:

1. Зарегистрируйтесь на https://codecov.io
2. Подключите ваш репозиторий
3. Скопируйте Codecov token
4. Добавьте в GitHub: Settings → Secrets → New repository secret
   - Name: `CODECOV_TOKEN`
   - Value: ваш токен

### 5. Настройте branch protection (рекомендуется)

Settings → Branches → Add branch protection rule:
- Branch name pattern: `main`
- ✅ Require status checks to pass before merging
  - ✅ CI / test
  - ✅ CI / security
  - ✅ CI / code-quality
- ✅ Require branches to be up to date before merging

## Текущее состояние проекта

✅ Git репозиторий инициализирован  
✅ Все файлы добавлены в первый коммит  
✅ CI/CD workflows настроены  
✅ Black & isort форматирование применено  
✅ Dev dependencies установлены  
⏳ Ожидается push на GitHub

## Команда для быстрого старта

```bash
# 1. Создайте репозиторий на GitHub (см. шаг 1 выше)

# 2. Выполните (замените YOUR_USERNAME и REPO_NAME):
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main

# 3. Проверьте Actions:
# https://github.com/YOUR_USERNAME/REPO_NAME/actions
```

## После успешного push

CI автоматически:
- Запустит тесты с PostgreSQL 15 и Redis 7
- Проверит безопасность (safety, bandit)
- Проверит форматирование (black, isort)
- Загрузит coverage на Codecov (если настроен токен)

Для Pull Request дополнительно проверит:
- Миграции, шаблоны, переводы
- Сложность кода (radon)
