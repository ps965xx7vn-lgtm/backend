# Manager Dashboard - Документация

## Обзор

Manager Dashboard - полнофункциональная административная панель для
управления платформой Pyland.

## Доступ

**URL:** `<http://localhost:8000/ru/managers/`> (или `/en/managers/` для
английской версии)

**Требования:** Требуются права администратора (`is_staff=True`)

## Функциональность

### 1. Dashboard (Главная страница)

- **URL:** `/managers/`
- **Статистика:**
  - Обратная связь (всего, необработанных, за сегодня)
  - Пользователи (всего, активных, новых за неделю, staff)
  - Контент (статьи, курсы, комментарии)
  - Настройки системы
- **Последние данные:**
  - 5 последних обращений
  - 10 последних системных логов
- **Быстрые действия:** Ссылки на все разделы

### 2. Обратная связь

- **URL:** `/managers/feedback/`
- **Возможности:**
  - Список всех обращений с пагинацией (25 на страницу)
  - Фильтрация:
    - Поиск по имени, email, телефону, сообщению
    - Дата от/до
    - Статус обработки
  - Просмотр деталей обращения
  - Отметка как обработанное/необработанное
  - Добавление заметок администратора
  - Удаление обращений (с подтверждением)

### 3. Системные логи

- **URL:** `/managers/logs/`
- **Возможности:**
  - Просмотр всех системных событий
  - Фильтрация по:
    - Уровню (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Типу действия (LOGIN, LOGOUT, CREATE, UPDATE, DELETE и т.д.)
    - Пользователю
    - Дате
    - Поисковому запросу
  - Пагинация (50 на страницу)
  - Просмотр деталей лога (JSON details)

### 4. Настройки системы

- **URL:** `/managers/settings/`
- **Возможности:**
  - Просмотр всех настроек
  - Редактирование значений
  - Группировка по категориям
  - Типы значений:
    - String (текст)
    - Integer (число)
    - Boolean (true/false)
    - JSON (JSON объект)
  - Статус публичности (публичная/приватная)
  - История изменений (кто и когда обновил)

## Структура файлов

```text
managers/
├── __init__.py              # Докстринг модуля
├── apps.py                  # Конфигурация приложения
├── models.py                # Модели (Feedback, SystemLog, SystemSettings)
├── views.py                 # Django views для dashboard
├── urls.py                  # URL маршруты
├── admin.py                 # Django admin конфигурация
├── api.py                   # REST API endpoints (Ninja)
├── schemas.py               # Pydantic схемы для API
├── forms.py                 # Django формы
├── middleware.py            # Rate limiting и security headers
├── cache_utils.py           # Утилиты кеширования
└── templates/
    └── managers/
        ├── base.html                     # Базовый шаблон
        ├── dashboard.html                # Главная страница
        ├── feedback_list.html            # Список обращений
        ├── feedback_detail.html          # Детали обращения
        ├── feedback_confirm_delete.html  # Подтверждение удаления
        ├── system_logs.html              # Системные логи
        └── system_settings.html          # Настройки системы
```text
## Особенности

### Безопасность

- ✅ Все views защищены `@staff_member_required`
- ✅ Rate limiting через middleware (50/200 req/час)
- ✅ Security headers (X-Frame-Options: DENY, X-XSS-Protection и т.д.)
- ✅ CSRF защита на всех формах

### Производительность

- ✅ Кеширование статистики (Redis, TTL 5-10 минут)
- ✅ ORM оптимизации (select_related, prefetch_related)
- ✅ Пагинация для больших списков
- ✅ Lazy loading деталей логов

### UX/UI

- ✅ Responsive дизайн (Bootstrap 5)
- ✅ Font Awesome иконки
- ✅ Цветные бейджи для статусов
- ✅ Breadcrumbs навигация
- ✅ Фильтрация и поиск
- ✅ Сообщения об успехе/ошибке (Django messages)

## Докстринги

Все файлы имеют **русские докстринги** в стиле Poetry:

- Модуль-уровень докстринги
- Класс-уровень докстринги
- Функция-уровень докстринги с Args, Returns, Examples

## API

REST API доступен через `/api/managers/`:

- `GET /api/managers/feedback/` - Список обращений
- `GET /api/managers/feedback/{id}/` - Детали обращения
- `DELETE /api/managers/feedback/{id}/` - Удаление
- `GET /api/managers/feedback/stats/` - Статистика

**Документация:** `/api/docs` (требуется staff login)

## Использование

### 1. Запуск сервера

```bash
cd src/
poetry run python manage.py runserver
```text
### 2. Создание суперпользователя (если нет)

```bash
poetry run python manage.py createsuperuser
```text
### 3. Открыть dashboard

```text
<http://localhost:8000/ru/managers/>
```text
### 4. Логин

Используйте учетные данные суперпользователя или пользователя с `is_staff=True`.

## Интеграция

### В pyland/urls.py

```python
urlpatterns += i18n_patterns(
    ...
    path("managers/", include("manager.urls")),  # ✅ Добавлено
    ...
)
```text
### В settings.py MIDDLEWARE

```python
MIDDLEWARE = [
    ...
    'manager.middleware.ManagerRateLimitMiddleware',        # ✅ Добавлено
    'manager.middleware.ManagerSecurityHeadersMiddleware',  # ✅ Добавлено
]
```text
### В pyland/api.py

```python
from manager.api import router as manager_router
api.add_router("/managers/", manager_router)  # ✅ Добавлено
```text
## Логирование

Все административные действия логируются в `SystemLog`:

- Обработка feedback
- Изменение настроек
- Удаление записей
- И другие критичные операции

## Тестирование

```bash

# Проверка работоспособности

poetry run python manage.py check

# Миграции

poetry run python manage.py migrate

# Тесты (если есть)

poetry run pytest managers/tests/
```text
## Дальнейшее развитие

Возможные улучшения:

1. Экспорт данных (CSV, Excel)
2. Графики и диаграммы статистики
3. Email уведомления при новых обращениях
4. Массовые действия в списках
5. Расширенная фильтрация логов
6. Backup/restore настроек
7. Audit trail для всех изменений

## Поддержка

При возникновении проблем проверьте:

1. Права пользователя (`is_staff=True`)
2. Redis работает (для кеширования)
3. Миграции применены
4. Middleware добавлены в settings.py
5. URLs подключены в pyland/urls.py

---

**Автор:** Pyland Team
**Дата:** 2025
**Версия:** 1.0.0
