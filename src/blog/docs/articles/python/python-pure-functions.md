# Pure Functions — Чистота и порядок! 🧼

## Что такое Pure Function (Чистая функция)?

**Pure function** — это функция, которая:
1. **Всегда возвращает одинаковый результат** при одинаковых аргументах
2. **Не имеет побочных эффектов** (не меняет внешнее состояние)

### Пример ЧИСТОЙ функции:
```python
def add(a, b):
    return a + b

print(add(2, 3))  # 5
print(add(2, 3))  # 5  ← Всегда одинаковый результат!
```

### Пример НЕЧИСТОЙ функции:
```python
total = 0  # Глобальная переменная

def add_impure(x):
    global total
    total += x  # Меняет внешнее состояние!
    return total

print(add_impure(5))  # 5
print(add_impure(5))  # 10  ← Разные результаты!
```

**Чистые функции предсказуемы и надёжны!** 🎯

---

## Признаки Pure Function

### ✅ Чистая функция:
```python
def multiply(x, y):
    """Чистая: только аргументы → результат."""
    return x * y
```

- ✅ Использует только свои аргументы
- ✅ Не читает глобальные переменные
- ✅ Не меняет аргументы
- ✅ Не печатает, не пишет в файл
- ✅ Одинаковый input → одинаковый output

### ❌ Нечистая функция:
```python
counter = 0

def increment_impure():
    """Нечистая: меняет глобальную переменную."""
    global counter
    counter += 1
    return counter
```

- ❌ Использует глобальные переменные
- ❌ Меняет внешнее состояние
- ❌ Разный результат каждый раз

---

## Примеры чистых функций

### 1. Математические операции
```python
def square(x):
    """Возвести в квадрат."""
    return x ** 2

def average(numbers):
    """Среднее значение."""
    return sum(numbers) / len(numbers)

def distance(x1, y1, x2, y2):
    """Расстояние между точками."""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
```

**Все чистые:** одинаковые аргументы → одинаковый результат!

### 2. Работа со строками
```python
def uppercase(text):
    """В заглавные буквы."""
    return text.upper()

def reverse(text):
    """Перевернуть строку."""
    return text[::-1]

def count_vowels(text):
    """Подсчёт гласных."""
    vowels = "aeiouаеёиоуыэюя"
    return sum(1 for char in text.lower() if char in vowels)
```

**Все чистые:** не меняют исходную строку!

### 3. Работа со списками
```python
def double_all(numbers):
    """Удвоить каждое число."""
    return [x * 2 for x in numbers]

def filter_positive(numbers):
    """Только положительные."""
    return [x for x in numbers if x > 0]

def get_first_n(data, n):
    """Первые N элементов."""
    return data[:n]
```

**Все чистые:** возвращают НОВЫЙ список, не меняя оригинал!

---

## Примеры нечистых функций

### 1. Изменение глобального состояния
```python
# ❌ НЕЧИСТАЯ
total_score = 0

def add_score_impure(points):
    global total_score
    total_score += points
    return total_score

# ✅ ЧИСТАЯ
def add_score_pure(current_total, points):
    return current_total + points
```

### 2. Изменение аргументов
```python
# ❌ НЕЧИСТАЯ
def append_impure(lst, item):
    lst.append(item)  # Меняет оригинальный список!
    return lst

# ✅ ЧИСТАЯ
def append_pure(lst, item):
    return lst + [item]  # Новый список
```

### 3. Побочные эффекты (I/O)
```python
# ❌ НЕЧИСТАЯ
def save_to_file_impure(data):
    with open("data.txt", "w") as f:
        f.write(data)
    return True

# ❌ НЕЧИСТАЯ
def print_result_impure(x):
    print(f"Result: {x}")  # Печать = побочный эффект!
    return x

# ✅ ЧИСТАЯ (возвращает данные, печать снаружи)
def format_result_pure(x):
    return f"Result: {x}"
```

### 4. Использование случайности
```python
import random

# ❌ НЕЧИСТАЯ
def get_random_number_impure():
    return random.randint(1, 100)

# ✅ ЧИСТАЯ (передаём seed как аргумент)
def get_random_number_pure(seed):
    random.seed(seed)
    return random.randint(1, 100)
```

---

## Почему Pure Functions хороши?

### 1. Предсказуемость
```python
# Чистая функция
def add(a, b):
    return a + b

# Результат всегда одинаковый!
assert add(2, 3) == 5
assert add(2, 3) == 5
assert add(2, 3) == 5
```

### 2. Лёгкое тестирование
```python
# Тестировать чистую функцию легко!
def test_add():
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, 1) == 0
    # Всегда работает одинаково!
```

