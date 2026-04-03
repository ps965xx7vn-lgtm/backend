# Функции в Python: создавай переиспользуемый код 🔧

**Представь:** ты написал код для расчёта скидки. Этот код нужен в 10 местах программы!

**Плохой подход:** Копируй-вставляй 10 раз → нашёл ошибку → исправляй в 10 местах 😰

**Хороший подход:** Создай функцию → используй 10 раз → исправляй в одном месте! 🚀

**Функции - основа профессионального программирования!**

## 🤔 Что такое функция?

**Функция** - это именованный блок кода, который можно вызывать много раз.

### Функции которые ты уже знаешь:

```python
print("Hello")      # Функция вывода
len("Python")       # Функция длины
input("Имя: ")      # Функция ввода
range(10)           # Функция генерации чисел
```

Все это **встроенные функции** Python. Теперь научимся создавать **свои**!

---

## 📝 Создание функции - синтаксис

### Базовый синтаксис:

```python
def имя_функции():
    код
    код
    return результат  # опционально
```

**Элементы:**
- `def` - ключевое слово (от "define")
- `имя_функции` - твой выбор имени
- `()` - скобки для параметров (пока пустые)
- `:` - двоеточие обязательно!
- Код - с отступом (indent)

### Простейший пример:

```python
def say_hello():
    print("Привет!")
    print("Как дела?")

# Вызов функции:
say_hello()
# Выведет:
# Привет!
# Как дела?
```

### Использование много раз:

```python
say_hello()  # Первый вызов
say_hello()  # Второй вызов
say_hello()  # Третий вызов

# Код выполнится 3 раза!
```

---

## 📦 Параметры - передача данных в функцию

**Параметры** позволяют функции работать с разными данными.

### Один параметр:

```python
def greet(name):
    print(f"Привет, {name}!")

greet("Анна")   # Привет, Анна!
greet("Боб")    # Привет, Боб!
greet("Света")  # Привет, Света!
```

**name** - это **параметр** (в определении функции)
**"Анна"** - это **аргумент** (при вызове функции)

### Несколько параметров:

```python
def introduce(name, age, city):
    print(f"Меня зовут {name}")
    print(f"Мне {age} лет")
    print(f"Я из города {city}")

introduce("Анна", 16, "Москва")
# Меня зовут Анна
# Мне 16 лет
# Я из города Москва
```

### Параметры по умолчанию:

```python
def greet(name="Гость"):
    print(f"Привет, {name}!")

greet()         # Привет, Гость!
greet("Анна")   # Привет, Анна!
```

Если не передал аргумент → используется значение по умолчанию.

### Именованные аргументы:

```python
def create_profile(name, age, city):
    print(f"{name}, {age}, {city}")

# Порядок не важен:
create_profile(age=16, city="Москва", name="Анна")
# Анна, 16, Москва
```

---

## 🔄 Return - возврат значения

**`return`** позволяет функции вернуть результат!

### Без return (только печать):

```python
def add(a, b):
    print(a + b)

add(5, 3)  # Выведет 8, но ничего не вернёт
result = add(5, 3)
print(result)  # None ❌
```

### С return (возврат результата):

```python
def add(a, b):
    return a + b

result = add(5, 3)  # result = 8 ✅
print(result)       # 8
```

**Разница критическая!**

- **print()** - показывает на экране
- **return** - возвращает значение для использования в коде

### Return останавливает функцию:

```python
def check_age(age):
    if age < 18:
        return "Несовершеннолетний"  # Выход здесь!

    # Эта часть не выполнится если age < 18:
    return "Взрослый"

status = check_age(16)
print(status)  # Несовершеннолетний
```

### Несколько return:

```python
def get_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

grade = get_grade(85)
print(f"Оценка: {grade}")  # Оценка: B
```

### Возврат нескольких значений:

```python
def get_user_info():
    name = "Анна"
    age = 16
    city = "Москва"
    return name, age, city  # Возвращает кортеж

# Распаковка:
user_name, user_age, user_city = get_user_info()
print(user_name)  # Анна
print(user_age)   # 16
print(user_city)  # Москва
```

---

## 🎯 Примеры полезных функций

### 1. Калькулятор:

