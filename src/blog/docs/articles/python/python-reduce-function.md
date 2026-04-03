# reduce() — Сверни всё в одно! 🔽

## Что такое reduce()?

**reduce()** сворачивает список в **одно значение**, применяя функцию последовательно.

### Без reduce() (старый способ):
```python
numbers = [1, 2, 3, 4, 5]

# Сумма всех чисел
total = 0
for num in numbers:
    total = total + num

print(total)  # 15
```

### С reduce() (элегантно!):
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

total = reduce(lambda acc, x: acc + x, numbers)

print(total)  # 15
```

**Одна строка вместо цикла с аккумулятором!** 🚀

---

## Синтаксис reduce()

```python
from functools import reduce

reduce(функция, итерируемый_объект, начальное_значение)
```

**Параметры:**
- `функция` — принимает 2 аргумента: аккумулятор и текущий элемент
- `итерируемый_объект` — список, кортеж и т.д.
- `начальное_значение` — опциональное начальное значение аккумулятора

**Возвращает:** Единственное значение (не список!)

---

## Как работает reduce()?

### Визуализация:
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

result = reduce(lambda acc, x: acc + x, numbers)
```

**Шаг за шагом:**
```
Шаг 1: acc=1, x=2 → 1 + 2 = 3
Шаг 2: acc=3, x=3 → 3 + 3 = 6
Шаг 3: acc=6, x=4 → 6 + 4 = 10
Шаг 4: acc=10, x=5 → 10 + 5 = 15

Результат: 15
```

**Аккумулятор (acc)** — переменная, которая накапливает результат!

---

## Базовые примеры

### 1. Сумма чисел
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

total = reduce(lambda acc, x: acc + x, numbers)
print(total)  # 15

# С начальным значением
total = reduce(lambda acc, x: acc + x, numbers, 10)
print(total)  # 25 (10 + 1 + 2 + 3 + 4 + 5)
```

### 2. Произведение чисел
```python
numbers = [1, 2, 3, 4, 5]

product = reduce(lambda acc, x: acc * x, numbers)
print(product)  # 120 (1 * 2 * 3 * 4 * 5 = факториал!)

# С начальным значением 1
product = reduce(lambda acc, x: acc * x, numbers, 1)
print(product)  # 120
```

### 3. Максимальное число
```python
numbers = [5, 12, 3, 18, 25, 7]

maximum = reduce(lambda acc, x: acc if acc > x else x, numbers)
print(maximum)  # 25
```

### 4. Минимальное число
```python
numbers = [5, 12, 3, 18, 25, 7]

minimum = reduce(lambda acc, x: acc if acc < x else x, numbers)
print(minimum)  # 3
```

---

## reduce() со строками

### Конкатенация строк
```python
words = ["Python", "is", "awesome"]

sentence = reduce(lambda acc, word: acc + " " + word, words)
print(sentence)  # "Python is awesome"

# Лучше с начальным значением
sentence = reduce(lambda acc, word: acc + " " + word, words, "")
print(sentence.strip())  # "Python is awesome" (убрали пробел в начале)
```

### Склеивание с разделителем
```python
words = ["apple", "banana", "orange"]

# С запятыми
result = reduce(lambda acc, word: f"{acc}, {word}", words)
print(result)  # "apple, banana, orange"

# Или просто используй join! (проще)
result = ", ".join(words)
print(result)  # "apple, banana, orange"
```

---

## reduce() со словарями

### Суммирование значений
```python
sales = [
    {"product": "Phone", "revenue": 500},
    {"product": "Laptop", "revenue": 1200},
    {"product": "Mouse", "revenue": 25}
]

total_revenue = reduce(lambda acc, sale: acc + sale["revenue"], sales, 0)
print(total_revenue)  # 1725
```

### Объединение словарей
```python
dicts = [
    {"a": 1},
    {"b": 2},
    {"c": 3}
]

merged = reduce(lambda acc, d: {**acc, **d}, dicts, {})
print(merged)  # {'a': 1, 'b': 2, 'c': 3}
```

### Подсчёт элементов
```python
items = ["apple", "banana", "apple", "orange", "banana", "apple"]

