# List Comprehensions — Элегантные списки! ✨

## Что такое List Comprehension?

**List comprehension** — это способ создать список в **одну строку** вместо цикла.

### Без comprehension (старый способ):
```python
numbers = [1, 2, 3, 4, 5]
squares = []

for num in numbers:
    squares.append(num ** 2)

print(squares)  # [1, 4, 9, 16, 25]
```

### С comprehension (элегантно!):
```python
numbers = [1, 2, 3, 4, 5]

squares = [num ** 2 for num in numbers]

print(squares)  # [1, 4, 9, 16, 25]
```

**Одна строка вместо цикла!** 🚀

---

## Синтаксис

### Базовый:
```python
[выражение for элемент in список]
```

**Пример:**
```python
# Удвоить каждое число
doubled = [x * 2 for x in [1, 2, 3, 4, 5]]
print(doubled)  # [2, 4, 6, 8, 10]
```

### С условием (if):
```python
[выражение for элемент in список if условие]
```

**Пример:**
```python
# Удвоить только чётные
doubled_even = [x * 2 for x in [1, 2, 3, 4, 5, 6] if x % 2 == 0]
print(doubled_even)  # [4, 8, 12]
```

### С if-else:
```python
[выражение_если_true if условие else выражение_если_false for элемент in список]
```

**Пример:**
```python
# "чет" или "нечет"
labels = ["чет" if x % 2 == 0 else "нечет" for x in [1, 2, 3, 4, 5]]
print(labels)  # ['нечет', 'чет', 'нечет', 'чет', 'нечет']
```

---

## Базовые примеры

### 1. Преобразование каждого элемента
```python
# Возведение в квадрат
squares = [x ** 2 for x in [1, 2, 3, 4, 5]]
print(squares)  # [1, 4, 9, 16, 25]

# Умножение на 10
tens = [x * 10 for x in [1, 2, 3]]
print(tens)  # [10, 20, 30]
```

### 2. Преобразование типов
```python
# Строки в числа
strings = ["1", "2", "3", "4", "5"]
numbers = [int(s) for s in strings]
print(numbers)  # [1, 2, 3, 4, 5]

# Числа в строки
numbers = [10, 20, 30]
strings = [str(n) for n in numbers]
print(strings)  # ['10', '20', '30']
```

### 3. Фильтрация с if
```python
# Только чётные
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even = [x for x in numbers if x % 2 == 0]
print(even)  # [2, 4, 6, 8, 10]

# Только положительные
numbers = [-5, 2, -3, 8, 0, -1, 10]
positive = [x for x in numbers if x > 0]
print(positive)  # [2, 8, 10]
```

### 4. Фильтрация + преобразование
```python
# Удвоить только чётные
numbers = [1, 2, 3, 4, 5, 6]
doubled_even = [x * 2 for x in numbers if x % 2 == 0]
print(doubled_even)  # [4, 8, 12]

# Квадраты чисел > 5
numbers = [2, 5, 7, 3, 8, 4]
big_squares = [x ** 2 for x in numbers if x > 5]
print(big_squares)  # [49, 64]
```

---

## Comprehension со строками

### Преобразование строк
```python
words = ["python", "javascript", "go"]

# Заглавные буквы
upper = [word.upper() for word in words]
print(upper)  # ['PYTHON', 'JAVASCRIPT', 'GO']

# Длины слов
lengths = [len(word) for word in words]
print(lengths)  # [6, 10, 2]

# Первые буквы
first_letters = [word[0] for word in words]
print(first_letters)  # ['p', 'j', 'g']
```

### Работа с символами
```python
text = "Python"

# Список символов
chars = [char for char in text]
print(chars)  # ['P', 'y', 't', 'h', 'o', 'n']

# Только гласные
vowels = [char for char in text.lower() if char in 'aeiou']
print(vowels)  # ['o']

# Коды символов
codes = [ord(char) for char in "ABC"]
print(codes)  # [65, 66, 67]
```

### Фильтрация строк
```python
words = ["кот", "собака", "мышь", "слон", "кенгуру"]

# Длинные слова (> 4)
long_words = [word for word in words if len(word) > 4]
print(long_words)  # ['собака', 'кенгуру']

# Слова с буквой "о"
with_o = [word for word in words if "о" in word]
print(with_o)  # ['кот', 'собака', 'слон']
```

---

## Comprehension со словарями

### Извлечение из словарей
```python
students = [
    {"name": "Алиса", "grade": 95},
    {"name": "Боб", "grade": 87},
    {"name": "Карл", "grade": 92}
]

# Имена
names = [s["name"] for s in students]
print(names)  # ['Алиса', 'Боб', 'Карл']

# Оценки
grades = [s["grade"] for s in students]
print(grades)  # [95, 87, 92]

# Отличники (>= 90)
high_achievers = [s["name"] for s in students if s["grade"] >= 90]
print(high_achievers)  # ['Алиса', 'Карл']
```