```python
def calculate(a, b, operation):
    if operation == "+":
        return a + b
    elif operation == "-":
        return a - b
    elif operation == "*":
        return a * b
    elif operation == "/":
        if b != 0:
            return a / b
        else:
            return "Ошибка: деление на ноль"
    else:
        return "Неизвестная операция"

result = calculate(10, 5, "+")
print(result)  # 15
```

### 2. Проверка чётности:

```python
def is_even(number):
    return number % 2 == 0

if is_even(10):
    print("10 чётное")
else:
    print("10 нечётное")
# 10 чётное
```

### 3. Поиск максимума:

```python
def find_max(a, b, c):
    if a >= b and a >= c:
        return a
    elif b >= a and b >= c:
        return b
    else:
        return c

maximum = find_max(5, 12, 7)
print(f"Максимум: {maximum}")  # Максимум: 12
```

### 4. Валидация пароля:

```python
def is_password_strong(password):
    if len(password) < 8:
        return False

    has_digit = any(char.isdigit() for char in password)
    has_letter = any(char.isalpha() for char in password)

    return has_digit and has_letter

if is_password_strong("abc123"):
    print("✅ Пароль надёжный")
else:
    print("❌ Пароль слабый")
```

### 5. Конвертер температур:

```python
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

temp_f = celsius_to_fahrenheit(25)
print(f"25°C = {temp_f}°F")  # 25°C = 77.0°F

temp_c = fahrenheit_to_celsius(77)
print(f"77°F = {temp_c}°C")  # 77°F = 25.0°C
```

---

## 🌍 Область видимости (scope)

**Где переменная "живёт"?**

### Локальные переменные:

Создаются **внутри функции**, существуют только там.

```python
def test():
    x = 10  # Локальная переменная
    print(x)  # 10

test()
print(x)  # ❌ NameError: x не существует!
```

### Глобальные переменные:

Создаются **вне функций**, доступны везде.

```python
x = 10  # Глобальная

def test():
    print(x)  # Читает глобальную

test()  # 10
print(x)  # 10
```

### Изменение глобальной в функции:

```python
counter = 0  # Глобальная

def increment():
    global counter  # Говорим что изменяем глобальную!
    counter += 1

increment()
print(counter)  # 1

increment()
print(counter)  # 2
```

### ⚠️ Ловушка:

```python
x = 10

def change():
    x = 20  # Создаёт НОВУЮ локальную!
    print(x)  # 20

change()
print(x)  # 10 (глобальная не изменилась!)
```

### 💡 Лучшая практика - избегай global:

```python
# ❌ С global:
score = 0

def add_points(points):
    global score
    score += points

# ✅ Без global (лучше!):
def add_points(current_score, points):
    return current_score + points

score = 0
score = add_points(score, 10)  # 10
score = add_points(score, 5)   # 15
```

**Параметры + return лучше чем global!**

---

## 📚 Docstrings - документация функций

**Docstring** описывает что делает функция.

```python
def calculate_area(width, height):
    """
    Вычисляет площадь прямоугольника.

    Параметры:
        width (float): Ширина прямоугольника
        height (float): Высота прямоугольника

    Возвращает:
        float: Площадь прямоугольника
    """
    return width * height

# Просмотр документации:
help(calculate_area)
```

**Используй тройные кавычки** `"""` для docstring!

---

## 🎮 Практический пример - игра

Организуем игру Угадай число с функциями:

```python
import random

def get_number_input(prompt, min_val, max_val):
    """Получает число от пользователя в диапазоне."""
    while True:
        try:
            number = int(input(prompt))
            if min_val <= number <= max_val:
                return number
            else:
                print(f"Число должно быть от {min_val} до {max_val}")
        except ValueError:
            print("Введи корректное число!")

def generate_secret_number(min_val, max_val):
    """Генерирует случайное число для угадывания."""
    return random.randint(min_val, max_val)

def check_guess(guess, secret):
    """Проверяет догадку и даёт подсказку."""
    if guess == secret:
        return "correct"
    elif guess < secret:
        return "too_low"
    else:
        return "too_high"

def play_game():
    """Главная функция игры."""
    print("🎮 Игра: Угадай число")

    min_num = 1
    max_num = 100
    max_attempts = 7

    secret = generate_secret_number(min_num, max_num)

    for attempt in range(1, max_attempts + 1):
        print(f"\nПопытка {attempt}/{max_attempts}")
        guess = get_number_input(f"Твоё число ({min_num}-{max_num}): ",
                                  min_num, max_num)

        result = check_guess(guess, secret)

        if result == "correct":
            print(f"🎉 Победа! Угадал за {attempt} попыток!")
            return
        elif result == "too_low":
            print("⬆️ Моё число больше")
        else:
            print("⬇️ Моё число меньше")

    print(f"\n😢 Проигрыш! Число было: {secret}")

# Запуск игры:
play_game()
```