### 3. Параллелизм
```python
# Чистые функции можно вызывать параллельно!
from multiprocessing import Pool

def square(x):
    return x ** 2

numbers = [1, 2, 3, 4, 5]

# Безопасно распараллелить
with Pool(4) as pool:
    results = pool.map(square, numbers)

print(results)  # [1, 4, 9, 16, 25]
```

### 4. Кэширование (Memoization)
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    """Чистая функция — можно кэшировать!"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Повторные вызовы мгновенные!
print(fibonacci(100))  # Вычисляется
print(fibonacci(100))  # Берётся из кэша!
```

---

## Как сделать функцию чистой?

### Проблема 1: Глобальная переменная
```python
# ❌ НЕЧИСТАЯ
score = 0

def add_points_impure(points):
    global score
    score += points
    return score

# ✅ ЧИСТАЯ — передать состояние аргументом
def add_points_pure(current_score, points):
    return current_score + points

# Использование
score = 0
score = add_points_pure(score, 10)  # 10
score = add_points_pure(score, 5)   # 15
```

### Проблема 2: Изменение списка
```python
# ❌ НЕЧИСТАЯ
def sort_impure(numbers):
    numbers.sort()  # Меняет оригинал!
    return numbers

# ✅ ЧИСТАЯ — вернуть новый список
def sort_pure(numbers):
    return sorted(numbers)  # Новый список

# Использование
original = [3, 1, 2]
sorted_list = sort_pure(original)
print(original)     # [3, 1, 2]  ← не изменился
print(sorted_list)  # [1, 2, 3]
```

### Проблема 3: Изменение словаря
```python
# ❌ НЕЧИСТАЯ
def update_age_impure(person, new_age):
    person["age"] = new_age  # Меняет оригинал!
    return person

# ✅ ЧИСТАЯ — вернуть новый словарь
def update_age_pure(person, new_age):
    return {**person, "age": new_age}

# Использование
person = {"name": "Алиса", "age": 25}
updated = update_age_pure(person, 26)
print(person)   # {'name': 'Алиса', 'age': 25}  ← не изменился
print(updated)  # {'name': 'Алиса', 'age': 26}
```

---

## Практические примеры

### Пример 1: Обработка данных студентов
```python
# Чистая функция — фильтрация
def get_high_performers(students, threshold=90):
    """Студенты с оценкой >= threshold."""
    return [s for s in students if s["grade"] >= threshold]

# Чистая функция — трансформация
def add_status(students):
    """Добавить статус без изменения оригинала."""
    return [
        {**s, "status": "Отличник" if s["grade"] >= 90 else "Хорошист"}
        for s in students
    ]

# Использование
students = [
    {"name": "Алиса", "grade": 95},
    {"name": "Боб", "grade": 87},
    {"name": "Карл", "grade": 92}
]

high_performers = get_high_performers(students, 90)
with_status = add_status(students)

# Оригинал НЕ изменён!
print(students)  # Без поля "status"
```

### Пример 2: Вычисления для AI модели
```python
# Чистые функции — математические операции
def calculate_accuracy(correct, total):
    """Точность модели."""
    return (correct / total) * 100 if total > 0 else 0

def calculate_f1_score(precision, recall):
    """F1-мера."""
    if precision + recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)

def normalize_scores(scores):
    """Нормализация 0-100."""
    max_score = max(scores) if scores else 1
    return [s / max_score * 100 for s in scores]

# Использование
acc = calculate_accuracy(85, 100)  # 85.0
f1 = calculate_f1_score(0.9, 0.85)  # 0.874
normalized = normalize_scores([10, 50, 75, 100])  # [10, 50, 75, 100]
```

### Пример 3: Обработка цен
```python
# Чистые функции для цен
def apply_discount(price, discount_percent):
    """Применить скидку."""
    return price * (1 - discount_percent / 100)

def add_tax(price, tax_percent):
    """Добавить налог."""
    return price * (1 + tax_percent / 100)

def calculate_total(prices):
    """Общая сумма."""
    return sum(prices)

# Композиция чистых функций
def final_price(base_price, discount, tax):
    """Финальная цена: скидка → налог."""
    discounted = apply_discount(base_price, discount)
    with_tax = add_tax(discounted, tax)
    return round(with_tax, 2)

# Использование
price = final_price(100, 20, 10)  # 100 → 80 (скидка) → 88 (налог)
print(price)  # 88.0
```

---

## Композиция Pure Functions

Чистые функции можно комбинировать как LEGO!

```python
# Набор чистых функций
def double(x):
    return x * 2

def add_ten(x):
    return x + 10

def square(x):
    return x ** 2

# Композиция
def compose(*functions):
    """Применить функции последовательно."""
    def combined(x):
        result = x
        for func in functions:
            result = func(result)
        return result
    return combined

# Создать pipeline
pipeline = compose(double, add_ten, square)

print(pipeline(5))  # 5 → 10 (double) → 20 (add_ten) → 400 (square)
```

---

## Pure vs Impure — сравнение

### Задача: увеличить все числа на 10

**Нечистый способ:**
```python
def add_ten_impure(numbers):
    for i in range(len(numbers)):
        numbers[i] += 10  # Меняет оригинал!
    return numbers

nums = [1, 2, 3]
result = add_ten_impure(nums)
print(nums)    # [11, 12, 13]  ← изменился!
print(result)  # [11, 12, 13]
```

**Чистый способ:**
```python
def add_ten_pure(numbers):
    return [n + 10 for n in numbers]

nums = [1, 2, 3]
result = add_ten_pure(nums)
print(nums)    # [1, 2, 3]     ← не изменился!
print(result)  # [11, 12, 13]
```

---

## Частые ошибки

### Ошибка 1: Изменение аргумента напрямую
```python
# ❌ НЕЧИСТАЯ
def add_item_impure(items, new_item):
    items.append(new_item)
    return items

# ✅ ЧИСТАЯ
def add_item_pure(items, new_item):
    return items + [new_item]
```

### Ошибка 2: Использование времени/случайности
```python
import time
import random

# ❌ НЕЧИСТАЯ (результат зависит от времени)
def get_timestamp_impure():
    return time.time()

# ❌ НЕЧИСТАЯ (результат случайный)
def shuffle_impure(items):
    random.shuffle(items)
    return items

# ✅ ЧИСТАЯ (передаём значение извне)
def format_timestamp_pure(timestamp):
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))
```

### Ошибка 3: Скрытое изменение состояния
```python
class Counter:
    def __init__(self):
        self.count = 0

    # ❌ НЕЧИСТАЯ (меняет объект)
    def increment_impure(self):
        self.count += 1
        return self.count

    # ✅ ЧИСТАЯ (возвращает новое значение)
    def increment_pure(self, current_count):
        return current_count + 1
```

---

## Когда НЕ нужны Pure Functions?

Pure functions — отлично, но не всегда возможно!

### Когда нечистота неизбежна:
- 📁 **Работа с файлами** — чтение/запись это side effect
- 🖥️ **Работа с БД** — запросы меняют состояние
- 🖨️ **Вывод на экран** — `print()` это side effect
- 🌐 **Сетевые запросы** — API вызовы нечистые
- ⏰ **Работа со временем** — `time.time()` всегда разный

### Решение: изолировать нечистоту
```python
# ❌ Смешано: чистое + нечистое
def process_and_save_impure(data):
    processed = [x * 2 for x in data]  # Чистое
    with open("result.txt", "w") as f:  # Нечистое
        f.write(str(processed))
    return processed

# ✅ Разделить: чистое отдельно, нечистое отдельно
def process_pure(data):
    """Чистая обработка."""
    return [x * 2 for x in data]

def save_to_file(data, filename):
    """Нечистое I/O отдельно."""
    with open(filename, "w") as f:
        f.write(str(data))

# Использование
data = [1, 2, 3]
processed = process_pure(data)  # Чистое
save_to_file(processed, "result.txt")  # Нечистое
```

---

## Резюме

### Pure Function — это функция, которая:
- ✅ Одинаковые аргументы → одинаковый результат
- ✅ Не меняет внешнее состояние
- ✅ Не читает глобальные переменные
- ✅ Не имеет побочных эффектов (I/O, print)

### Преимущества:
- 🎯 Предсказуемость
- 🧪 Легко тестировать
- 🔄 Можно кэшировать
- ⚡ Безопасный параллелизм
- 🧩 Композиция функций

### Как сделать функцию чистой:
```python
# Передавать состояние как аргумент
def add_points(current_score, points):
    return current_score + points

# Возвращать новые данные, не менять старые
def update_list(items, new_item):
    return items + [new_item]

# Изолировать нечистые операции
processed = process_pure(data)  # Чистая
save_to_file(processed)  # Нечистая отдельно
```

---

## Что дальше?

Теперь ты знаешь Pure Functions! 🎉

**Следующие темы:**
- Data pipelines — цепочки чистых функций
- Function composition — комбинирование функций
- Immutability — неизменяемые данные

Pure functions — основа надёжного кода! 🧼✨