# Подсчитать каждый элемент
count = reduce(
    lambda acc, item: {**acc, item: acc.get(item, 0) + 1},
    items,
    {}
)
print(count)  # {'apple': 3, 'banana': 2, 'orange': 1}
```

---

## Начальное значение (важно!)

### Без начального значения:
```python
numbers = [1, 2, 3, 4, 5]

result = reduce(lambda acc, x: acc + x, numbers)
# acc начинается с первого элемента (1)
print(result)  # 15
```

### С начальным значением:
```python
numbers = [1, 2, 3, 4, 5]

result = reduce(lambda acc, x: acc + x, numbers, 0)
# acc начинается с 0
print(result)  # 15
```

### Когда начальное значение ОБЯЗАТЕЛЬНО?

**1. Пустой список:**
```python
# БЕЗ начального — ОШИБКА!
result = reduce(lambda acc, x: acc + x, [])
# ❌ TypeError: reduce() of empty sequence with no initial value

# С начальным — ОК
result = reduce(lambda acc, x: acc + x, [], 0)
print(result)  # 0
```

**2. Другой тип результата:**
```python
numbers = [1, 2, 3, 4, 5]

# Суммируем в словарь
result = reduce(
    lambda acc, x: {**acc, str(x): x ** 2},
    numbers,
    {}  # ← ОБЯЗАТЕЛЬНО! Результат — словарь
)
print(result)  # {'1': 1, '2': 4, '3': 9, '4': 16, '5': 25}
```

---

## Практические примеры

### Пример 1: Факториал
```python
def factorial(n):
    return reduce(lambda acc, x: acc * x, range(1, n + 1), 1)

print(factorial(5))  # 120 (1 * 2 * 3 * 4 * 5)
print(factorial(0))  # 1 (правильно!)
```

### Пример 2: Сглаживание списка (flatten)
```python
nested = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]

flattened = reduce(lambda acc, lst: acc + lst, nested, [])
print(flattened)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Пример 3: Пайплайн функций
```python
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

def square(x):
    return x ** 2

# Применить все функции последовательно
functions = [add_10, multiply_2, square]
result = reduce(lambda acc, func: func(acc), functions, 5)
# 5 → add_10 → 15 → multiply_2 → 30 → square → 900
print(result)  # 900
```

### Пример 4: Найти самый длинный элемент
```python
words = ["cat", "elephant", "dog", "hippopotamus"]

longest = reduce(
    lambda acc, word: word if len(word) > len(acc) else acc,
    words
)
print(longest)  # "hippopotamus"
```

---

## reduce() vs sum() / max() / min()

Для простых операций есть встроенные функции!

```python
numbers = [1, 2, 3, 4, 5]

# reduce
total = reduce(lambda acc, x: acc + x, numbers)

# sum (ПРОЩЕ!)
total = sum(numbers)

print(total)  # 15
```

### Когда использовать reduce():
- ✅ Сложная логика (не просто сумма/max/min)
- ✅ Нестандартные операции
- ✅ Пайплайн преобразований

### Когда НЕ использовать:
- ❌ Сумма → используй `sum()`
- ❌ Максимум → используй `max()`
- ❌ Минимум → используй `min()`
- ❌ Склеивание строк → используй `"".join()`

---

## reduce() с обычной функцией

Lambda не обязательна! Можно использовать обычную функцию:

```python
def add(acc, x):
    """Функция сложения для reduce."""
    print(f"acc={acc}, x={x}, result={acc + x}")
    return acc + x

numbers = [1, 2, 3, 4, 5]
result = reduce(add, numbers)

# Вывод:
# acc=1, x=2, result=3
# acc=3, x=3, result=6
# acc=6, x=4, result=10
# acc=10, x=5, result=15

print(result)  # 15
```

**Полезно для отладки!**

---

## Комбинация reduce + map + filter

Функциональное программирование в действии!

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Чётные → удвоить → сумма
result = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x * 2, filter(lambda x: x % 2 == 0, numbers)),
    0
)
print(result)  # 60

# Пошагово:
# filter: [2, 4, 6, 8, 10]
# map: [4, 8, 12, 16, 20]
# reduce: 4 + 8 + 12 + 16 + 20 = 60
```

**Читается справа налево!**

---

## Распространённые ошибки

### Ошибка 1: Забыли импортировать
```python
# ❌ ОШИБКА
result = reduce(lambda acc, x: acc + x, [1, 2, 3])
# NameError: name 'reduce' is not defined

