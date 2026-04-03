# AI Startup Investment — Привлеки капитал! 💎

## Что такое инвестиции в стартап?

**Инвестиции** — это деньги, которые инвесторы дают стартапу в обмен на долю компании.

### Простая формула:
```
Деньги в обмен на акции = Инвестиция
```

**Без инвестиций сложно масштабироваться!** 📈

---

## Раунды инвестиций

### Этапы финансирования:

```python
investment_rounds = {
    "Bootstrapping": {
        "amount": "0-50K",
        "source": "Свои деньги",
        "stage": "Идея"
    },
    "Friends & Family": {
        "amount": "10K-100K",
        "source": "Друзья и семья",
        "stage": "Прототип"
    },
    "Angel": {
        "amount": "50K-500K",
        "source": "Бизнес-ангелы",
        "stage": "MVP"
    },
    "Seed": {
        "amount": "500K-2M",
        "source": "Венчурные фонды",
        "stage": "Первые клиенты"
    },
    "Series A": {
        "amount": "2M-15M",
        "source": "VC фонды",
        "stage": "Масштабирование"
    },
    "Series B": {
        "amount": "10M-50M",
        "source": "Крупные VC",
        "stage": "Быстрый рост"
    },
    "Series C+": {
        "amount": "50M+",
        "source": "Мега-фонды",
        "stage": "Глобальная экспансия"
    }
}
```

---

## Bootstrapping (Бутстрапинг)

**Начать на свои деньги.**

```python
class BootstrappedStartup:
    """Стартап без внешних инвестиций."""

    def __init__(self, founder_capital):
        self.capital = founder_capital
        self.revenue = 0
        self.expenses = 0
        self.stage = "bootstrapping"

    def generate_revenue(self, amount):
        """Заработать деньги."""
        self.revenue += amount
        self.capital += amount
        print(f"💰 Выручка: +${amount} (Всего: ${self.capital})")

    def pay_expenses(self, amount):
        """Оплатить расходы."""
        if self.capital < amount:
            print(f"❌ Недостаточно средств!")
            return False

        self.expenses += amount
        self.capital -= amount
        print(f"💸 Расходы: -${amount} (Осталось: ${self.capital})")
        return True

    def get_status(self):
        """Статус стартапа."""
        profit = self.revenue - self.expenses

        return {
            "capital": self.capital,
            "revenue": self.revenue,
            "expenses": self.expenses,
            "profit": profit,
            "stage": self.stage
        }

# Использование
startup = BootstrappedStartup(founder_capital=10000)

# Первые месяцы
startup.generate_revenue(500)
startup.pay_expenses(300)
startup.generate_revenue(800)
startup.pay_expenses(400)

print(startup.get_status())
```

**Плюсы:** Полный контроль, нет инвесторов
**Минусы:** Медленный рост, свои риски

---

## Seed Round (Посевной раунд)

**Первый серьёзный раунд финансирования.**

```python
class SeedRound:
    """Посевной раунд инвестиций."""

    def __init__(self, startup_name, pre_money_valuation):
        self.startup_name = startup_name
        self.pre_money_valuation = pre_money_valuation
        self.investment_amount = 0
        self.investor_equity = 0
        self.post_money_valuation = pre_money_valuation

    def receive_investment(self, amount):
        """Получить инвестицию."""
        self.investment_amount = amount
        self.post_money_valuation = self.pre_money_valuation + amount

        # Доля инвестора = investment / post-money valuation
        self.investor_equity = (amount / self.post_money_valuation) * 100

        print(f"💎 {self.startup_name} получил ${amount:,}")
        print(f"📊 Pre-money valuation: ${self.pre_money_valuation:,}")
        print(f"📊 Post-money valuation: ${self.post_money_valuation:,}")
        print(f"🤝 Доля инвестора: {self.investor_equity:.1f}%")
        print(f"👤 Доля основателя: {100 - self.investor_equity:.1f}%")

    def get_terms(self):
        """Условия раунда."""
        return {
            "pre_money": self.pre_money_valuation,
            "investment": self.investment_amount,
            "post_money": self.post_money_valuation,
            "investor_equity": f"{self.investor_equity:.1f}%",
            "founder_equity": f"{100 - self.investor_equity:.1f}%"
        }

# Пример Seed раунда
seed = SeedRound("TextMaster AI", pre_money_valuation=2000000)
seed.receive_investment(500000)
```

### Типичные условия Seed:
```python
seed_terms = {
    "amount": "500K - 2M",
    "equity": "10-25%",
    "valuation": "2M - 10M",
    "investors": "VC funds, Angel syndicates"
}
```

---

## Series A (Раунд A)

**Масштабирование бизнеса.**

