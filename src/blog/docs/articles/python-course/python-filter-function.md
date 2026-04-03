# filter() — Отбери лучшее! 🔍

## Что такое filter()?

**filter()** отбирает элементы, которые **проходят проверку** (возвращают True).

### Без filter() (старый способ):
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even = []

for num in numbers:
    if num % 2 == 0:
        even.append(num)

print(even)  # [2, 4, 6, 8, 10]
```

### С filter() (элегантно!):
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

even = list(filter(lambda x: x % 2 == 0, numbers))

print(even)  # [2, 4, 6, 8, 10]
```

**Одна строка вместо цикла!** 🚀

---

## Синтаксис filter()

```python
filter(функция_проверки, итерируемый_объект)
```

**Параметры:**
- `функция_проверки` — должна возвращать True/False
- `итерируемый_объект` — список, кортеж, строка и т.д.

**Возвращает:** Объект filter (нужно превратить в list)

```python
result = filter(func, data)  # filter объект
result_list = list(filter(func, data))  # список
```

---

## Базовые примеры

### 1. Чётные числа
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4, 6, 8, 10]
```

### 2. Нечётные числа
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

odd = list(filter(lambda x: x % 2 != 0, numbers))
print(odd)  # [1, 3, 5, 7, 9]
```

### 3. Больше порога
```python
numbers = [5, 12, 3, 18, 25, 7]

above_10 = list(filter(lambda x: x > 10, numbers))
print(above_10)  # [12, 18, 25]
```

### 4. С обычной функцией
```python
def is_positive(x):
    return x > 0

numbers = [-5, 2, -3, 8, 0, -1, 10]

positive = list(filter(is_positive, numbers))
print(positive)  # [2, 8, 10]
```

---

## filter() со строками

### Фильтрация по длине
```python
words = ["кот", "собака", "мышь", "слон", "кенгуру"]

# Слова длиннее 4 символов
long_words = list(filter(lambda w: len(w) > 4, words))
print(long_words)  # ['собака', 'кенгуру']

# Короткие слова
short_words = list(filter(lambda w: len(w) <= 4, words))
print(short_words)  # ['кот', 'мышь', 'слон']
```

### Фильтрация по содержанию
```python
words = ["python", "javascript", "go", "java", "typescript"]

# Содержат "script"
with_script = list(filter(lambda w: "script" in w, words))
print(with_script)  # ['javascript', 'typescript']

# Начинаются с "j"
starts_j = list(filter(lambda w: w.startswith("j"), words))
print(starts_j)  # ['javascript', 'java']
```

### Удаление пустых строк
```python
data = ["Алиса", "", "Боб", "  ", "Карл", ""]

# Убрать пустые
non_empty = list(filter(lambda s: s.strip(), data))
print(non_empty)  # ['Алиса', 'Боб', 'Карл']

# ИЛИ просто None (без lambda!)
non_empty2 = list(filter(None, data))
print(non_empty2)  # ['Алиса', 'Боб', '  ', 'Карл']  ← Пробелы остались!
```

**filter(None, ...)** убирает только False, None, 0, пустые строки "". Строка с пробелами " " - это True!

---

## filter() со словарями

### Фильтрация списка словарей
```python
students = [
    {"name": "Алиса", "grade": 95},
    {"name": "Боб", "grade": 67},
    {"name": "Карл", "grade": 88},
    {"name": "Дима", "grade": 72}
]

# Оценка >= 80
high_performers = list(filter(lambda s: s["grade"] >= 80, students))
print(high_performers)
# [{"name": "Алиса", "grade": 95}, {"name": "Карл", "grade": 88}]

# Провалили (< 70)
failed = list(filter(lambda s: s["grade"] < 70, students))
print(failed)
# [{"name": "Боб", "grade": 67}]
```

### Фильтрация ключей словаря
```python
data = {"name": "Алиса", "age": 25, "city": "Москва", "score": 0}

# Убрать ключи с пустыми значениями
filtered_keys = list(filter(lambda k: data[k], data.keys()))
print(filtered_keys)  # ['name', 'age', 'city']  ← score=0 убран!

# Создать новый словарь
clean_data = {k: data[k] for k in filtered_keys}
print(clean_data)  # {'name': 'Алиса', 'age': 25, 'city': 'Москва'}
```

