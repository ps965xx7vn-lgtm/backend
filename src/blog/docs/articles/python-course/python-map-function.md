# map() — Преобразуй всё разом! 🔄

## Что такое map()?

**map()** применяет функцию к **каждому элементу** списка и возвращает результаты.

### Без map() (старый способ):
```python
numbers = [1, 2, 3, 4, 5]
doubled = []

for num in numbers:
    doubled.append(num * 2)

print(doubled)  # [2, 4, 6, 8, 10]
```

### С map() (элегантно!):
```python
numbers = [1, 2, 3, 4, 5]

doubled = list(map(lambda x: x * 2, numbers))

print(doubled)  # [2, 4, 6, 8, 10]
```

**Одна строка вместо цикла!** 🚀

---

## Синтаксис map()

```python
map(функция, итерируемый_объект)
```

**Параметры:**
- `функция` — что применить к каждому элементу
- `итерируемый_объект` — список, кортеж, строка и т.д.

**Возвращает:** Объект map (нужно превратить в list)

```python
result = map(func, data)  # map объект
result_list = list(map(func, data))  # список
```

---

## Базовые примеры

### 1. Умножение на 2
```python
numbers = [1, 2, 3, 4, 5]

# С lambda
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)  # [2, 4, 6, 8, 10]

# С обычной функцией
def double(x):
    return x * 2

doubled2 = list(map(double, numbers))
print(doubled2)  # [2, 4, 6, 8, 10]
```

### 2. Возведение в квадрат
```python
numbers = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x ** 2, numbers))
print(squares)  # [1, 4, 9, 16, 25]
```

### 3. Преобразование типов
```python
#String to int
strings = ["1", "2", "3", "4", "5"]
numbers = list(map(int, strings))
print(numbers)  # [1, 2, 3, 4, 5]

# Int to string
numbers = [10, 20, 30]
strings = list(map(str, numbers))
print(strings)  # ['10', '20', '30']

# Float to int
floats = [1.5, 2.7, 3.9]
integers = list(map(int, floats))
print(integers)  # [1, 2, 3] (отбрасывает дробную часть!)
```

---

## map() со строками

### Преобразование строк
```python
words = ["python", "javascript", "go"]

# Заглавные буквы
upper_words = list(map(str.upper, words))
print(upper_words)  # ['PYTHON', 'JAVASCRIPT', 'GO']

# Длины слов
lengths = list(map(len, words))
print(lengths)  # [6, 10, 2]

# Первая буква
first_letters = list(map(lambda w: w[0], words))
print(first_letters)  # ['p', 'j', 'g']
```

### Форматирование
```python
names = ["алиса", "боб", "карл"]

# Capitalize
capitalized = list(map(str.capitalize, names))
print(capitalized)  # ['Алиса', 'Боб', 'Карл']

# Добавить префикс
with_prefix = list(map(lambda n: f"Студент: {n}", names))
print(with_prefix)  # ['Студент: алиса', 'Студент: боб', 'Студент: карл']
```

---

## map() со словарями

### Извлечение значений
```python
students = [
    {"name": "Алиса", "grade": 95},
    {"name": "Боб", "grade": 87},
    {"name": "Карл", "grade": 92}
]

# Извлечь имена
names = list(map(lambda s: s["name"], students))
print(names)  # ['Алиса', 'Боб', 'Карл']

# Извлечь оценки
grades = list(map(lambda s: s["grade"], students))
print(grades)  # [95, 87, 92]
```

### Преобразование структуры
```python
students = [
    {"name": "Алиса", "grade": 95},
    {"name": "Боб", "grade": 87}
]

# Добавить статус
with_status = list(map(
    lambda s: {**s, "status": "Отличник" if s["grade"] >= 90 else "Хорошист"},
    students
))

print(with_status)
# [
#   {"name": "Алиса", "grade": 95, "status": "Отличник"},
#   {"name": "Боб", "grade": 87, "status": "Хорошист"}
# ]
```

---

## map() с несколькими списками

map() может принимать **несколько списков**!

```python
numbers1 = [1, 2, 3]
numbers2 = [10, 20, 30]

# Сложение элементов
sums = list(map(lambda x, y: x + y, numbers1, numbers2))
print(sums)  # [11, 22, 33]

# Умножение
products = list(map(lambda x, y: x * y, numbers1, numbers2))
print(products)  # [10, 40, 90]
```

**Внимание:** Если списки разной длины, map() остановится на коротком!

```python
short = [1, 2]
long = [10, 20, 30, 40]

result = list(map(lambda x, y: x + y, short, long))
print(result)  # [11, 22] (только 2 элемента!)
```

---

## Практические примеры

### Пример 1: Нормализация данных
```python
# Данные 0-1, нужно 0-100
data = [0.1, 0.5, 0.75, 0.9]

normalized = list(map(lambda x: x * 100, data))
print(normalized)  # [10.0, 50.0, 75.0, 90.0]

# Округление
rounded = list(map(lambda x: round(x * 100), data))
print(rounded)  # [10, 50, 75, 90]
```

### Пример 2: Обработка цен
```python
prices = [100, 200, 150, 300]

# Применить скидку 20%
discounted = list(map(lambda p: p * 0.8, prices))
print(discounted)  # [80.0, 160.0, 120.0, 240.0]

# Добавить налог 10%
with_tax = list(map(lambda p: p * 1.1, prices))
print(with_tax)  # [110.0, 220.0, 165.0, 330.0]
```