```python
def calculate_series_a(revenue_growth, active_users, mrr):
    """Готовность к Series A."""
    criteria = {
        "revenue_growth": revenue_growth > 3.0,  # 3x рост
        "users": active_users > 1000,
        "mrr": mrr > 10000  # $10K MRR
    }

    ready = all(criteria.values())

    return {
        "ready_for_series_a": ready,
        "criteria": criteria,
        "typical_raise": "2M-15M" if ready else "Not ready"
    }

# Проверка готовности
result = calculate_series_a(
    revenue_growth=4.5,  # 4.5x рост
    active_users=2500,
    mrr=15000  # $15K/месяц
)

print(f"Готовность к Series A: {result['ready_for_series_a']}")
print(f"Типичная сумма: {result['typical_raise']}")
```

---

## Оценка стартапа (Valuation)

### Методы оценки:

**1. Revenue Multiple (Мультипликатор выручки)**
```python
def calculate_valuation_revenue(arr, multiple=10):
    """Оценка через ARR."""
    return arr * multiple

# Пример
arr = 120000  # $120K ARR
valuation = calculate_valuation_revenue(arr, multiple=10)
print(f"Оценка: ${valuation:,}")  # $1,200,000
```

**2. User-based Valuation**
```python
def calculate_valuation_users(active_users, value_per_user=100):
    """Оценка через пользователей."""
    return active_users * value_per_user

# Пример
users = 5000
valuation = calculate_valuation_users(users, value_per_user=100)
print(f"Оценка: ${valuation:,}")  # $500,000
```

**3. Comparable Companies**
```python
def calculate_valuation_comparable(similar_company_valuation, your_metrics_ratio):
    """Оценка через аналоги."""
    return similar_company_valuation * your_metrics_ratio

# Пример: похожий стартап оценён в $5M, у нас в 2 раза меньше метрики
valuation = calculate_valuation_comparable(5000000, 0.5)
print(f"Оценка: ${valuation:,}")  # $2,500,000
```

---

## Dilution (Размытие доли)

### Как меняется доля основателя:

```python
class FounderEquity:
    """Отслеживание доли основателя."""

    def __init__(self, initial_equity=100):
        self.equity_history = [initial_equity]
        self.rounds = ["Founding"]

    def add_round(self, round_name, equity_sold):
        """Добавить раунд инвестиций."""
        current_equity = self.equity_history[-1]
        new_equity = current_equity * (1 - equity_sold / 100)

        self.equity_history.append(new_equity)
        self.rounds.append(round_name)

        print(f"{round_name}: {current_equity:.1f}% → {new_equity:.1f}%")

    def get_history(self):
        """История размытия."""
        return list(zip(self.rounds, self.equity_history))

# Пример размытия
founder = FounderEquity(initial_equity=100)

founder.add_round("Seed", equity_sold=20)     # Отдали 20%
founder.add_round("Series A", equity_sold=25)  # Отдали 25% от оставшегося
founder.add_round("Series B", equity_sold=20)  # Отдали 20% от оставшегося

print("\n📊 История доли:")
for round_name, equity in founder.get_history():
    print(f"{round_name}: {equity:.1f}%")
```

---

## Практический пример: жизненный цикл

```python
class StartupFunding:
    """Полный цикл финансирования стартапа."""

    def __init__(self, name):
        self.name = name
        self.stage = "idea"
        self.capital = 0
        self.valuation = 0
        self.founder_equity = 100
        self.funding_history = []

    def bootstrap(self, amount):
        """Начать на свои деньги."""
        self.capital = amount
        self.stage = "bootstrapping"
        self.funding_history.append({
            "round": "Bootstrapping",
            "amount": amount,
            "valuation": 0,
            "equity_sold": 0
        })
        print(f"🏁 {self.name} запущен с ${amount:,}")

    def raise_round(self, round_name, amount, valuation, equity_sold):
        """Привлечь раунд."""
        self.capital += amount
        self.valuation = valuation
        self.founder_equity *= (1 - equity_sold / 100)
        self.stage = round_name.lower()

        self.funding_history.append({
            "round": round_name,
            "amount": amount,
            "valuation": valuation,
            "equity_sold": equity_sold
        })

        print(f"\n💎 {round_name} завершён!")
        print(f"   Привлечено: ${amount:,}")
        print(f"   Оценка: ${valuation:,}")
        print(f"   Доля основателя: {self.founder_equity:.1f}%")

    def get_summary(self):
        """Итоговая сводка."""
        total_raised = sum(r["amount"] for r in self.funding_history)

        return {
            "name": self.name,
            "stage": self.stage,
            "total_raised": total_raised,
            "current_valuation": self.valuation,
            "founder_equity": f"{self.founder_equity:.1f}%",
            "funding_rounds": len(self.funding_history)
        }

# История привлечения инвестиций
startup = StartupFunding("TextMaster AI")

# Этап 1: Bootstrapping
startup.bootstrap(10000)

# Этап 2: Seed
startup.raise_round("Seed", 500000, 2500000, equity_sold=20)

# Этап 3: Series A
startup.raise_round("Series A", 5000000, 25000000, equity_sold=20)

# Этап 4: Series B
startup.raise_round("Series B", 20000000, 100000000, equity_sold=20)

# Итоги
print("\n📈 Финальная сводка:")
summary = startup.get_summary()
for key, value in summary.items():
    print(f"  {key}: {value}")
```

