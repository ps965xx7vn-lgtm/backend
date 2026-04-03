# Data Pipelines — Конвейер обработки! 🏭

## Что такое Data Pipeline?

**Data Pipeline** (Конвейер данных) — это последовательная цепочка функций, где **выход одной** становится **входом другой**.

### Без pipeline (много переменных):
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Шаг 1: отобрать чётные
even = [x for x in numbers if x % 2 == 0]

# Шаг 2: удвоить
doubled = [x * 2 for x in even]

# Шаг 3: сумма
total = sum(doubled)

print(total)  # 60
```

### С pipeline (одна цепочка!):
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Pipeline: filter → map → reduce
total = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x * 2, filter(lambda x: x % 2 == 0, numbers)),
    0
)

print(total)  # 60
```

**Данные текут через конвейер!** 🌊

---

## Визуализация Pipeline

```
Входные данные
    ↓
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ↓
filter(чётные)
    ↓
[2, 4, 6, 8, 10]
    ↓
map(удвоить)
    ↓
[4, 8, 12, 16, 20]
    ↓
reduce(сумма)
    ↓
60
```

**Каждый этап преобразует данные и передаёт дальше!**

---

## Базовый Pipeline: filter → map → reduce

### Пример 1: Сумма квадратов чётных
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

result = reduce(
    lambda acc, x: acc + x,  # Шаг 3: сумма
    map(
        lambda x: x ** 2,  # Шаг 2: возвести в квадрат
        filter(lambda x: x % 2 == 0, numbers)  # Шаг 1: чётные
    ),
    0
)

print(result)  # 220
# Чётные: [2, 4, 6, 8, 10]
# Квадраты: [4, 16, 36, 64, 100]
# Сумма: 220
```

### Пример 2: Средняя цена дорогих товаров
```python
products = [
    {"name": "Phone", "price": 500},
    {"name": "Laptop", "price": 1200},
    {"name": "Mouse", "price": 25},
    {"name": "Monitor", "price": 300}
]

# Pipeline: filter (>100) → map (извлечь цены) → reduce (среднее)
expensive_prices = list(filter(lambda p: p["price"] > 100, products))
prices = list(map(lambda p: p["price"], expensive_prices))
average = sum(prices) / len(prices) if prices else 0

print(average)  # 666.67
# Дорогие: Phone(500), Laptop(1200), Monitor(300)
# Среднее: (500 + 1200 + 300) / 3 = 666.67
```

---

## Pipeline с List Comprehension

List comprehension — это тоже pipeline, но читаемее!

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# С map/filter
result = sum(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

# С comprehension (ПРОЩЕ!)
result = sum([x ** 2 for x in numbers if x % 2 == 0])

print(result)  # 220
```

**Comprehension читается слева направо!**

---

## Создание пользовательского Pipeline

### Функция pipe()
```python
def pipe(data, *functions):
    """Применить функции последовательно."""
    result = data
    for func in functions:
        result = func(result)
    return result

# Определяем шаги
def filter_even(numbers):
    return [x for x in numbers if x % 2 == 0]

def double_all(numbers):
    return [x * 2 for x in numbers]

def sum_all(numbers):
    return sum(numbers)

# Используем pipeline
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = pipe(numbers, filter_even, double_all, sum_all)

print(result)  # 60
```

### Класс Pipeline
```python
class Pipeline:
    """Удобный pipeline с методами."""

    def __init__(self, data):
        self.data = data

    def filter(self, predicate):
        """Фильтрация."""
        self.data = [x for x in self.data if predicate(x)]
        return self

    def map(self, transform):
        """Преобразование."""
        self.data = [transform(x) for x in self.data]
        return self

    def reduce(self, reducer, initial=None):
        """Свёртка."""
        from functools import reduce
        if initial is None:
            return reduce(reducer, self.data)
        return reduce(reducer, self.data, initial)

    def collect(self):
        """Получить результат."""
        return self.data

# Использование
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

result = (Pipeline(numbers)
    .filter(lambda x: x % 2 == 0)  # Чётные
    .map(lambda x: x * 2)           # Удвоить
    .reduce(lambda acc, x: acc + x, 0))  # Сумма

print(result)  # 60
```

---

## Практические примеры Pipeline