### Пример 3: Создание URL
```python
products = ["phone", "laptop", "mouse"]

# Создать URL для каждого
urls = list(map(lambda p: f"https://shop.com/products/{p}", products))

for url in urls:
    print(url)
# https://shop.com/products/phone
# https://shop.com/products/laptop
# https://shop.com/products/mouse
```

---

## map() vs List Comprehension

Оба делают то же самое!

```python
numbers = [1, 2, 3, 4, 5]

# map()
doubled_map = list(map(lambda x: x * 2, numbers))

# List comprehension
doubled_comp = [x * 2 for x in numbers]

print(doubled_map == doubled_comp)  # True
```

### Когда что использовать?

**map() — когда:**
- ✅ Уже есть готовая функция
- ✅ Простое преобразование
- ✅ Нужна функциональная парадигма

```python
# map удобнее
numbers = ["1", "2", "3"]
integers = list(map(int, numbers))
```

**List comprehension — когда:**
- ✅ Нужно условие (if)
- ✅ Сложная логика
- ✅ Pythonic style

```python
# Comprehension удобнее
numbers = [1, 2, 3, 4, 5]
even_doubled = [x * 2 for x in numbers if x % 2 == 0]
```

---

## Цепочки map()

Можно применять map() несколько раз!

```python
numbers = [1, 2, 3, 4, 5]

# Умножить на 2, потом возвести в квадрат
result = list(map(lambda x: x ** 2, map(lambda x: x * 2, numbers)))
print(result)  # [4, 16, 36, 64, 100]

# Читается справа налево:
# 1. Умножаем на 2: [2, 4, 6, 8, 10]
# 2. Возводим в квадрат: [4, 16, 36, 64, 100]
```

**Но лучше так:**
```python
# Понятнее и проще!
doubled = list(map(lambda x: x * 2, numbers))
squared = list(map(lambda x: x ** 2, doubled))
print(squared)  # [4, 16, 36, 64, 100]
```

---

## Распространённые ошибки

### Ошибка 1: Забыли list()
```python
numbers = [1, 2, 3]

result = map(lambda x: x * 2, numbers)
print(result)  # <map object at 0x...>  ← НЕ список!

# ✅ ПРАВИЛЬНО
result = list(map(lambda x: x * 2, numbers))
print(result)  # [2, 4, 6]
```

### Ошибка 2: Функция не возвращает значение
```python
def double_bad(x):
    x * 2  # Забыли return!

result = list(map(double_bad, [1, 2, 3]))
print(result)  # [None, None, None]  ← Ошибка!

# ✅ ПРАВИЛЬНО
def double_good(x):
    return x * 2

result = list(map(double_good, [1, 2, 3]))
print(result)  # [2, 4, 6]
```

### Ошибка 3: Изменение исходного списка
```python
# map НЕ изменяет исходный список!
numbers = [1, 2, 3]
doubled = list(map(lambda x: x * 2, numbers))

print(numbers)  # [1, 2, 3]  ← НЕ изменился!
print(doubled)  # [2, 4, 6]  ← Новый список
```

---

## Производительность

map() быстрее цикла for на больших данных!

```python
import time

data = list(range(1000000))  # Миллион чисел

# С циклом for
start = time.time()
result1 = []
for x in data:
    result1.append(x * 2)
time_for = time.time() - start

# С map
start = time.time()
result2 = list(map(lambda x: x * 2, data))
time_map = time.time() - start

print(f"For: {time_for:.4f}s")
print(f"Map: {time_map:.4f}s")
# Map обычно быстрее на 10-30%!
```

---

## Комбинация с другими функциями

### map + filter
```python
numbers = [1, 2, 3, 4, 5, 6]

# Удвоить чётные числа
result = list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, numbers)))
print(result)  # [4, 8, 12]
```

### map + sorted
```python
words = ["python", "go", "javascript"]

# Отсортировать по длине, потом заглавные
result = list(map(str.upper, sorted(words, key=len)))
print(result)  # ['GO', 'PYTHON', 'JAVASCRIPT']
```

### map + reduce
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Удвоить, потом сумма
doubled = map(lambda x: x * 2, numbers)
total = reduce(lambda acc, x: acc + x, doubled, 0)
print(total)  # 30
```

---

## Резюме

### map() — это:
- ✅ Применить функцию к каждому элементу
- ✅ Возвращает новый список
- ✅ НЕ изменяет исходный список
- ✅ Быстрее цикла for
- ✅ Функциональный стиль

### Синтаксис:
```python
list(map(функция, данные))
```

### Типичное использование:
```python
# Преобразование типов
list(map(int, ["1", "2", "3"]))

# С lambda
list(map(lambda x: x * 2, numbers))

# С готовой функцией
list(map(str.upper, words))

# Несколько списков
list(map(lambda x, y: x + y, list1, list2))
```

---

## Что дальше?

Теперь ты знаешь map()! 🎉

**Следующие темы:**
- `filter()` — отобрать элементы по условию
- `reduce()` — свернуть список в одно значение
- List comprehensions — альтернатива map

map() — основа функционального программирования! 🚀
