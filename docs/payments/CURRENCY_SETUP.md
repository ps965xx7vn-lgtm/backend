# Dynamic Currency Rates Setup

## Overview

Система динамических курсов валют обеспечивает автоматическое обновление курсов каждый час, что гарантирует что курсы не будут продаваться дешевле из-за устаревших данных.

## Why Dynamic Rates?

**Проблема статичных курсов:**
- ❌ Курсы валют постоянно меняются
- ❌ Можно продать курс дешевле при изменении курса
- ❌ Необходимо вручную обновлять код при каждом изменении
- ❌ Риск финансовых потерь

**Решение с динамическими курсами:**
- ✅ Автоматическое обновление каждый час через Celery Beat
- ✅ Актуальные курсы из надежного источника (exchangerate-api.com)
- ✅ Кэширование для производительности (TTL = 1 час)
- ✅ Fallback на статичные курсы при ошибке API
- ✅ Гарантия корректных цен без ручного вмешательства
- ✅ Фоновая обработка без блокировки запросов

## Setup Instructions

### 1. Получить API ключ

**Вариант А: Бесплатный тариф (Рекомендуется для старта)**

1. Перейдите на https://www.exchangerate-api.com/
2. Нажмите "Get Free Key"
3. Зарегистрируйтесь (email + password)
4. Скопируйте ваш API ключ

**Лимиты бесплатного тарифа:**
- 1,500 запросов в месяц (≈50 запросов/день)
- При кэшировании на 1 час: 24 запроса/день = достаточно
- Поддержка всех валют
- HTTPS доступ
- Без кредитной карты

**Вариант Б: Платный тариф (Для production с высокой нагрузкой)**

- Professional: $12/месяц - 100,000 запросов
- Enterprise: Custom - неограниченные запросы

### 2. Настроить переменные окружения

#### Development (.env file):
```env
# Currency API (Optional - без него используются статичные курсы)
EXCHANGE_RATE_API_KEY=your_api_key_here

# Example:
# EXCHANGE_RATE_API_KEY=abc123def456ghi789jkl012mno345pq
```

#### Production (Environment Variables):
```bash
export EXCHANGE_RATE_API_KEY="your_production_api_key"
```

### 3. Проверить работу

```bash
# Показать текущие курсы
poetry run python src/manage.py update_currency_rates --show

# Принудительно обновить курсы
poetry run python src/manage.py update_currency_rates --force
```

**Ожидаемый вывод:**
```
============================================================
  CURRENCY RATES MANAGER - Менеджер курсов валют
============================================================

✅ Актуальные курсы валют (базовая валюта: USD):

   --------------------------------------------------
   | Валюта           | Курс к USD        | Символ |
   --------------------------------------------------
   | Доллар США       | 1.0000 (база)     | 💵     |
   | Евро             | 0.9234            | 💶     |
   | Российский рубль | 92.3450           | ₽      |
   | Грузинский лари  | 2.6789            | ₾      |
   --------------------------------------------------

📊 Примеры конвертации (100 USD):
   • 100 USD = 92.34 EUR
   • 100 USD = 9234.50 RUB
   • 100 USD = 267.89 GEL

============================================================
⏰ Время: 2026-03-26 14:30:45
💾 Курсы кэшируются на 1 час
============================================================
```

### 4. Проверить логи

```bash
# Смотреть логи
tail -f logs/pyland.log | grep -i currency

# Ожидаемые сообщения:
# INFO: CurrencyService singleton initialized
# INFO: Currency service инициализирован с API ключом
# INFO: Получены курсы из API: USD=1.00, EUR=0.93, RUB=92.34, GEL=2.68
# INFO: Курсы валют обновлены из API для USD. Кэширование на 3600 секунд.
```

### 5. Автоматическое обновление через Celery Beat

**Важно!** Курсы обновляются автоматически каждый час фоновой задачей Celery Beat. Вам **не нужно** запускать команду вручную.

#### Как это работает:

