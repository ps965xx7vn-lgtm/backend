# Dynamic Currency Rates - Implementation Summary

## Краткое описание изменений

Добавлена система **динамического обновления курсов валют** для гарантии актуальных цен при продаже курсов в разных валютах.

## Проблема

До изменений:
- ❌ Статичные курсы валют в коде (hardcoded)
- ❌ Риск продажи курсов дешевле при изменении курсов
- ❌ Необходимость ручного обновления кода
- ❌ Отсутствие guarantee актуальных цен

## Решение

После изменений:
- ✅ Автоматическое обновление курсов каждый час
- ✅ Интеграция с exchangerate-api.com
- ✅ Кэширование в Redis (TTL = 1 час)
- ✅ Fallback на статичные курсы при ошибке
- ✅ Thread-safe singleton pattern
- ✅ Management command для ручного управления

## Архитектура

### Новые компоненты

```
src/payments/
├── currency_service.py                          # NEW: Singleton service
├── management/                                   # NEW: Management commands
│   └── commands/
│       └── update_currency_rates.py             # NEW: CLI команда
├── views.py                                     # MODIFIED: Использует currency_service
├── apps.py                                      # MODIFIED: Обновлен docstring
├── __init__.py                                  # MODIFIED: Обновлена документация
└── README.md                                    # MODIFIED: Добавлен раздел о курсах

docs/payments/
└── CURRENCY_SETUP.md                            # NEW: Полная документация

.env.example                                      # MODIFIED: Добавлена EXCHANGE_RATE_API_KEY
```

### Класс CurrencyService

**Location:** `src/payments/currency_service.py`

**Основные методы:**
```python
class CurrencyService:
    def get_exchange_rates(base_currency: str = "USD") -> dict[str, Decimal]
    def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal
    def invalidate_cache() -> None
    def _fetch_from_api(base_currency: str) -> dict[str, Decimal]
    def _get_fallback_rates() -> dict[str, Decimal]
```

**Особенности:**
- Singleton pattern (thread-safe double-checked locking)
- Автоматическое кэширование на 1 час
- Graceful degradation (fallback на статичные курсы)
- Comprehensive logging

### Изменения в views.py

**До:**
```python
EXCHANGE_RATES: dict[str, Decimal] = {
    "USD": Decimal("1.00"),
    "EUR": Decimal("0.93"),
    "RUB": Decimal("90.00"),
    "GEL": Decimal("2.65"),
}

def convert_currency(amount, from_currency, to_currency):
    usd_amount = amount / EXCHANGE_RATES[from_currency]
    result = usd_amount * EXCHANGE_RATES[to_currency]
    return result.quantize(Decimal("0.01"))
```

**После:**
```python
from .currency_service import get_currency_service

def convert_currency(amount, from_currency, to_currency):
    currency_service = get_currency_service()
    return currency_service.convert_currency(amount, from_currency, to_currency)
```

### Management Command

**Usage:**
```bash
# Показать текущие курсы
poetry run python src/manage.py update_currency_rates --show

# Принудительно обновить курсы (очистить кэш)
poetry run python src/manage.py update_currency_rates --force
```

**Output Example:**
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
```

### Автоматическое обновление (Celery Beat)

**Важно!** Курсы обновляются **полностью автоматически** каждый час через Celery Beat. Вам **не нужно** запускать команду вручную.

#### Новый файл: `src/payments/tasks.py`

**Celery задача для автоматического обновления:**
```python
@shared_task(name="payments.update_currency_rates")
def update_currency_rates_task():
    """
    Периодическая задача для автоматического обновления курсов валют.

    Запускается каждый час через Celery Beat для гарантии актуальных курсов.
    При ошибке API автоматически использует fallback курсы.
    """
    try:
        currency_service = get_currency_service()
        currency_service.invalidate_cache()  # Очистить старый кэш
        rates = currency_service.get_exchange_rates("USD")  # Получить свежие

        logger.info(f"✅ Курсы валют автоматически обновлены через Celery")
        return f"Currency rates updated: {rates}"

    except Exception as e:
        logger.error(f"Ошибка при автоматическом обновлении курсов: {e}")
        return f"Error: {str(e)}"