### Пример 1: Обработка студентов
```python
students = [
    {"name": "Алиса", "grade": 95, "active": True},
    {"name": "Боб", "grade": 67, "active": False},
    {"name": "Карл", "grade": 88, "active": True},
    {"name": "Дима", "grade": 72, "active": True},
    {"name": "Ева", "grade": 91, "active": False}
]

# Pipeline: активные → хорошие оценки (>=80) → имена → заглавные
result = [
    name.upper()
    for student in students
    if student["active"] and student["grade"] >= 80
    for name in [student["name"]]
]

print(result)  # ['АЛИСА', 'КАРЛ']

# Или пошагово:
active = [s for s in students if s["active"]]
high_achievers = [s for s in active if s["grade"] >= 80]
names = [s["name"] for s in high_achievers]
upper_names = [n.upper() for n in names]
print(upper_names)  # ['АЛИСА', 'КАРЛ']
```

### Пример 2: Анализ текста
```python
text = "Python is AWESOME! Learn Python, love Python."

# Pipeline: слова → lowercase → только буквы → уникальные → сортировка
words = text.split()
lower_words = [w.lower() for w in words]
clean_words = [w.strip(",.!") for w in lower_words]
unique_words = list(set(clean_words))
sorted_words = sorted(unique_words)

print(sorted_words)  # ['awesome', 'is', 'learn', 'love', 'python']

# Компактно с pipeline
result = sorted(set(w.strip(",.!").lower() for w in text.split()))
print(result)  # ['awesome', 'is', 'learn', 'love', 'python']
```

### Пример 3: Обработка данных AI модели
```python
# Сырые данные AI модели
raw_data = [
    {"model": "GPT-3", "accuracy": 0.92, "loss": 0.15},
    {"model": "BERT", "accuracy": 0.88, "loss": 0.22},
    {"model": "T5", "accuracy": 0.95, "loss": 0.12},
    {"model": "RoBERTa", "accuracy": 0.90, "loss": 0.18}
]

# Pipeline: точность > 0.9 → сортировать по loss → извлечь имена
high_accuracy = [m for m in raw_data if m["accuracy"] > 0.9]
sorted_models = sorted(high_accuracy, key=lambda m: m["loss"])
model_names = [m["model"] for m in sorted_models]

print(model_names)  # ['T5', 'GPT-3', 'RoBERTa']
```

---

## Pipeline для очистки данных

### Очистка и валидация
```python
def clean_data_pipeline(raw_data):
    """Pipeline очистки данных."""

    # Шаг 1: убрать None
    step1 = [x for x in raw_data if x is not None]

    # Шаг 2: убрать пустые строки
    step2 = [x for x in step1 if x != ""]

    # Шаг 3: trim пробелы
    step3 = [x.strip() if isinstance(x, str) else x for x in step2]

    # Шаг 4: убрать дубликаты
    step4 = list(set(step3))

    # Шаг 5: сортировка
    step5 = sorted(step4)

    return step5

# Грязные данные
dirty = [None, "  Python  ", "", "Java", "Python", "  Go  ", None, "Java"]

clean = clean_data_pipeline(dirty)
print(clean)  # ['Go', 'Java', 'Python']
```

### Валидация email
```python
def validate_emails_pipeline(emails):
    """Pipeline проверки email."""

    # Шаг 1: убрать пустые
    non_empty = [e for e in emails if e]

    # Шаг 2: только с @
    with_at = [e for e in non_empty if "@" in e]

    # Шаг 3: только с доменом
    with_domain = [e for e in with_at if "." in e.split("@")[-1]]

    # Шаг 4: lowercase
    normalized = [e.lower().strip() for e in with_domain]

    # Шаг 5: убрать дубликаты
    unique = list(set(normalized))

    return sorted(unique)

# Грязные email
dirty_emails = [
    "alice@gmail.com",
    "BOB@YAHOO.COM",
    "invalid-email",
    "",
    "alice@gmail.com",  # Дубликат
    "charlie@example"    # Без домена
]

clean_emails = validate_emails_pipeline(dirty_emails)
print(clean_emails)  # ['alice@gmail.com', 'bob@yahoo.com']
```

---

## Асинхронный Pipeline (генераторы)

Для БОЛЬШИХ данных используй генераторы!