---

## Множественные условия

### AND (и)
```python
numbers = [5, 12, 3, 18, 25, 7, 30]

# Чётные И > 10
result = list(filter(lambda x: x % 2 == 0 and x > 10, numbers))
print(result)  # [12, 18, 30]
```

### OR (или)
```python
numbers = [5, 12, 3, 18, 25, 7, 30]

# < 10 ИЛИ > 20
result = list(filter(lambda x: x < 10 or x > 20, numbers))
print(result)  # [5, 3, 25, 7, 30]
```

### Сложные условия
```python
products = [
    {"name": "Телефон", "price": 500, "in_stock": True},
    {"name": "Ноутбук", "price": 1200, "in_stock": False},
    {"name": "Мышь", "price": 25, "in_stock": True},
    {"name": "Монитор", "price": 300, "in_stock": True}
]

# В наличии И цена < 600
affordable = list(filter(
    lambda p: p["in_stock"] and p["price"] < 600,
    products
))

for p in affordable:
    print(f"{p['name']}: ${p['price']}")
# Телефон: $500
# Мышь: $25
# Монитор: $300
```

---

## Практические примеры

### Пример 1: Фильтрация email
```python
emails = [
    "alice@gmail.com",
    "bob@yahoo.com",
    "invalid-email",
    "charlie@gmail.com",
    "dave@hotmail.com"
]

# Только Gmail
gmail_only = list(filter(lambda e: e.endswith("@gmail.com"), emails))
print(gmail_only)  # ['alice@gmail.com', 'charlie@gmail.com']

# С правильным @
valid_emails = list(filter(lambda e: "@" in e and "." in e, emails))
print(valid_emails)  # Все кроме 'invalid-email'
```

### Пример 2: Фильтрация файлов
```python
files = [
    "image1.jpg",
    "document.pdf",
    "photo.png",
    "script.py",
    "data.csv",
    "picture.jpg"
]

# Только изображения
images = list(filter(
    lambda f: f.endswith(".jpg") or f.endswith(".png"),
    files
))
print(images)  # ['image1.jpg', 'photo.png', 'picture.jpg']

# Python файлы
python_files = list(filter(lambda f: f.endswith(".py"), files))
print(python_files)  # ['script.py']
```

### Пример 3: Очистка данных
```python
raw_data = [0, 5, None, 12, "", False, 25, [], 30]

# Убрать "ложные" значения (0, None, "", False, [])
clean_data = list(filter(None, raw_data))
print(clean_data)  # [5, 12, 25, 30]

# Только числа > 0
numbers_only = list(filter(lambda x: isinstance(x, (int, float)) and x > 0, raw_data))
print(numbers_only)  # [5, 12, 25, 30]
```

---

## filter() vs List Comprehension

Оба делают то же самое!

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# filter()
even_filter = list(filter(lambda x: x % 2 == 0, numbers))

# List comprehension
even_comp = [x for x in numbers if x % 2 == 0]

print(even_filter == even_comp)  # True
```

### Когда что использовать?

**filter() — когда:**
- ✅ Уже есть готовая функция-проверка
- ✅ Простое условие
- ✅ Функциональная парадигма

```python
def is_adult(person):
    return person["age"] >= 18

adults = list(filter(is_adult, people))
```

**List comprehension — когда:**
- ✅ Сложное условие
- ✅ Нужно также преобразовать данные
- ✅ Pythonic style

```python
# Comprehension удобнее
adult_names = [p["name"] for p in people if p["age"] >= 18]
```

---

## Комбинация filter + map

filter → map: сначала отбор, потом преобразование.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Чётные → удвоить
even = filter(lambda x: x % 2 == 0, numbers)
doubled = list(map(lambda x: x * 2, even))
print(doubled)  # [4, 8, 12, 16, 20]

# ИЛИ одной строкой
result = list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, numbers)))
print(result)  # [4, 8, 12, 16, 20]
```

map → filter: сначала преобразование, потом отбор.

```python
words = ["python", "go", "javascript", "c"]

# Заглавные → длина > 2
upper = map(str.upper, words)
long_words = list(filter(lambda w: len(w) > 2, upper))
print(long_words)  # ['PYTHON', 'JAVASCRIPT']
```

