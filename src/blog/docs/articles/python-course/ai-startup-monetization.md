# AI Startup Monetization — Зарабатывай деньги! 💰

## Что такое монетизация?

**Монетизация** — это превращение продукта в деньги.

### Простая формула:
```
Продукт + Пользователи = Выручка
```

**Без монетизации стартап не выживет!** 💸

---

## Модели монетизации для AI

### 1. API Pricing (Плата за запросы)
**Клиенты платят за каждый запрос к AI.**

```python
api_pricing = {
    "text_generation": "$0.02 / 1000 токенов",
    "image_generation": "$0.015 / изображение",
    "data_analysis": "$0.001 / запрос"
}
```

**Примеры:**
- OpenAI — $0.02 за 1K токенов
- Midjourney — $0.04 за изображение
- Stable Diffusion — $0.0015 за генерацию

### 2. Subscription (Подписка)
**Фиксированная плата в месяц.**

```python
subscription_tiers = {
    "free": {"price": 0, "requests": 100},
    "basic": {"price": 10, "requests": 1000},
    "pro": {"price": 50, "requests": 10000},
    "enterprise": {"price": 500, "requests": 100000}
}
```

### 3. Freemium
**Бесплатно + платные функции.**

```python
freemium_model = {
    "free": {
        "features": ["Базовая AI", "100 запросов/месяц"],
        "price": 0
    },
    "premium": {
        "features": ["Продвинутая AI", "Без лимитов", "API доступ"],
        "price": 29
    }
}
```

---

## Расчёт выручки

### Monthly Recurring Revenue (MRR)
```python
def calculate_mrr(users_by_tier, tier_prices):
    """Месячная повторяющаяся выручка."""
    mrr = 0

    for tier, users in users_by_tier.items():
        price = tier_prices.get(tier, 0)
        mrr += users * price

    return mrr

# Пример
users = {"free": 1000, "basic": 150, "pro": 30, "enterprise": 5}
prices = {"free": 0, "basic": 10, "pro": 50, "enterprise": 500}

mrr = calculate_mrr(users, prices)
print(f"MRR: ${mrr:,}")  # MRR: $5,500
```

### Annual Recurring Revenue (ARR)
```python
def calculate_arr(mrr):
    """Годовая выручка."""
    return mrr * 12

arr = calculate_arr(mrr)
print(f"ARR: ${arr:,}")  # ARR: $66,000
```

---

## API Pricing система

### Простая система оплаты за запросы
```python
class APIMonetization:
    """Система монетизации API."""

    def __init__(self):
        self.pricing = {
            "text_generation": 0.02,  # $0.02 за 1K токенов
            "image_generation": 0.015,  # $0.015 за изображение
            "data_analysis": 0.001  # $0.001 за запрос
        }

    def calculate_cost(self, service_type, units):
        """Рассчитать стоимость."""
        price_per_unit = self.pricing.get(service_type, 0)
        return price_per_unit * units

    def process_request(self, service_type, units, user_balance):
        """Обработать запрос."""
        cost = self.calculate_cost(service_type, units)

        if user_balance < cost:
            return {
                "success": False,
                "message": "Недостаточно средств",
                "cost": cost,
                "balance": user_balance
            }

        new_balance = user_balance - cost

        return {
            "success": True,
            "cost": cost,
            "balance": new_balance
        }

# Использование
api = APIMonetization()

# Запрос генерации текста (50K токенов = 50 единиц)
result = api.process_request("text_generation", 50, user_balance=10)
print(result)
# {'success': True, 'cost': 1.0, 'balance': 9.0}
```

---

## Тарифные планы (Tiers)

### Создание тарифов
```python
class SubscriptionTier:
    """Тарифный план."""

    def __init__(self, name, price, limits):
        self.name = name
        self.price = price  # $ в месяц
        self.limits = limits  # Лимиты использования

    def can_afford(self, current_usage):
        """Проверить, не превышен ли лимит."""
        for resource, usage in current_usage.items():
            limit = self.limits.get(resource, 0)
            if usage > limit:
                return False
        return True

    def get_info(self):
        """Информация о тарифе."""
        return {
            "name": self.name,
            "price": f"${self.price}/месяц",
            "limits": self.limits
        }

# Создать тарифы
free_tier = SubscriptionTier("Free", 0, {
    "api_requests": 100,
    "storage_mb": 10
})

basic_tier = SubscriptionTier("Basic", 10, {
    "api_requests": 1000,
    "storage_mb": 100
})

pro_tier = SubscriptionTier("Pro", 50, {
    "api_requests": 10000,
    "storage_mb": 1000
})

# Проверка использования
usage = {"api_requests": 500, "storage_mb": 50}

print("Free tier:", free_tier.can_afford(usage))  # False
print("Basic tier:", basic_tier.can_afford(usage))  # True
```

