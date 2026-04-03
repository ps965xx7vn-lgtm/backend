# Lambda функции: Маленькие умные функции ⚡

## Что такое Lambda?

**Lambda** — это способ создать **маленькую функцию в одну строку** без имени.

### Обычная функция:
```python
def double(x):
    return x * 2

result = double(5)  # 10
```

### Lambda функция:
```python
double = lambda x: x * 2

result = double(5)  # 10
```

**Та же функция, но короче!** ⚡

---

## Синтаксис Lambda

```python
lambda аргументы: выражение
```

**Части:**
- `lambda` — ключевое слово
- `аргументы` — параметры (как в def)
- `:` — разделитель
- `выражение` — что вернуть (ОДНА строка!)

---

## Примеры Lambda

### 1. Простая арифметика
```python
# Сложение
add = lambda a, b: a + b
print(add(3, 5))  # 8

# Квадрат числа
square = lambda x: x ** 2
print(square(4))  # 16

# Проверка чётности
is_even = lambda n: n % 2 == 0
print(is_even(10))  # True
print(is_even(7))   # False
```

### 2. Со строками
```python
# Приветствие
greet = lambda name: f"Привет, {name}!"
print(greet("Алиса"))  # Привет, Алиса!

# Длина строки
length = lambda s: len(s)
print(length("Python"))  # 6
```

### 3. С условиями
```python
# Максимум из двух
max_num = lambda a, b: a if a > b else b
print(max_num(10, 20))  # 20

# Положительное или нет
sign = lambda x: "+" if x >= 0 else "-"
print(sign(5))   # +
print(sign(-3))  # -
```

---

## Когда использовать Lambda?

### ✅ Хорошо использовать:

**1. Внутри других функций:**
```python
numbers = [1, 2, 3, 4, 5]

# sorted с lambda
sorted_desc = sorted(numbers, key=lambda x: -x)
print(sorted_desc)  # [5, 4, 3, 2, 1]

# map с lambda (скоро изучим!)
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)  # [2, 4, 6, 8, 10]
```

**2. Простые преобразования:**
```python
students = [
    {"name": "Алиса", "grade": 95},
    {"name": "Боб", "grade": 87},
    {"name": "Карл", "grade": 92}
]

# Сортировка по оценке
sorted_students = sorted(students, key=lambda s: s["grade"], reverse=True)
print(sorted_students[0]["name"])  # Алиса
```

**3. Генерация данных:**
```python
import random

# Lambda для случайных чисел
random_point = lambda: random.randint(0, 100)

points = [random_point() for _ in range(5)]
print(points)  # [42, 17, 89, 5, 63] (случайные!)
```

### ❌ Плохо использовать:

**1. Сложная логика:**
```python
# ❌ ПЛОХО - слишком сложно
check = lambda x: x > 0 and x < 100 and x % 2 == 0 and str(x)[0] != "5"

# ✅ ХОРОШО - обычная функция
def check_number(x):
    """Проверить число по критериям."""
    if x <= 0 or x >= 100:
        return False
    if x % 2 != 0:
        return False
    if str(x)[0] == "5":
        return False
    return True
```

**2. Нужен docstring:**
```python
# ❌ ПЛОХО - нельзя добавить описание
calculate = lambda x, y, z: (x + y) * z / 2

# ✅ ХОРОШО - с документацией
def calculate_formula(x, y, z):
    """
    Вычислить по формуле: (x + y) * z / 2

    Args:
        x, y, z: Числа для расчёта

    Returns:
        float: Результат формулы
    """
    return (x + y) * z / 2
```

---

## Lambda vs Обычная функция

| Критерий | Lambda | Def |
|----------|--------|-----|
| **Длина** | Одна строка | Много строк OK |
| **Имя** | Анонимная (без имени) | Обязательно имя |
| **Docstring** | ❌ Нельзя | ✅ Можно |
| **Сложность** | Простые операции | Любая сложность |
| **Использование** | Внутри других функций | Везде |

---

## Практические примеры

### Пример 1: Сортировка товаров
```python
products = [
    {"name": "Ноутбук", "price": 50000},
    {"name": "Мышка", "price": 500},
    {"name": "Клавиатура", "price": 3000}
]

# Сортировка по цене
cheap_first = sorted(products, key=lambda p: p["price"])
expensive_first = sorted(products, key=lambda p: p["price"], reverse=True)

print(cheap_first[0]["name"])  # Мышка
print(expensive_first[0]["name"])  # Ноутбук
```

