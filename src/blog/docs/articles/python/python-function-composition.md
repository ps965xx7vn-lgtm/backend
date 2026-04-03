# Function Composition — Собери свой LEGO! 🧩

## Что такое Function Composition?

**Function Composition** (Композиция функций) — это комбинирование простых функций в сложные.

### Математика:
```
(f ∘ g)(x) = f(g(x))
```

Читается: **"f после g"** — сначала g, потом f.

### В Python:
```python
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

# Композиция: сначала add_10, potom multiply_2
result = multiply_2(add_10(5))
print(result)  # 30
# 5 → add_10 → 15 → multiply_2 → 30
```

**Функции как кубики LEGO — собираем сложное из простого!** 🧱

---

## Зачем нужна композиция?

### Без композиции (повторение):
```python
# Обработка данных в 3 шага
data1 = step1(raw_data)
data2 = step2(data1)
result = step3(data2)

# Каждый раз повторяем!
data1 = step1(other_data)
data2 = step2(data1)
result = step3(data2)
```

### С композицией (переиспользование):
```python
# Создаём готовый pipeline один раз
process = compose(step1, step2, step3)

# Используем много раз!
result1 = process(raw_data)
result2 = process(other_data)
result3 = process(more_data)
```

---

## Простая функция compose()

```python
def compose(f, g):
    """Композиция двух функций: f(g(x))."""
    def composed(x):
        return f(g(x))
    return composed

# Пример
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

# Создать новую функцию
add_then_multiply = compose(multiply_2, add_10)

print(add_then_multiply(5))  # 30
# 5 → add_10 → 15 → multiply_2 → 30
```

---

## Композиция многих функций

```python
def compose(*functions):
    """Композиция нескольких функций."""
    def composed(x):
        result = x
        for func in reversed(functions):  # Справа налево!
            result = func(result)
        return result
    return composed

# Пример
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

def square(x):
    return x ** 2

# Композиция: сначала add_10, потом multiply_2, потом square
pipeline = compose(square, multiply_2, add_10)

print(pipeline(5))  # 900
# 5 → add_10 → 15 → multiply_2 → 30 → square → 900
```

**Читается справа налево!** (как в математике)

---

## Pipe — композиция слева направо

```python
def pipe(*functions):
    """Применить функции слева направо."""
    def piped(x):
        result = x
        for func in functions:  # Слева направо!
            result = func(result)
        return result
    return piped

# Пример (тот же)
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

def square(x):
    return x ** 2

# Pipe: add_10 → multiply_2 → square (читается естественно!)
pipeline = pipe(add_10, multiply_2, square)

print(pipeline(5))  # 900
# 5 → add_10 → 15 → multiply_2 → 30 → square → 900
```

**Читается слева направо!** (привычнее для кода)

---

## Практические примеры

### Пример 1: Обработка строк
```python
def trim(text):
    """Убрать пробелы."""
    return text.strip()

def lowercase(text):
    """В нижний регистр."""
    return text.lower()

def remove_punctuation(text):
    """Убрать знаки препинания."""
    import string
    return text.translate(str.maketrans("", "", string.punctuation))

# Композиция
clean_text = pipe(trim, lowercase, remove_punctuation)

# Использование
dirty = "  Hello, World!  "
clean = clean_text(dirty)
print(clean)  # "hello world"
```

### Пример 2: Обработка чисел
```python
def validate_positive(x):
    """Проверить, что > 0."""
    if x <= 0:
        raise ValueError("Must be positive")
    return x

def apply_discount(percent):
    """Применить скидку."""
    def discount(price):
        return price * (1 - percent / 100)
    return discount

def add_tax(percent):
    """Добавить налог."""
    def tax(price):
        return price * (1 + percent / 100)
    return tax

def round_price(price):
    """Округлить до 2 знаков."""
    return round(price, 2)

# Композиция: валидация → скид 20% → налог 10% → округление
calculate_price = pipe(
    validate_positive,
    apply_discount(20),
    add_tax(10),
    round_price
)

# Использование
base_price = 100
final_price = calculate_price(base_price)
print(final_price)  # 88.0
# 100 → проверка → 80 (скидка) → 88 (налог) → 88.0 (округление)
```