---

## Учёт использования (Usage Tracking)

### Трекинг API запросов
```python
class UsageTracker:
    """Отслеживание использования API."""

    def __init__(self):
        self.users = {}  # {user_id: usage_data}

    def track_request(self, user_id, service_type, units):
        """Записать запрос."""
        if user_id not in self.users:
            self.users[user_id] = {
                "requests": 0,
                "total_cost": 0,
                "services_used": {}
            }

        user = self.users[user_id]
        user["requests"] += 1

        if service_type not in user["services_used"]:
            user["services_used"][service_type] = 0

        user["services_used"][service_type] += units

    def get_user_usage(self, user_id):
        """Статистика пользователя."""
        return self.users.get(user_id, {
            "requests": 0,
            "total_cost": 0,
            "services_used": {}
        })

    def get_total_revenue(self, pricing):
        """Общая выручка."""
        total = 0

        for user_data in self.users.values():
            for service, units in user_data["services_used"].items():
                price = pricing.get(service, 0)
                total += price * units

        return total

# Использование
tracker = UsageTracker()

# Пользователи делают запросы
tracker.track_request("user1", "text_generation", 10)
tracker.track_request("user1", "image_generation", 5)
tracker.track_request("user2", "text_generation", 50)

# Статистика user1
usage = tracker.get_user_usage("user1")
print(f"User1 usage: {usage}")

# Общая выручка
pricing = {"text_generation": 0.02, "image_generation": 0.015}
revenue = tracker.get_total_revenue(pricing)
print(f"Total revenue: ${revenue:.2f}")
```

---

## Конверсия Free → Paid

### Стратегии конверсии
```python
def calculate_conversion_rate(free_users, paid_users):
    """Процент конверсии из free в paid."""
    total = free_users + paid_users
    if total == 0:
        return 0
    return (paid_users / total) * 100

# Пример
free = 1000
paid = 50

conversion = calculate_conversion_rate(free, paid)
print(f"Конверсия: {conversion:.1f}%")  # 4.8%
```

### Улучшение конверсии
```python
class ConversionOptimizer:
    """Оптимизация конверсии."""

    @staticmethod
    def suggest_upgrade(user_usage, current_tier):
        """Предложить upgrade."""
        suggestions = []

        # Если пользователь близок к лимиту
        if user_usage["api_requests"] > current_tier.limits["api_requests"] * 0.8:
            suggestions.append({
                "reason": "Скоро закончатся запросы",
                "benefit": "Upgrade для больше запросов"
            })

        # Если часто использует
        if user_usage["api_requests"] > 50:
            suggestions.append({
                "reason": "Активное использование",
                "benefit": "Pro тариф выгоднее"
            })

        return suggestions

# Использование
optimizer = ConversionOptimizer()
usage = {"api_requests": 85, "storage_mb": 5}
suggestions = optimizer.suggest_upgrade(usage, free_tier)

for s in suggestions:
    print(f"💡 {s['reason']}: {s['benefit']}")
```

---

## Практический пример: полная система