**1. Задача настроена в `src/pyland/celery.py`:**
```python
app.conf.beat_schedule = {
    "update-currency-rates-hourly": {
        "task": "payments.update_currency_rates",
        "schedule": 3600.0,  # Каждый час
    },
}
```

**2. Задача реализована в `src/payments/tasks.py`:**
```python
@shared_task(name="payments.update_currency_rates")
def update_currency_rates_task():
    """Автоматическое обновление курсов валют каждый час."""
    currency_service = get_currency_service()
    currency_service.invalidate_cache()  # Очистить старый кэш
    rates = currency_service.get_exchange_rates("USD")  # Получить свежие
    logger.info(f"✅ Курсы валют автоматически обновлены через Celery")
    return rates
```

**3. Запуск Celery Worker и Beat:**

```bash
# Terminal 1: Celery Worker (обрабатывает задачи)
poetry run celery -A pyland worker -l info

# Terminal 2: Celery Beat (планировщик задач)
poetry run celery -A pyland beat -l info

# Или объединенная команда (НЕ для production):
poetry run celery -A pyland worker -B -l info
```

**4. Проверка автоматического обновления в логах:**

```bash
tail -f src/logs/pyland.log | grep -i "автоматически обновлены"

# Ожидаемый вывод каждый час:
# 2026-03-26 15:00:00 | INFO | tasks.py:54 | ✅ Курсы валют автоматически обновлены через Celery: USD=1.0000, EUR=0.8638, GEL=2.7039, RUB=81.0053
# 2026-03-26 16:00:00 | INFO | tasks.py:54 | ✅ Курсы валют автоматически обновлены через Celery: USD=1.0000, EUR=0.8642, GEL=2.7045, RUB=81.1234
```

#### Production Deployment:

**Docker Compose (рекомендуется):**
```yaml
services:
  celery-worker:
    image: pyland:latest
    command: celery -A pyland worker -l info
    environment:
      - EXCHANGE_RATE_API_KEY=${EXCHANGE_RATE_API_KEY}
    depends_on:
      - redis

  celery-beat:
    image: pyland:latest
    command: celery -A pyland beat -l info
    environment:
      - EXCHANGE_RATE_API_KEY=${EXCHANGE_RATE_API_KEY}
    depends_on:
      - redis
```

**Kubernetes (see k8s/base/):**
- `deployment-celery-worker.yaml` - Worker pods
- `deployment-celery-beat.yaml` - Beat scheduler (только 1 реплика!)

#### Мониторинг:

```bash
# Проверить статус задач
poetry run celery -A pyland inspect scheduled

# Проверить активные задачи
poetry run celery -A pyland inspect active

# История выполненных задач
poetry run celery -A pyland events

# Flower (Web UI для Celery) - опционально
pip install flower
poetry run celery -A pyland flower
# Откройте http://localhost:5555
```

#### Troubleshooting:

**Проблема:** Задача не запускается автоматически
```bash
# 1. Убедитесь что Celery Beat запущен
ps aux | grep "celery.*beat"

# 2. Проверьте расписание
poetry run celery -A pyland inspect scheduled

# 3. Проверьте логи Beat
tail -f src/logs/pyland.log | grep -i beat
```

**Проблема:** Курсы не обновляются
```bash
# 1. Проверьте что API ключ установлен
poetry run python src/manage.py shell -c "from django.conf import settings; print(f'API Key: {settings.EXCHANGE_RATE_API_KEY[:10]}...')"

# 2. Проверьте подключение к Redis
redis-cli ping  # Должен вернуть "PONG"

# 3. Вручную запустите задачу для теста
poetry run python src/manage.py shell -c "from payments.tasks import update_currency_rates_task; update_currency_rates_task()"
```

## Architecture

### Components

```
payments/
├── currency_service.py     # Singleton service для получения курсов
├── views.py                # Использует CurrencyService
├── management/
│   └── commands/
│       └── update_currency_rates.py  # Management command
└── README.md               # Документация
```