### Пример 2: Фильтрация данных
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Только чётные (скоро изучим filter!)
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4, 6, 8, 10]

# Только > 5
big = list(filter(lambda x: x > 5, numbers))
print(big)  # [6, 7, 8, 9, 10]
```

### Пример 3: Обработка списка словарей
```python
students = [
    {"name": "Алиса", "age": 20, "grade": 95},
    {"name": "Боб", "age": 19, "grade": 87},
    {"name": "Карл", "age": 21, "grade": 92}
]

# Найти студента с максимальной оценкой
best = max(students, key=lambda s: s["grade"])
print(f"Лучший студент: {best['name']} ({best['grade']})")

# Найти самого младшего
youngest = min(students, key=lambda s: s["age"])
print(f"Самый младший: {youngest['name']} ({youngest['age']} лет)")
```

---

## Множественные параметры

Lambda может принимать несколько параметров:

```python
# Два параметра
multiply = lambda x, y: x * y
print(multiply(5, 3))  # 15

# Три параметра
volume = lambda l, w, h: l * w * h
print(volume(2, 3, 4))  # 24

# С значениями по умолчанию (не работает!)
# ❌ power = lambda x, n=2: x ** n  # SyntaxError!

# Для значений по умолчанию используй def:
def power(x, n=2):
    return x ** n
```

---

## Lambda и встроенные функции

### С sorted()
```python
words = ["Python", "JavaScript", "Go", "C++", "Rust"]

# По длине слова
by_length = sorted(words, key=lambda w: len(w))
print(by_length)  # ['Go', 'C++', 'Rust', 'Python', 'JavaScript']

# В обратном алфавитном порядке
reverse_alpha = sorted(words, key=lambda w: w.lower(), reverse=True)
print(reverse_alpha)  # ['Rust', 'Python', 'JavaScript', 'Go', 'C++']
```

### С max() и min()
```python
data = [10, 3, 45, 7, 89, 12]

# Максимальный элемент (можно без lambda)
print(max(data))  # 89

# Максимальный по модулю
numbers = [-50, 10, -30, 5]
max_abs = max(numbers, key=lambda x: abs(x))
print(max_abs)  # -50 (модуль 50 самый большой!)
```

---

## Распространённые ошибки

### Ошибка 1: Много строк
```python
# ❌ ОШИБКА - lambda только ОДНА строка!
calc = lambda x:
    result = x * 2
    return result

# ✅ ПРАВИЛЬНО
calc = lambda x: x * 2
```

### Ошибка 2: Присваивания
```python
# ❌ ОШИБКА - нельзя присваивать в lambda
update = lambda x: x = x + 1  # SyntaxError!

# ✅ ПРАВИЛЬНО - используй обычную функцию
def update(x):
    x = x + 1
    return x
```

### Ошибка 3: Забыли return
```python
# ❌ ПЛОХО
def double(x):
    x * 2  # Забыли return!

result = double(5)
print(result)  # None

# ✅ ХОРОШО - lambda всегда возвращает
double = lambda x: x * 2
result = double(5)
print(result)  # 10
```

---

## Когда НЕ нужна Lambda?

### Не сохраняй в переменную!

```python
# ❌ ПЛОХАЯ практика
double = lambda x: x * 2
square = lambda x: x ** 2
add = lambda a, b: a + b

# ✅ ХОРОШО - используй def
def double(x):
    return x * 2

def square(x):
    return x ** 2

def add(a, b):
    return a + b
```

**Почему?**
- Lambda для **одноразового** использования
- Если сохраняешь → нужно имя → используй `def`!

---

## Резюме

### Lambda — это:
- ✅ Анонимная функция в одну строку
- ✅ Удобна внутри других функций
- ✅ Короткая и чёткая
- ❌ НЕ для сложной логики
- ❌ НЕ для сохранения в переменные

### Синтаксис:
```python
lambda параметры: выражение
```

### Типичное использование:
```python
# Сортировка
sorted(data, key=lambda x: x["field"])

# С map/filter (скоро изучим!)
list(map(lambda x: x * 2, numbers))
list(filter(lambda x: x > 0, numbers))

# Генерация
[lambda_func() for _ in range(10)]
```

---

## Что дальше?

Теперь ты знаешь lambda! 🎉

**Следующие темы:**
- `map()` — применить функцию к списку
- `filter()` — отобрать элементы
- `reduce()` — свернуть список в значение

Lambda — фундамент функционального программирования в Python! 🚀