---

## filter(None, ...) — особый случай

**filter(None, data)** убирает "ложные" значения без lambda!

```python
data = [0, 1, False, True, None, "text", "", "  ", [], [1, 2]]

filtered = list(filter(None, data))
print(filtered)  # [1, True, 'text', '  ', [1, 2]]
```

**Что считается "ложным":**
- ❌ `None`
- ❌ `False`
- ❌ `0`, `0.0`
- ❌ Пустые: `""`, `[]`, `{}`, `()`
- ✅ Всё остальное — True

**Полезно для:**
```python
# Убрать пустые строки
lines = ["Строка 1", "", "Строка 2", None, "Строка 3"]
non_empty = list(filter(None, lines))
print(non_empty)  # ['Строка 1', 'Строка 2', 'Строка 3']

# Убрать нулевые значения
scores = [100, 0, 85, None, 92, 0]
valid_scores = list(filter(None, scores))
print(valid_scores)  # [100, 85, 92]
```

---

## Распространённые ошибки

### Ошибка 1: Забыли list()
```python
numbers = [1, 2, 3, 4, 5]

result = filter(lambda x: x > 2, numbers)
print(result)  # <filter object at 0x...>  ← НЕ список!

# ✅ ПРАВИЛЬНО
result = list(filter(lambda x: x > 2, numbers))
print(result)  # [3, 4, 5]
```

### Ошибка 2: Функция не возвращает True/False
```python
def check_bad(x):
    x > 5  # Забыли return!

result = list(filter(check_bad, [1, 6, 3, 8]))
print(result)  # []  ← Пусто, потому что функция возвращает None!

# ✅ ПРАВИЛЬНО
def check_good(x):
    return x > 5

result = list(filter(check_good, [1, 6, 3, 8]))
print(result)  # [6, 8]
```

### Ошибка 3: Изменение исходного списка
```python
# filter НЕ изменяет исходный список!
numbers = [1, 2, 3, 4, 5]
filtered = list(filter(lambda x: x > 2, numbers))

print(numbers)  # [1, 2, 3, 4, 5]  ← НЕ изменился!
print(filtered)  # [3, 4, 5]  ← Новый список
```

### Ошибка 4: filter(None) не всегда работает как ожидается
```python
data = [0, 5, 10, 15]

# filter(None) уберёт 0!
result = list(filter(None, data))
print(result)  # [5, 10, 15]  ← 0 пропал!

# Если 0 — валидное значение, используй lambda
result = list(filter(lambda x: x is not None, data))
print(result)  # [0, 5, 10, 15]  ← 0 остался
```

---

## Производительность

filter() быстрее цикла for на больших данных!

```python
import time

data = list(range(1000000))  # Миллион чисел

# С циклом for
start = time.time()
result1 = []
for x in data:
    if x % 2 == 0:
        result1.append(x)
time_for = time.time() - start

# С filter
start = time.time()
result2 = list(filter(lambda x: x % 2 == 0, data))
time_filter = time.time() - start

print(f"For: {time_for:.4f}s")
print(f"Filter: {time_filter:.4f}s")
# Filter обычно быстрее на 10-20%!
```

---

## Резюме

### filter() — это:
- ✅ Отобрать элементы по условию
- ✅ Функция должна возвращать True/False
- ✅ Возвращает новый список
- ✅ НЕ изменяет исходный список
- ✅ Быстрее цикла for

### Синтаксис:
```python
list(filter(функция_проверки, данные))
```

### Типичное использование:
```python
# С lambda
list(filter(lambda x: x > 0, numbers))

# С готовой функцией
list(filter(str.isupper, words))

# Убрать "ложные" значения
list(filter(None, data))

# Комбинация с map
list(map(str.upper, filter(lambda w: len(w) > 3, words)))
```

---

## Что дальше?

Теперь ты знаешь filter()! 🎉

**Следующие темы:**
- `reduce()` — свернуть список в одно значение
- List comprehensions с if — альтернатива filter
- `any()` / `all()` — проверка условий

filter() + map() = мощнейший дуэт! 🚀