### Flow Diagram

```
User Request → checkout_view()
                    ↓
         convert_currency(100, "USD", "EUR")
                    ↓
         get_currency_service() [Singleton]
                    ↓
         get_exchange_rates("USD")
                    ↓
              Check Cache
                 ↙      ↘
            Found      Not Found
              ↓            ↓
         Return     Fetch from API
                         ↓
                   Cache (1 hour)
                         ↓
                      Return
```

### Caching Strategy

**Cache Key Format:**
```python
f"currency_rates:{base_currency}"
# Example: "currency_rates:USD"
```

**Cache TTL:** 1 час (3600 секунд)

**Cache Storage:**
- Development: Dummy cache (no actual caching)
- Production: Redis (persistent)

### Fallback Mechanism

**Приоритет источников данных:**
1. **Redis Cache** (если доступен и не устарел)
2. **exchangerate-api.com** (если API ключ настроен)
3. **Static Fallback Rates** (hardcoded в currency_service.py)

**Fallback курсы (обновлены 26.03.2026):**
```python
FALLBACK_RATES = {
    "USD": Decimal("1.00"),
    "EUR": Decimal("0.93"),
    "RUB": Decimal("90.00"),
    "GEL": Decimal("2.65"),
}
```

## Testing

### Unit Tests

```python
# tests/test_currency_service.py
def test_currency_service_singleton():
    """Проверка singleton pattern."""
    service1 = get_currency_service()
    service2 = get_currency_service()
    assert service1 is service2

def test_get_exchange_rates():
    """Проверка получения курсов."""
    service = get_currency_service()
    rates = service.get_exchange_rates()

    assert "USD" in rates
    assert "EUR" in rates
    assert "RUB" in rates
    assert "GEL" in rates
    assert rates["USD"] == Decimal("1.00")

def test_convert_currency():
    """Проверка конвертации валют."""
    service = get_currency_service()
    result = service.convert_currency(
        Decimal("100.00"), "USD", "EUR"
    )

    assert result > Decimal("0")
    assert result < Decimal("100.00")  # EUR дороже USD
```

### Manual Testing

```bash
# 1. Без API ключа (должны использоваться fallback курсы)
unset EXCHANGE_RATE_API_KEY
poetry run python src/manage.py update_currency_rates --show
# Expected: WARNING "EXCHANGE_RATE_API_KEY не установлен"

# 2. С API ключом (должны загружаться актуальные курсы)
export EXCHANGE_RATE_API_KEY="your_key"
poetry run python src/manage.py update_currency_rates --force
# Expected: SUCCESS "Получены курсы из API"

# 3. Проверка кэширования
poetry run python src/manage.py update_currency_rates --show  # Первый раз
poetry run python src/manage.py update_currency_rates --show  # Второй раз (из кэша)
# Expected: "Курсы валют получены из кэша"
```

## Production Deployment

### 1. Environment Variables

```bash
# Kubernetes Secret
apiVersion: v1
kind: Secret
metadata:
  name: pyland-secrets
type: Opaque
stringData:
  EXCHANGE_RATE_API_KEY: "your_production_key"
```

### 2. Cron Job (Optional)

Хотя курсы обновляются автоматически при каждом запросе, можно настроить cron для превентивного обновления:

```yaml
# k8s/cronjob-currency-update.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: currency-rates-update
spec:
  schedule: "0 * * * *"  # Каждый час
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: update-currency
            image: pyland:latest
            command:
            - python
            - manage.py
            - update_currency_rates
            - --force
          restartPolicy: OnFailure
```

### 3. Monitoring

**Metrics to Monitor:**
- API request success rate
- Cache hit/miss ratio
- Average conversion time
- Fallback usage frequency

**Alerts Setup:**
```python
# Example with Sentry
if not self.use_api:
    sentry_sdk.capture_message(
        "Currency API key missing - using fallback rates",
        level="warning"
    )
```