**Преимущества:**
- Каждая функция решает одну задачу
- Код читаемый и понятный
- Легко тестировать каждую часть
- Легко добавлять новые функции

---

## 💡 Лучшие практики

### 1. Именование функций:

```python
# ✅ Хорошие имена (глаголы, описывают действие):
def calculate_total()
def send_email()
def validate_password()
def find_maximum()

# ❌ Плохие имена:
def func1()        # Неясно что делает
def do_stuff()     # Слишком общее
def x()            # Непонятное
```

### 2. Одна функция = одна задача:

```python
# ❌ Функция делает слишком много:
def process_user():
    validate_input()
    save_to_database()
    send_email()
    update_statistics()
    log_action()

# ✅ Разбей на несколько функций:
def validate_user_input():
    # ...

def save_user():
    # ...

def notify_user_by_email():
    # ...
```

### 3. Размер функции:

**Идеал:** 10-20 строк
**Максимум:** 30-50 строк
**Если больше:** Разбивай на несколько функций!

### 4. Избегай побочных эффектов:

```python
# ❌ Изменяет глобальное состояние:
count = 0

def add(x, y):
    global count
    count += 1  # Побочный эффект!
    return x + y

# ✅ Чистая функция (без побочных эффектов):
def add(x, y):
    return x + y  # Только вычисление, ничего не меняет
```

### 5. Используй return вместо print:

```python
# ❌ Только печатает:
def calculate(a, b):
    result = a + b
    print(result)

# ✅ Возвращает значение:
def calculate(a, b):
    return a + b

# Теперь можно использовать результат:
total = calculate(5, 3)
if total > 10:
    print("Больше 10")
```

---

## ⚠️ Распространённые ошибки

### 1. Забыл двоеточие:

```python
# ❌ Ошибка:
def greet()
    print("Hi")

# ✅ Правильно:
def greet():
    print("Hi")
```

### 2. Забыл отступ:

```python
# ❌ Ошибка:
def greet():
print("Hi")

# ✅ Правильно:
def greet():
    print("Hi")
```

### 3. Забыл вызвать (скобки):

```python
def greet():
    print("Hi")

greet  # ❌ Ничего не выведет (это объект функции)
greet()  # ✅ Hi
```

### 4. Путаница параметр/аргумент:

```python
def greet(name):  # name - ПАРАМЕТР
    print(f"Hi, {name}")

greet("Anna")  # "Anna" - АРГУМЕНТ
```

### 5. Использовал переменную до определения:

```python
# ❌ Ошибка:
def test():
    print(x)  # x ещё не определён!
    x = 10

# ✅ Правильно:
def test():
    x = 10
    print(x)
```

---

## 🚀 Итого

**Функции - основа профессионального кода!**

Ты научился:

✅ Создавать функции с `def`
✅ Использовать параметры для передачи данных
✅ Возвращать результаты с `return`
✅ Понимать область видимости (scope)
✅ Организовывать код в переиспользуемые блоки
✅ Следовать лучшим практикам

**С функциями ты можешь:**
- Избегать дублирования кода
- Делать код читаемым
- Упрощать тестирование
- Масштабировать проекты
- Работать в команде эффективнее

---

**Практикуй в CodeHS!** Создавай функции для всего:
- Калькуляторы
- Валидаторы
- Конвертеры
- Игры

**Золотое правило:** Если код повторяется → создай функцию! 💪

**Следующий шаг:** Изучи списки и словари чтобы работать с коллекциями данных! 📦