```python
def filter_even_gen(numbers):
    """Генератор для фильтрации."""
    for n in numbers:
        if n % 2 == 0:
            yield n

def double_gen(numbers):
    """Генератор для удвоения."""
    for n in numbers:
        yield n * 2

# Pipeline с генераторами (ленивая обработка!)
numbers = range(1000000)  # Миллион чисел!

pipeline = double_gen(filter_even_gen(numbers))

# Обрабатывается ПО МЕРЕ ЗАПРОСА!
result = sum(pipeline)
print(result)  # Быстро, без хранения в памяти!
```

**Генераторы не загружают всё в память!** 💡

---

## Обработка ошибок в Pipeline

### Безопасный тPipeline
```python
def safe_pipeline(data, *functions):
    """Pipeline с обработкой ошибок."""
    result = data

    for func in functions:
        try:
            result = func(result)
        except Exception as e:
            print(f"Ошибка в {func.__name__}: {e}")
            return None

    return result

def divide_by_zero(x):
    """Опасная функция."""
    return x / 0

def double(x):
    return x * 2

# Использование
result = safe_pipeline(10, double, divide_by_zero)
# Вывод: Ошибка в divide_by_zero: division by zero
print(result)  # None
```

---

## Pipeline + map/filter/reduce

### Комбинация всех инструментов
```python
from functools import reduce

data = [
    {"product": "Phone", "quantity": 2, "price": 500},
    {"product": "Laptop", "quantity": 1, "price": 1200},
    {"product": "Mouse", "quantity": 5, "price": 25},
    {"product": "Monitor", "quantity": 2, "price": 300}
]

# Pipeline: quantity > 1 → вычислить total → суммировать
filtered = filter(lambda item: item["quantity"] > 1, data)
totals = map(lambda item: item["quantity"] * item["price"], filtered)
grand_total = reduce(lambda acc, x: acc + x, totals, 0)

print(grand_total)  # 1725
# Phone: 2 * 500 = 1000
# Mouse: 5 * 25 = 125
# Monitor: 2 * 300 = 600
# Total: 1725
```

---

## Частые ошибки

### Ошибка 1: Изменение оригинальных данных
```python
def bad_pipeline(data):
    data.sort()  # Меняет оригинал!
    return [x * 2 for x in data]

numbers = [3, 1, 2]
result = bad_pipeline(numbers)
print(numbers)  # [1, 2, 3]  ← Изменился!

# ✅ ПРАВИЛЬНО: pure function
def good_pipeline(data):
    sorted_data = sorted(data)  # Новый список
    return [x * 2 for x in sorted_data]

numbers = [3, 1, 2]
result = good_pipeline(numbers)
print(numbers)  # [3, 1, 2]  ← Не изменился!
```

### Ошибка 2: Слишком длинный pipeline
```python
# ❌ ПЛОХО: нечитаемо!
result = reduce(
    lambda a, x: a + x,
    map(
        lambda x: x ** 2,
        filter(
            lambda x: x > 0,
            map(
                lambda x: x - 10,
                filter(lambda x: x % 2 == 0, data)
            )
        )
    ),
    0
)

# ✅ ЛУЧШЕ: разбить на шаги
step1 = [x for x in data if x % 2 == 0]
step2 = [x - 10 for x in step1]
step3 = [x for x in step2 if x > 0]
step4 = [x ** 2 for x in step3]
result = sum(step4)
```

---

## Резюме

### Data Pipeline — это:
- ✅ Последовательность преобразований данных
- ✅ Выход одной функции → вход другой
- ✅ Чистые функции без побочных эффектов
- ✅ Читаемый и предсказуемый код

### Основные этапы:
```
Данные → filter → map → reduce → Результат
```

### Инструменты:
```python
# filter() — отобрать
filter(lambda x: x > 0, data)

# map() — преобразовать
map(lambda x: x * 2, data)

# reduce() — свернуть
reduce(lambda acc, x: acc + x, data, 0)

# List comprehension — всё сразу
[x * 2 for x in data if x > 0]
```

### Правила хорошего pipeline:
- ✅ Каждый шаг — чистая функция
- ✅ Не менять исходные данные
- ✅ Разбивать сложные pipeline на шаги
- ✅ Использовать генераторы для больших данных
- ✅ Обрабатывать ошибки

---

## Что дальше?

Теперь ты знаешь Data Pipelines! 🎉

**Следующие темы:**
- Function composition — композиция функций
- Generator expressions — ленивые вычисления
- Декораторы — обёртки для функций

Data pipeline — основа обработки данных в AI! 🤖📊