```

#### Изменения в `src/pyland/celery.py`

**Добавлено в beat_schedule:**
```python
app.conf.beat_schedule = {
    # ... существующие задачи ...

    "update-currency-rates-hourly": {
        "task": "payments.update_currency_rates",
        "schedule": 3600.0,  # 1 час - гарантия актуальных курсов для платежей
    },
}
```

#### Запуск Celery

**Development:**
```bash
# Terminal 1: Worker (обрабатывает задачи)
poetry run celery -A pyland worker -l info

# Terminal 2: Beat (планировщик задач)
poetry run celery -A pyland beat -l info

# Или объединенная команда (НЕ для production):
poetry run celery -A pyland worker -B -l info
```

**Production (Docker Compose):**
```yaml
services:
  celery-worker:
    image: pyland:latest
    command: celery -A pyland worker -l info
    environment:
      - EXCHANGE_RATE_API_KEY=${EXCHANGE_RATE_API_KEY}

  celery-beat:
    image: pyland:latest
    command: celery -A pyland beat -l info
    environment:
      - EXCHANGE_RATE_API_KEY=${EXCHANGE_RATE_API_KEY}
```

**Production (Kubernetes):**
- `k8s/base/deployment-celery-worker.yaml` - Worker pods (можно scale)
- `k8s/base/deployment-celery-beat.yaml` - Beat scheduler (**только 1 реплика!**)

#### Проверка автоматического обновления

**Логи:**
```bash
tail -f src/logs/pyland.log | grep -i "автоматически обновлены"

# Ожидаемый вывод каждый час:
# 2026-03-26 15:00:00 | INFO | tasks.py:54 | ✅ Курсы валют автоматически обновлены через Celery: USD=1.0000, EUR=0.8638, GEL=2.7039, RUB=81.0053
# 2026-03-26 16:00:00 | INFO | tasks.py:54 | ✅ Курсы валют автоматически обновлены через Celery: USD=1.0000, EUR=0.8642, GEL=2.7045, RUB=81.1234
```

**Мониторинг:**
```bash
# Проверить статус задач
poetry run celery -A pyland inspect scheduled

# Проверить активные задачи
poetry run celery -A pyland inspect active

# Flower (Web UI для Celery) - опционально
pip install flower
poetry run celery -A pyland flower
# Открыть http://localhost:5555
```

## Конфигурация

### Environment Variables

**Новая переменная:**
```env
EXCHANGE_RATE_API_KEY=your_api_key_here
```

**Получение API ключа:**
1. Зарегистрироваться на https://www.exchangerate-api.com/
2. Получить бесплатный ключ (1500 запросов/месяц)
3. Добавить в `.env` файл

**Без API ключа:**
- ⚠️ Система будет использовать fallback статичные курсы
- Логируется WARNING: "EXCHANGE_RATE_API_KEY не установлен"

### Кэширование

**Cache Key Format:**
```python
f"currency_rates:{base_currency}"
# Example: "currency_rates:USD"
```

**Cache Settings:**
- TTL: 3600 секунд (1 час)
- Backend: Redis (production) или Dummy Cache (development)
- Automatic invalidation: каждый час

## Workflow

### Currency Update Flow

```
API Request → get_currency_service() [Singleton]
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
                   On Error
                         ↓
                 Fallback Rates
                         ↓
                      Return
```

### Payment Flow with Currency Conversion

```
User → Checkout Page
         ↓
   Select Currency (EUR)
         ↓
   Course Price (100 USD)
         ↓
   convert_currency(100, "USD", "EUR")
         ↓
   CurrencyService.get_exchange_rates()
         ↓
   Returns: 93.00 EUR
         ↓
   Display Price: €93.00
         ↓
   Create Payment with EUR
```

## Тестирование

### Unit Tests (TODO)

**Файл:** `src/payments/tests/test_currency_service.py`

```python
def test_currency_service_singleton()
def test_get_exchange_rates_with_api()
def test_get_exchange_rates_without_api()
def test_convert_currency()
def test_cache_invalidation()
def test_fallback_rates()
def test_api_error_handling()
```

### Manual Testing

```bash
# 1. Без API ключа (fallback курсы)
unset EXCHANGE_RATE_API_KEY
poetry run python src/manage.py update_currency_rates --show