---

## Metrics инвестор смотрит

### Key тфmetricsы для инвесторов:

```python
investor_metrics = {
    "Traction": {
        "users": "Количество пользователей",
        "growth_rate": "Месячный рост %",
        "retention": "Удержание пользователей"
    },
    "Revenue": {
        "mrr": "Monthly Recurring Revenue",
        "arr": "Annual Recurring Revenue",
        "ltv": "Lifetime Value клиента"
    },
    "Unit Economics": {
        "cac": "Customer Acquisition Cost",
        "ltv_cac_ratio": "LTV / CAC > 3",
        "gross_margin": "Валовая маржа > 70%"
    },
    "Team": {
        "experience": "Опыт основателей",
        "technical_expertise": "Технические навыки",
        "market_knowledge": "Знание рынка"
    }
}
```

### Расчет LTV/CAC:
```python
def calculate_ltv_cac_ratio(avg_revenue_per_user, churn_rate, acquisition_cost):
    """LTV/CAC ratio - ключевая метрика."""
    if churn_rate == 0:
        ltv = float('inf')
    else:
        ltv = avg_revenue_per_user / churn_rate

    if acquisition_cost == 0:
        return float('inf')

    ratio = ltv / acquisition_cost

    return {
        "ltv": ltv,
        "cac": acquisition_cost,
        "ratio": ratio,
        "status": "Good" if ratio > 3 else "Need improvement"
    }

# Пример
result = calculate_ltv_cac_ratio(
    avg_revenue_per_user=120,  # $120 за lifetime
    churn_rate=0.10,           # 10% уходит
    acquisition_cost=30        # $30 стоит привлечь
)

print(f"LTV: ${result['ltv']:.2f}")
print(f"CAC: ${result['cac']}")
print(f"LTV/CAC: {result['ratio']:.1f}x")
print(f"Статус: {result['status']}")
```

---

## Частые ошибки

### ❌ Ошибка 1: Слишком раннее привлечение
```python
# ПЛОХО: привлекаем без продукта
if users == 0 and revenue == 0:
    raise_seed_round()  # Никто не даст!

# ✅ ХОРОШО: сначала traction
build_mvp()
get_first_users(100)
generate_revenue(1000)
then_raise_seed()
```

### ❌ Ошибка 2: Завышенная оценка
```python
# ПЛОХО: нереалистичная оценка
valuation = 50000000  # $50M без revenue!

# ✅ ХОРОШО: адекватная оценка
arr = 100000  # $100K ARR
realistic_valuation = arr * 10  # $1M
```

### ❌ Ошибка 3: Продажа слишком большой доли
```python
# ПЛОХО: отдали 60% в Seed
founder_equity = 40  # Мало контроля!

# ✅ ХОРОШО: сохранить контроль
seed_equity_sold = 20  # 20-25% в Seed
founder_equity = 80  # Контроль сохранён
```

---

## Резюме

### Раунды инвестиций:
```python
rounds = {
    "Bootstrapping": "0-50K (свои)",
    "Seed": "500K-2M (10-25%)",
    "Series A": "2M-15M (15-25%)",
    "Series B": "10M-50M (15-20%)",
    "Series C+": "50M+ (< 20%)"
}
```

### Ключевые термины:
```python
terms = {
    "Valuation": "Оценка стартапа",
    "Equity": "Доля компании",
    "Dilution": "Размытие доли",
    "Post-money": "Оценка после инвестиций"
}
```

### Метрики для инвесторов:
- 📈 **Growth Rate** — рост пользователей
- 💰 **MRR/ARR** — регулярная выручка
- 🎯 **LTV/CAC** — юнит-экономика
- 👥 **Team** — сильная команда

---

## Что дальше?

Теперь ты знаешь про инвестиции! 🎉

**Следующие темы:**
- Конкуренция — анализ рынка
- Pitch deck — презентация для инвесторов
- Exit стратегия — продажа или IPO

Привлеки миллионы в свой AI стартап! 💎🚀
