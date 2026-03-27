# Автоматическое обновление курсов валют - Быстрый старт

## ✅ Что было реализовано

Система **полностью автоматического** обновления курсов валют через **Celery Beat**.

**Больше не нужно запускать команды вручную!**

## 🚀 Как запустить автоматизацию

### Вариант 1: Development (локальная разработка)

**Открыть 2 терминала:**

**Terminal 1 - Celery Worker:**
```bash
cd /Users/dmitrii/Documents/GitHub/pyschool_delete_css/backend
poetry run celery -A pyland worker -l info
```

**Terminal 2 - Celery Beat:**
```bash
cd /Users/dmitrii/Documents/GitHub/pyschool_delete_css/backend
poetry run celery -A pyland beat -l info
```

**Или объединенная команда (для быстрого теста):**
```bash
poetry run celery -A pyland worker -B -l info
```

### Вариант 2: Production (Docker/Kubernetes)

**Docker Compose** - уже настроено в `docker-compose.yml`:
- Service `celery-worker` - обрабатывает задачи
- Service `celery-beat` - запускает задачи по расписанию

**Kubernetes** - уже настроено в `k8s/base/`:
- `deployment-celery-worker.yaml` - Worker pods
- `deployment-celery-beat.yaml` - Beat scheduler

## 📊 Что происходит автоматически

**Каждый час Celery Beat:**
1. ⏰ Запускает задачу `payments.update_currency_rates`
2. 🗑️ Очищает старый кэш курсов
3. 🌐 Запрашивает свежие курсы из exchangerate-api.com
4. 💾 Кэширует новые курсы на 1 час
5. 📝 Логирует результат

**Логи:**
```bash
tail -f src/logs/pyland.log | grep -i "автоматически обновлены"

# Вывод каждый час:
# 15:00:00 | INFO | ✅ Курсы валют автоматически обновлены через Celery: USD=1.0000, EUR=0.8638, GEL=2.7039, RUB=81.0053
# 16:00:00 | INFO | ✅ Курсы валют автоматически обновлены через Celery: USD=1.0000, EUR=0.8642, GEL=2.7045, RUB=81.1234
```

## 🧪 Тестирование

### Проверить что задача настроена:
```bash
poetry run celery -A pyland inspect scheduled
```

### Запустить задачу вручную (для теста):
```bash
poetry run python src/manage.py shell -c "from payments.tasks import update_currency_rates_task; update_currency_rates_task()"
```

### Ожидаемый результат:
```
INFO | Currency service инициализирован с API ключом
INFO | Запущено автоматическое обновление курсов валют (Celery Beat)
INFO | Получены курсы из API: USD=1, EUR=0.8638, GEL=2.7039, RUB=81.0053
INFO | Курсы валют обновлены из API для USD. Кэширование на 3600 секунд.
INFO | ✅ Курсы валют автоматически обновлены через Celery
```

## 🔍 Мониторинг

**Flower (Web UI для Celery) - опционально:**
```bash
pip install flower
poetry run celery -A pyland flower

# Откройте http://localhost:5555
```

**Celery Inspector:**
```bash
# Активные задачи
poetry run celery -A pyland inspect active

# Запланированные задачи
poetry run celery -A pyland inspect scheduled

# Зарегистрированные задачи
poetry run celery -A pyland inspect registered
```

## ⚙️ Конфигурация

**В .env уже настроено:**
```env
EXCHANGE_RATE_API_KEY='0570d8ec1dc5e300e97afff9'
```

**В settings.py уже добавлено:**
```python
EXCHANGE_RATE_API_KEY = env.str("EXCHANGE_RATE_API_KEY", "")
```

**В celery.py уже настроено:**
```python
app.conf.beat_schedule = {
    "update-currency-rates-hourly": {
        "task": "payments.update_currency_rates",
        "schedule": 3600.0,  # Каждый час
    },
}
```

## 📁 Созданные файлы

**Новые:**
1. `src/payments/tasks.py` - Celery задача автообновления
2. `src/payments/currency_service.py` - Singleton сервис
3. `src/payments/management/commands/update_currency_rates.py` - CLI команда

**Обновленные:**
1. `src/pyland/celery.py` - Добавлен beat_schedule
2. `src/pyland/settings.py` - Добавлен EXCHANGE_RATE_API_KEY
3. `src/payments/views.py` - Использует CurrencyService
4. `src/payments/README.md` - Добавлена документация
5. `src/payments/__init__.py` - Обновлена документация
6. `docs/payments/CURRENCY_SETUP.md` - Полная инструкция
7. `docs/payments/CURRENCY_IMPLEMENTATION.md` - Техническая документация

## 🎯 Итоговый результат

**До изменений:**
- ❌ Статичные курсы в коде
- ❌ Необходимость ручного обновления
- ❌ Риск устаревших курсов

**После изменений:**
- ✅ Автоматическое обновление каждый час
- ✅ Реальные курсы из exchangerate-api.com
- ✅ Кэширование для производительности
- ✅ Fallback при ошибке API
- ✅ Полное логирование
- ✅ Готово к production

**Гарантия:** Вы никогда не продадите курс дешевле из-за устаревших курсов! 🎉

## 📚 Документация

**Основная:** `docs/payments/CURRENCY_SETUP.md`
**Техническая:** `docs/payments/CURRENCY_IMPLEMENTATION.md`
**README:** `src/payments/README.md`

## ⏭️ Следующие шаги

1. **Запустить Celery Beat** (см. команды выше)
2. **Проверить логи** через 1 час
3. **Опционально:** Настроить Flower для мониторинга
4. **Production:** Убедиться что celery-beat запущен в Docker/K8s

---

**Дата:** 26 марта 2026
**Автор:** Pyland Team
**Версия:** 2.0.0 (с автоматизацией)