# ✅ ПРАВИЛЬНО
from functools import reduce
result = reduce(lambda acc, x: acc + x, [1, 2, 3])
```

### Ошибка 2: Функция не возвращает значение
```python
def add_bad(acc, x):
    acc + x  # Забыли return!

result = reduce(add_bad, [1, 2, 3])
print(result)  # None  ← Ошибка!

# ✅ ПРАВИЛЬНО
def add_good(acc, x):
    return acc + x

result = reduce(add_good, [1, 2, 3])
print(result)  # 6
```

### Ошибка 3: Пустой список без начального значения
```python
# ❌ ОШИБКА
result = reduce(lambda acc, x: acc + x, [])
# TypeError: reduce() of empty sequence with no initial value

# ✅ ПРАВИЛЬНО
result = reduce(lambda acc, x: acc + x, [], 0)
print(result)  # 0
```

### Ошибка 4: Неправильный порядок аргументов
```python
# ❌ ОШИБКА
result = reduce(lambda x, acc: acc + x, [1, 2, 3])
# Порядок важен! Первый аргумент — АККУМУЛЯТОР

# ✅ ПРАВИЛЬНО
result = reduce(lambda acc, x: acc + x, [1, 2, 3])
```

---

## Альтернативы reduce()

### Вместо reduce для суммы:
```python
numbers = [1, 2, 3, 4, 5]

# reduce
total = reduce(lambda acc, x: acc + x, numbers, 0)

# sum (ЛУЧШЕ!)
total = sum(numbers)
```

### Вместо reduce для max:
```python
numbers = [5, 12, 3, 18, 25]

# reduce
maximum = reduce(lambda acc, x: acc if acc > x else x, numbers)

# max (ЛУЧШЕ!)
maximum = max(numbers)
```

### Вместо reduce для сложных случаев:
```python
# reduce
result = reduce(lambda acc, x: {**acc, x: x ** 2}, [1, 2, 3], {})

# dict comprehension (ЛУЧШЕ!)
result = {x: x ** 2 for x in [1, 2, 3]}
```

---

## Производительность

reduce() быстрый, но не всегда самый быстрый!

```python
import time

numbers = list(range(1000000))

# reduce
start = time.time()
result1 = reduce(lambda acc, x: acc + x, numbers, 0)
time_reduce = time.time() - start

# sum (встроенная функция)
start = time.time()
result2 = sum(numbers)
time_sum = time.time() - start

print(f"reduce: {time_reduce:.4f}s")
print(f"sum: {time_sum:.4f}s")
# sum обычно БЫСТРЕЕ в 2-3 раза!
```

**Встроенные функции оптимизированы!**

---

## Резюме

### reduce() — это:
- ✅ Свернуть список в одно значение
- ✅ Использует аккумулятор
- ✅ Применяет функцию последовательно
- ✅ Функция принимает (аккумулятор, элемент)
- ✅ Нужно импортировать: `from functools import reduce`

### Синтаксис:
```python
from functools import reduce

reduce(lambda acc, x: ..., data, initial_value)
```

### Типичное использование:
```python
# Сумма
reduce(lambda acc, x: acc + x, numbers, 0)

# Произведение
reduce(lambda acc, x: acc * x, numbers, 1)

# Максимум
reduce(lambda acc, x: acc if acc > x else x, numbers)

# Объединение
reduce(lambda acc, lst: acc + lst, nested_lists, [])
```

### Когда НЕ использовать:
- ❌ Простая сумма → `sum()`
- ❌ Максимум/минимум → `max()` / `min()`
- ❌ Склеивание строк → `"".join()`

---

## Что дальше?

Теперь ты знаешь reduce()! 🎉

**Следующие темы:**
- List comprehensions — альтернатива map/filter
- Pure functions — функции без побочных эффектов
- Pipeline — цепочка map → filter → reduce

**Святая троица функционального программирования:**
1. `map()` — преобразовать каждый элемент
2. `filter()` — отобрать элементы
3. `reduce()` — свернуть в одно значение

Вместе они — сила! 🚀