# 2. С API ключом (реальные курсы)
export EXCHANGE_RATE_API_KEY="your_key"
poetry run python src/manage.py update_currency_rates --force

# 3. Проверка кэширования
poetry run python src/manage.py update_currency_rates --show  # Из API
poetry run python src/manage.py update_currency_rates --show  # Из кэша (быстрее)
```

## Deployment

### Development

```bash
# .env файл
EXCHANGE_RATE_API_KEY=your_sandbox_key

# Запустить приложение
poetry run python src/manage.py runserver
```

### Production

**Kubernetes Secret:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pyland-secrets
type: Opaque
stringData:
  EXCHANGE_RATE_API_KEY: "your_production_key"
```

**Optional: Cron Job для предварительного обновления:**
```yaml
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
            command: ["python", "manage.py", "update_currency_rates", "--force"]
```

## Мониторинг

### Логи

**Success:**
```
INFO: Currency service инициализирован с API ключом
INFO: Получены курсы из API: USD=1.00, EUR=0.93, RUB=92.34, GEL=2.68
INFO: Курсы валют обновлены из API для USD. Кэширование на 3600 секунд.
```

**Warnings:**
```
WARNING: EXCHANGE_RATE_API_KEY не установлен в settings.
WARNING: Используются fallback курсы валют (могут быть устаревшими)
```

**Errors:**
```
ERROR: Ошибка при получении курсов из API: Connection timeout
ERROR: Ошибка парсинга ответа API: Invalid JSON
```

### Metrics (TODO)

- API request success rate
- Cache hit/miss ratio
- Average response time
- Fallback usage frequency

## Миграция

### Для существующих инсталляций

1. **Backup текущих данных**
2. **Pull новый код:**
   ```bash
   git pull origin main
   ```

3. **Установить зависимости:**
   ```bash
   poetry install  # requests уже в зависимостях
   ```

4. **Добавить API ключ в .env:**
   ```env
   EXCHANGE_RATE_API_KEY=your_key
   ```

5. **Проверить работу:**
   ```bash
   python manage.py update_currency_rates --show
   ```

6. **Перезапустить приложение**

### Backward Compatibility

✅ **Полная обратная совместимость:**
- Если API ключ не установлен → используются статичные курсы (как раньше)
- Все существующие платежи работают без изменений
- API эндпоинты не изменились
- Database schema не изменилась

## Performance Impact

### Без кэширования (первый запрос):
- API request: ~200-500ms
- Parse JSON: ~10ms
- Store in cache: ~5ms
- **Total:** ~250-550ms

### С кэшированием (последующие запросы):
- Cache lookup: ~1-5ms
- **Total:** ~1-5ms

**Improvement:** 50-500x быстрее с кэшем

## Cost Analysis

### Бесплатный тариф
- 1500 requests / месяц
- С кэшем на 1 час: 24 requests / день = 720 / месяц
- **Запас:** 780 requests (52%)
- **Cost:** $0

### Paid тариф (если нужно)
- Professional: $12/месяц = 100,000 requests
- **Cost per request:** $0.00012
- При 10,000 пользователей/день: ~240 requests/день
- **Monthly cost:** ~$0.86 (но включено в тариф)

## Documentation

**Основная документация:**
- `src/payments/README.md` - Обзор payments app
- `docs/payments/CURRENCY_SETUP.md` - Детальная настройка курсов
- `src/payments/currency_service.py` - Inline docstrings

**API Documentation:**
- exchangerate-api.com: https://www.exchangerate-api.com/docs

## Support & Troubleshooting

**Common Issues:**

1. **"API key not set"** → Добавить `EXCHANGE_RATE_API_KEY` в .env
2. **"Connection timeout"** → Проверить интернет/firewall, fallback сработает автоматически
3. **"Invalid API key"** → Сгенерировать новый ключ на сайте
4. **"Quota reached"** → Upgrade план или уменьшить частоту запросов

**Help:**
- GitHub Issues: https://github.com/your-repo/issues
- Docs: `/docs/payments/CURRENCY_SETUP.md`

---

**Date:** 26 March 2026
**Author:** Pyland Team
**Version:** 1.0.0