### Создание словарей из списков
```python
names = ["Алиса", "Боб", "Карл"]
scores = [95, 87, 92]

# Объединить в словари
students = [{"name": name, "score": score} for name, score in zip(names, scores)]
print(students)
# [{'name': 'Алиса', 'score': 95}, {'name': 'Боб', 'score': 87}, ...]
```

---

## if-else в Comprehension

### Базовый if-else
```python
numbers = [1, 2, 3, 4, 5, 6]

# "чет" или "нечет"
labels = ["чет" if x % 2 == 0 else "нечет" for x in numbers]
print(labels)  # ['нечет', 'чет', 'нечет', 'чет', 'нечет', 'чет']

# Заменить отрицательные на 0
numbers = [-5, 3, -2, 8, -1, 10]
non_negative = [x if x >= 0 else 0 for x in numbers]
print(non_negative)  # [0, 3, 0, 8, 0, 10]
```

### Множественные условия
```python
numbers = [5, 12, 3, 18, 25, 7, 30]

# Категории: малое/среднее/большое
categories = [
    "малое" if x < 10
    else "среднее" if x < 20
    else "большое"
    for x in numbers
]
print(categories)
# ['малое', 'среднее', 'малое', 'среднее', 'большое', 'малое', 'большое']
```

---

## Вложенные циклы

### Две вложенности
```python
# Таблица умножения
table = [x * y for x in range(1, 4) for y in range(1, 4)]
print(table)  # [1, 2, 3, 2, 4, 6, 3, 6, 9]

# Понятнее:
for x in range(1, 4):
    for y in range(1, 4):
        table.append(x * y)
```

### Создание пар
```python
# Все пары (координаты)
pairs = [(x, y) for x in [1, 2, 3] for y in ['a', 'b']]
print(pairs)
# [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b'), (3, 'a'), (3, 'b')]
```

### С условием
```python
# Только пары где x < y
pairs = [(x, y) for x in range(1, 6) for y in range(1, 6) if x < y]
print(pairs)
# [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), ...]
```

---

## Практические примеры

### Пример 1: Фильтрация даннных
```python
data = [
    {"name": "Телефон", "price": 500, "in_stock": True},
    {"name": "Ноутбук", "price": 1200, "in_stock": False},
    {"name": "Мышь", "price": 25, "in_stock": True},
    {"name": "Монитор", "price": 300, "in_stock": True}
]

# В наличии + доступные (<600)
available = [
    p["name"]
    for p in data
    if p["in_stock"] and p["price"] < 600
]
print(available)  # ['Телефон', 'Мышь', 'Монитор']
```

### Пример 2: Преобразование данных
```python
# Цены с налогом 10%
prices = [100, 200, 150, 300]
with_tax = [round(p * 1.1, 2) for p in prices]
print(with_tax)  # [110.0, 220.0, 165.0, 330.0]

# Скидка 20% на дорогие (>150)
discounted = [p * 0.8 if p > 150 else p for p in prices]
print(discounted)  # [100, 160.0, 150, 240.0]
```

### Пример 3: Сглаживание вложенного списка
```python
nested = [[1, 2, 3], [4, 5], [6, 7, 8]]

# Flatten
flat = [item for sublist in nested for item in sublist]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8]
```

### Пример 4: Очистка данных
```python
# Убрать пустые строки и пробелы
lines = ["  Python  ", "", "  Go", "   ", "Java  "]
clean = [line.strip() for line in lines if line.strip()]
print(clean)  # ['Python', 'Go', 'Java']
```

---

## Comprehension vs map/filter

List comprehension — это альтернатива map и filter!

```python
numbers = [1, 2, 3, 4, 5, 6]

# map + filter
result = list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, numbers)))

# List comprehension (ПРОЩЕ!)
result = [x * 2 for x in numbers if x % 2 == 0]

print(result)  # [4, 8, 12]
```

### Когда использовать comprehension:
- ✅ Pythonic style (рекомендуется!)
- ✅ Более читаемо
- ✅ Не нужен lambda
- ✅ Сложные условия

### Когда использовать map/filter:
- ✅ Уже есть готовая функция
- ✅ Функциональная парадигма
- ✅ Композиция функций

---

## Dict & Set Comprehensions

Не только списки! Есть comprehension для словарей и множеств.

### Dict Comprehension
```python
# Создать словарь
numbers = [1, 2, 3, 4, 5]
squares_dict = {x: x ** 2 for x in numbers}
print(squares_dict)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Поменять ключи и значения
prices = {"apple": 50, "banana": 30, "orange": 40}
reversed_prices = {v: k for k, v in prices.items()}
print(reversed_prices)  # {50: 'apple', 30: 'banana', 40: 'orange'}

# Фильтрация словаря
prices = {"apple": 50, "banana": 30, "orange": 40, "mango": 70}
expensive = {k: v for k, v in prices.items() if v > 40}
print(expensive)  # {'apple': 50, 'mango': 70}
```