### Пример 3: Обработка списков
```python
def filter_even(numbers):
    """Только чётные."""
    return [x for x in numbers if x % 2 == 0]

def double_all(numbers):
    """Удвоить все."""
    return [x * 2 for x in numbers]

def sum_all(numbers):
    """Сумма."""
    return sum(numbers)

# Композиция
process_numbers = pipe(filter_even, double_all, sum_all)

# Использование
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = process_numbers(numbers)
print(result)  # 60
# [1..10] → [2,4,6,8,10] → [4,8,12,16,20] → 60
```

---

## Композиция с декораторами

Декораторы — это тоже композиция!

```python
def uppercase_decorator(func):
    """Декоратор: результат в uppercase."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

def exclaim_decorator(func):
    """Декоратор: добавить восклицание."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"{result}!!!"
    return wrapper

@exclaim_decorator
@uppercase_decorator
def greet(name):
    return f"hello, {name}"

print(greet("Alice"))  # "HELLO, ALICE!!!"
# greet → uppercase → exclaim
```

---

## Частичное применение (Partial Application)

Создание специализированных функций из общих.

```python
from functools import partial

def power(base, exponent):
    """Возведение в степень."""
    return base ** exponent

# Создать специализированные функции
square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125

# Композиция с partial
def add(a, b):
    return a + b

add_10 = partial(add, 10)
add_100 = partial(add, 100)

process = pipe(add_10, add_100)
print(process(5))  # 115 (5 + 10 + 100)
```

---

## Карринг (Currying)

Превращение функции с несколькими аргументами в цепочку функций с одним.

```python
def curry(func):
    """Превратить функцию в карринг."""
    def curried(a):
        def inner(b):
            return func(a, b)
        return inner
    return curried

# Обычная функция
def add(a, b):
    return a + b

# Карринг
curried_add = curry(add)

# Использование
add_10 = curried_add(10)
print(add_10(5))   # 15
print(add_10(20))  # 30

# Композиция с каррингом
add_5 = curried_add(5)
add_10 = curried_add(10)

add_both = pipe(add_5, add_10)
print(add_both(100))  # 115 (100 + 5 + 10)
```

---

## Композиция для AI обработки

### Pipeline обработки данных модели
```python
def normalize(data):
    """Нормализация 0-1."""
    max_val = max(data) if data else 1
    return [x / max_val for x in data]

def apply_threshold(threshold):
    """Отсечь значения ниже порога."""
    def thresholded(data):
        return [x if x >= threshold else 0 for x in data]
    return thresholded

def to_classes(data):
    """Преобразовать в классы 0/1."""
    return [1 if x > 0.5 else 0 for x in data]

def count_positives(data):
    """Подсчитать положительные."""
    return sum(data)

# Композиция: нормализация → порог 0.3 → классы → подсчёт
process_model_output = pipe(
    normalize,
    apply_threshold(0.3),
    to_classes,
    count_positives
)

# Использование
raw_scores = [45, 78, 23, 89, 56, 12, 90]
positive_count = process_model_output(raw_scores)
print(positive_count)  # 4
# [45,78,23,89,56,12,90] → [0.5,0.87,0.26,0.99,0.62,0.13,1.0]
# → [0.5,0.87,0,0.99,0.62,0,1.0] → [0,1,0,1,1,0,1] → 4
```

---

## Класс Composable

Удобный класс для композиции.