```python
class AIStartupMonetization:
    """Полная система монетизации."""

    def __init__(self):
        self.tiers = {
            "free": {"price": 0, "requests": 100},
            "basic": {"price": 10, "requests": 1000},
            "pro": {"price": 50, "requests": 10000}
        }

        self.users = {}  # {user_id: {tier, usage, balance}}
        self.revenue = 0

    def register_user(self, user_id, tier="free"):
        """Зарегистрировать пользователя."""
        self.users[user_id] = {
            "tier": tier,
            "usage": 0,
            "balance": 0
        }
        print(f"✅ Пользователь {user_id} зарегистрирован ({tier} tier)")

    def upgrade_user(self, user_id, new_tier):
        """Upgrade тарифа."""
        if user_id not in self.users:
            return False

        old_tier = self.users[user_id]["tier"]
        self.users[user_id]["tier"] = new_tier

        # Добавить revenue
        tier_price = self.tiers[new_tier]["price"]
        self.revenue += tier_price

        print(f"⬆️ {user_id}: {old_tier} → {new_tier} (+${tier_price})")
        return True

    def process_request(self, user_id):
        """Обработать API запрос."""
        if user_id not in self.users:
            return False

        user = self.users[user_id]
        tier_limit = self.tiers[user["tier"]]["requests"]

        if user["usage"] >= tier_limit:
            print(f"❌ {user_id}: лимит исчерпан ({user['usage']}/{tier_limit})")
            return False

        user["usage"] += 1
        print(f"✅ Запрос обработан: {user['usage']}/{tier_limit}")
        return True

    def get_stats(self):
        """Статистика."""
        total_users = len(self.users)
        users_by_tier = {}

        for user_data in self.users.values():
            tier = user_data["tier"]
            users_by_tier[tier] = users_by_tier.get(tier, 0) + 1

        mrr = sum(
            count * self.tiers[tier]["price"]
            for tier, count in users_by_tier.items()
        )

        return {
            "total_users": total_users,
            "users_by_tier": users_by_tier,
            "mrr": mrr,
            "arr": mrr * 12
        }

# Использование
startup = AIStartupMonetization()

# Регистрация пользователей
startup.register_user("alice", "free")
startup.register_user("bob", "free")
startup.register_user("charlie", "basic")

# Использование и upgrade
for _ in range(100):  # Alice исчерпывает лимит
    startup.process_request("alice")

startup.process_request("alice")  # Превышен лимит!

# Alice делает upgrade
startup.upgrade_user("alice", "basic")

# Теперь может использовать
startup.process_request("alice")

# Статистика
stats = startup.get_stats()
print(f"\n📊 Статистика стартапа:")
print(f"Пользователей: {stats['total_users']}")
print(f"По тарифам: {stats['users_by_tier']}")
print(f"MRR: ${stats['mrr']}")
print(f"ARR: ${stats['arr']}")
```

---

## Частые ошибки монетизации

### ❌ Ошибка 1: Слишком дорого
```python
# ПЛОХО: высокая цена отпугивает
expensive_tier = {"price": 500, "requests": 1000}  # $0.50 за запрос!

# ✅ ХОРОШО: конкурентная цена
reasonable_tier = {"price": 10, "requests": 1000}  # $0.01 за запрос
```

### ❌ Ошибка 2: Нет free tier
```python
# ПЛОХО: нет способа попробовать бесплатно
tiers = {"basic": 50, "pro": 200}  # Барьер входа!

# ✅ ХОРОШО: freemium модель
tiers = {"free": 0, "basic": 10, "pro": 50}  # Можно попробовать
```

### ❌ Ошибка 3: Нечёткие лимиты
```python
# ПЛОХО: непонятные лимиты
tier = {"price": 10, "features": "Базовые"}  # Что это значит?

# ✅ ХОРОШО: чёткие цифры
tier = {"price": 10, "requests": 1000, "storage_mb": 100}
```

---

## Резюме

### Модели монетизации:
```python
models = {
    "API Pricing": "Плата за запросы",
    "Subscription": "Фиксированная плата/месяц",
    "Freemium": "Бесплатно + премиум",
    "Pay-as-you-go": "Платишь только за использование"
}
```

### Ключевые метрики:
```python
metrics = {
    "MRR": "Monthly Recurring Revenue",
    "ARR": "Annual Recurring Revenue",
    "ARPU": "Average Revenue Per User",
    "Conversion Rate": "Free → Paid %"
}
```

### Успешные тарифные планы:
- **Free** — 0$, ограниченный доступ
- **Basic** — $10-30, для индивидуалов
- **Pro** — $50-100, для профессионалов
- **Enterprise** — $500+, для компаний

---

## Что дальше?

Теперь ты знаешь монетизацию AI! 🎉

**Следующие темы:**
- Инвестиции — раунды, оценка стартапа
- Конкуренция — анализ рынка
- Масштабирование — рост выручки

Создай прибыльный AI стартап! 💰🚀