### Set Comprehension
```python
# Множество квадратов
numbers = [1, 2, 3, 2, 1, 4, 3]
squares_set = {x ** 2 for x in numbers}
print(squares_set)  # {1, 4, 9, 16}  ← дубликаты убраны!

# Фильтрация
words = ["python", "javascript", "go", "java", "python", "go"]
long_unique = {w for w in words if len(w) > 3}
print(long_unique)  # {'java', 'javascript', 'python'}
```

---

## Производительность

Comprehension быстрее цикла!

```python
import time

data = range(1000000)

# Цикл for
start = time.time()
result1 = []
for x in data:
    result1.append(x * 2)
time_for = time.time() - start

# Comprehension
start = time.time()
result2 = [x * 2 for x in data]
time_comp = time.time() - start

print(f"For loop: {time_for:.4f}s")
print(f"Comprehension: {time_comp:.4f}s")
# Comprehension обычно быстрее на 20-30%!
```

---

## Частые ошибки

### Ошибка 1: Неправильный порядок if-else
```python
# ❌ ОШИБКА
result = [x * 2 for x in [1, 2, 3, 4] if x % 2 == 0 else x]
# SyntaxError!

# ✅ ПРАВИЛЬНО (else ПЕРЕД for)
result = [x * 2 if x % 2 == 0 else x for x in [1, 2, 3, 4]]
print(result)  # [1, 4, 3, 8]
```

### Ошибка 2: Слишком сложная логика
```python
# ❌ ПЛОХО (нечитаемо!)
result = [
    x * 2 if x > 0 else abs(x) if x < -10 else 0
    for x in data
    if x % 2 == 0 or x % 3 == 0
]

# ✅ ЛУЧШЕ обычным циклом если очень сложно!
result = []
for x in data:
    if x % 2 == 0 or x % 3 == 0:
        if x > 0:
            result.append(x * 2)
        elif x < -10:
            result.append(abs(x))
        else:
            result.append(0)
```

### Ошибка 3: Модификация элементов словаря
```python
students = [{"name": "Алиса", "grade": 85}]

# ❌ НЕ ИЗМЕНЯЕТ ОРИГИНАЛ!
updated = [s["grade"] + 10 for s in students]
print(students[0]["grade"])  # 85  ← НЕ изменилась!

# ✅ Если нужно изменить:
for s in students:
    s["grade"] += 10
print(students[0]["grade"])  # 95
```

---

## Когда НЕ использовать Comprehension

### 1. Побочные эффекты
```python
# ❌ ПЛОХО (сайд-эффекты в comprehension)
[print(x) for x in [1, 2, 3]]  # Плохая практика!

# ✅ ХОРОШО (обычный цикл)
for x in [1, 2, 3]:
    print(x)
```

### 2. Очень сложная логика
```python
# ❌ ПЛОХО (слишком сложно)
result = [
    process(transform(validate(x)))
    for x in data
    if check1(x) and check2(x)
]

# ✅ ЛУЧШЕ обычным циклом
result = []
for x in data:
    if check1(x) and check2(x):
        validated = validate(x)
        transformed = transform(validated)
        processed = process(transformed)
        result.append(processed)
```

### 3. Не нужен результат
```python
# ❌ ПЛОХО
_ = [save_to_db(x) for x in data]  # Результат не используем

# ✅ ХОРОШО
for x in data:
    save_to_db(x)
```

---

## Резюме

### List Comprehension — это:
- ✅ Создание списка в одну строку
- ✅ Альтернатива map + filter
- ✅ Pythonic style (рекомендуется!)
- ✅ Быстрее цикла for
- ✅ Читаемый код

### Синтаксис:
```python
# Базовый
[выражение for элемент in список]

# С фильтром
[выражение for элемент in список if условие]

# С if-else
[выражение_если_true if условие else выражение_если_false for элемент in список]

# Dict comprehension
{ключ: значение for элемент in список}

# Set comprehension
{выражение for элемент in список}
```

### Типичное использование:
```python
# Преобразование
[x * 2 for x in numbers]

# Фильтрация
[x for x in numbers if x > 0]

# Фильтрация + преобразование
[x ** 2 for x in numbers if x % 2 == 0]

# Вложенные циклы
[x * y for x in range(3) for y in range(3)]
```

---

## Что дальше?

Теперь ты знаешь List Comprehension! 🎉

**Следующие темы:**
- Generator expressions — ленивые comprehension
- Pure functions — функции без побочных эффектов
- Pipeline — цепочки преобразований

List comprehension — самый Pythonic способ работать со списками! 🐍✨