## Troubleshooting

### Issue: "EXCHANGE_RATE_API_KEY не установлен"

**Причина:** Отсутствует API ключ в environment variables

**Решение:**
1. Получить API ключ с https://www.exchangerate-api.com/
2. Добавить в `.env` файл: `EXCHANGE_RATE_API_KEY=your_key`
3. Перезапустить приложение

### Issue: "API вернул ошибку: invalid_key"

**Причина:** Неверный или устаревший API ключ

**Решение:**
1. Проверить корректность ключа
2. Сгенерировать новый ключ на сайте
3. Обновить `.env` файл

### Issue: "Ошибка HTTP запроса: Connection timeout"

**Причина:** Проблемы с сетью или недоступность API

**Решение:**
1. Автоматически используются fallback курсы
2. Проверить интернет соединение
3. Проверить firewall rules
4. API автоматически восстановится при следующем запросе

### Issue: Курсы не обновляются

**Причина:** Кэш не истек (TTL = 1 час)

**Решение:**
```bash
# Принудительно очистить кэш и обновить
poetry run python src/manage.py update_currency_rates --force
```

## API Documentation

### exchangerate-api.com

**Endpoint:**
```
GET https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}
```

**Response Example:**
```json
{
  "result": "success",
  "base_code": "USD",
  "conversion_rates": {
    "USD": 1.0000,
    "EUR": 0.9234,
    "RUB": 92.3450,
    "GEL": 2.6789,
    ...
  },
  "time_last_update_unix": 1711440001,
  "time_next_update_unix": 1711526401
}
```

**Rate Limits:**
- Free: 1,500 requests/month
- Professional: 100,000 requests/month
- Enterprise: Unlimited

**Error Codes:**
- `invalid_key` - Неверный API ключ
- `inactive_account` - Неактивный аккаунт
- `quota_reached` - Превышен лимит запросов
- `unsupported_code` - Неподдерживаемая валюта

## Best Practices

1. **Always Set API Key in Production**
   ```bash
   # Never use fallback rates in production
   export EXCHANGE_RATE_API_KEY="your_key"
   ```

2. **Monitor API Usage**
   - Track request count
   - Set up alerts for quota limits
   - Plan upgrade if needed

3. **Test Fallback Mechanism**
   ```python
   # Периодически тестировать без API ключа
   def test_fallback_rates():
       service = CurrencyService()
       service.api_key = None
       rates = service.get_exchange_rates()
       assert rates == FALLBACK_RATES
   ```

4. **Log All Currency Operations**
   - Enable DEBUG logging for currency operations
   - Monitor for anomalies in conversion rates
   - Track cache performance

5. **Update Fallback Rates Quarterly**
   ```python
   # Обновить FALLBACK_RATES в currency_service.py
   # Каждые 3 месяца или при значительном изменении курсов
   ```

## FAQ

**Q: Нужно ли платить за API?**
A: Нет для начала. Бесплатный тариф (1500 req/месяц) достаточен при кэшировании на 1 час.

**Q: Что если API недоступен?**
A: Автоматически используются fallback статичные курсы (обновлены 26.03.2026).

**Q: Как часто обновляются курсы?**
A: Автоматически каждый час через кэш TTL. Можно форсировать: `--force`.

**Q: Можно ли использовать другой API?**
A: Да, нужно изменить `_fetch_from_api()` метод в `currency_service.py`.

**Q: Безопасно ли хранить API ключ в .env?**
A: Да, но добавьте `.env` в `.gitignore`. В production используйте Kubernetes Secrets.

**Q: Как проверить сколько запросов осталось?**
A: Зайдите в dashboard на https://www.exchangerate-api.com/ → Usage Statistics

## Support

**Issues:** Create ticket in GitHub Issues
**Docs:** `/docs/payments/CURRENCY_SETUP.md`
**API Docs:** https://www.exchangerate-api.com/docs

---

**Last Updated:** 26 March 2026
**Author:** Pyland Team