```python
class Composable:
    """Функция с методом compose."""

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def then(self, other):
        """Композиция: сначала self, потом other."""
        def composed(*args, **kwargs):
            return other(self(*args, **kwargs))
        return Composable(composed)

# Использование
@Composable
def add_10(x):
    return x + 10

@Composable
def multiply_2(x):
    return x * 2

@Composable
def square(x):
    return x ** 2

# Цепочка вызовов!
pipeline = add_10.then(multiply_2).then(square)

print(pipeline(5))  # 900
# 5 → add_10 → 15 → multiply_2 → 30 → square → 900
```

---

## Отладка композиции

### Трассировка выполения
```python
def trace(func):
    """Декоратор для отладки."""
    def wrapper(x):
        result = func(x)
        print(f"{func.__name__}({x}) = {result}")
        return result
    wrapper.__name__ = func.__name__
    return wrapper

# Применяем trace
@trace
def add_10(x):
    return x + 10

@trace
def multiply_2(x):
    return x * 2

@trace
def square(x):
    return x ** 2

# Композиция
pipeline = pipe(add_10, multiply_2, square)

print(pipeline(5))
# Вывод:
# add_10(5) = 15
# multiply_2(15) = 30
# square(30) = 900
# 900
```

---

## Частые ошибки

### Ошибка 1: Неправильный порядок функций
```python
def add_10(x):
    return x + 10

def multiply_2(x):
    return x * 2

# compose читается справа налево!
wrong = compose(add_10, multiply_2)
print(wrong(5))  # 20 (5*2 + 10), НЕ 30!

# pipe читается слева направо!
right = pipe(add_10, multiply_2)
print(right(5))  # 30 (5+10) * 2)
```

### Ошибка 2: Функции с разными сигнатурами
```python
def add(a, b):  # 2 аргумента!
    return a + b

def square(x):  # 1 аргумент!
    return x ** 2

# ❌ ОШИБКА
pipeline = pipe(add, square)
# square ожидает 1 аргумент, а add возвращает число

# ✅ ПРАВИЛЬНО: используй partial или lambda
from functools import partial

add_10 = partial(add, 10)  # Теперь 1 аргумент
pipeline = pipe(add_10, square)
print(pipeline(5))  # 225 ((5+10)^2)
```

### Ошибка 3: Побочные эффекты
```python
counter = 0

def increment_and_double(x):
    global counter
    counter += 1  # Побочный эффект!
    return x * 2

# Композиция с побочными эффектами — ПЛОХО!
# Результат непредсказуем
```

---

## Резюме

### Function Composition — это:
- ✅ Комбинирование простых функций в сложные
- ✅ Переиспользование логики
- ✅ Читаемый pipeline
- ✅ Чистые функции без побочных эффектов

### Два подхода:
```python
# compose: справа налево (математика)
compose(f, g, h)(x) → f(g(h(x)))

# pipe: слева направо (код)
pipe(h, g, f)(x) → f(g(h(x)))
```

### Реализация compose:
```python
def compose(*functions):
    def composed(x):
        result = x
        for func in reversed(functions):
            result = func(result)
        return result
    return composed
```

### Реализация pipe:
```python
def pipe(*functions):
    def piped(x):
        result = x
        for func in functions:
            result = func(result)
        return result
    return piped
```

### Использование:
```python
# Определить шаги
def step1(x): return x + 10
def step2(x): return x * 2
def step3(x): return x ** 2

# Создать pipeline
process = pipe(step1, step2, step3)

# Использовать
result = process(5)  # 900
```

---

## Что дальше?

Теперь ты знаешь Function Composition! 🎉

**Применение:**
- 🏭 Data pipelines — цепочки обработки данных
- 🤖 AI workflows — обработка результатов моделей
- 🧹 Очистка данных — композиция фильтров
- 🔄 Трансформации — многошаговые преобразования

**Связанные темы:**
- Decorators — обёртки для функций
- Higher-order functions — функции высшего порядка
- Functional programming — парадигма FP

Function composition — основа элегантного кода! 🧩✨
