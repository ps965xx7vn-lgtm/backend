# Типы данных в Python: полный гид 🎯

Python может работать с разными типами данных: числами, текстом, логическими значениями. Разберём все основные типы!

## 📊 Основные типы данных

### 1. int - Целые числа

```python
age = 25
year = 2026
temperature = -15
big_number = 1000000

print(type(age))  # <class 'int'>
```

**Где используется:** счётчики, возраст, количество, годы

### 2. float - Дробные числа

```python
height = 1.75
price = 99.99
pi = 3.14159
temperature = -5.5

print(type(height))  # <class 'float'>
```

**Где используется:** рост, цены, проценты, координаты

### 3. str - Строки (текст)

```python
name = 'Анна'
city = "Москва"
message = '''Многострочный
текст'''

print(type(name))  # <class 'str'>
```

**Где используется:** имена, адреса, сообщения, любой текст

### 4. bool - Логический тип

```python
is_student = True
has_license = False

print(type(is_student))  # <class 'bool'>
```

**Где используется:** проверки условий, флаги состояния

## 🔄 Преобразование типов

### Строка → Число

```python
# Строка → Целое число
age_str = '25'
age_int = int(age_str)
print(age_int + 5)  # 30

# Строка → Дробное число
price_str = '99.99'
price_float = float(price_str)
print(price_float * 2)  # 199.98

# ⚠️ Ошибка если строка не число!
int('abc')  # ValueError!
```

### Число → Строка

```python
age = 25
age_str = str(age)
print('Мне ' + age_str + ' лет')  # Мне 25 лет

# Или используй f-строки (проще!)
print(f'Мне {age} лет')  # Мне 25 лет
```

### В логический тип

```python
# Любое число кроме 0 → True
bool(1)      # True
bool(100)    # True
bool(-5)     # True
bool(0)      # False

# Любая непустая строка → True
bool('текст') # True
bool('')      # False (пустая строка)
```

## 🎯 Частые ошибки

### Ошибка 1: Сложение строки и числа

```python
# ❌ TypeError!
age = 16
print('Мне ' + age + ' лет')  # Ошибка!

# ✅ Преобразуй число в строку
print('Мне ' + str(age) + ' лет')

# ✅ Или используй f-строку
print(f'Мне {age} лет')

# ✅ Или через запятую
print('Мне', age, 'лет')
```

### Ошибка 2: Деление int всегда даёт float

```python
print(10 / 2)   # 5.0 (float!)
print(10 // 2)  # 5 (int)

# Даже если делится нацело
result = 10 / 2
print(type(result))  # <class 'float'>
```

### Ошибка 3: True/False с большой буквы

```python
# ❌ Ошибка!
is_active = true   # NameError!

# ✅ Правильно
is_active = True
is_ready = False
```

## 💡 Проверка типа

```python
age = 25

# Узнать тип
print(type(age))  # <class 'int'>

# Проверить тип
if isinstance(age, int):
    print('Это целое число')

if isinstance('текст', str):
    print('Это строка')
```

## 🔢 Операции с разными типами

### int + int → int

```python
a = 10
b = 5
print(a + b)       # 15 (int)
print(type(a + b)) # <class 'int'>
```

### int + float → float

```python
a = 10     # int
b = 5.5    # float
print(a + b)       # 15.5 (float)
print(type(a + b)) # <class 'float'>
```

### str + str → str

```python
first = 'Привет'
second = 'мир'
print(first + ' ' + second)  # Привет мир
```

### str * int → str

```python
print('🔥' * 5)     # 🔥🔥🔥🔥🔥
print('ha' * 3)     # hahaha
```

## 🎨 Особенности строк

### Кавычки

```python
# Одинарные
name = 'Анна'

# Двойные
city = "Москва"

# Тройные (многострочный текст)
message = '''
Первая строка
Вторая строка
Третья строка
'''
```

### Спецсимволы

```python
# Перенос строки
print('Первая\\nВторая')

# Табуляция
print('Имя:\\tАнна')

# Кавычка внутри
print('Он сказал: \\'Привет!\\'')
```

### Индексация

```python
text = 'Python'

print(text[0])   # P (первый символ)
print(text[1])   # y (второй символ)
print(text[-1])  # n (последний)
print(text[-2])  # o (предпоследний)
```

## 🚀 Практические примеры

### Пример 1: Калькулятор типов

```python
num1 = int(input('Первое число: '))
num2 = int(input('Второе число: '))

print(f'{num1} + {num2} = {num1 + num2}')
print(f'Тип: {type(num1 + num2)}')

num3 = float(input('Дробное число: '))
print(f'{num1} + {num3} = {num1 + num3}')
print(f'Тип: {type(num1 + num3)}')
```

### Пример 2: Конвертер

```python
# Строка → Число → Строка
age_str = input('Возраст: ')
age_int = int(age_str)
doubled = age_int * 2
result = str(doubled)

print(f'Удвоенный возраст: {result}')
```

### Пример 3: Проверка типов

```python
value = input('Введи что-нибудь: ')

# Проверяем что ввели
if value.isdigit():
    print('Это число!')
    number = int(value)
    print(f'Удвоенное: {number * 2}')
elif value.isalpha():
    print('Это текст!')
    print(f'В верхнем регистре: {value.upper()}')
else:
    print('Это что-то другое')
```

## 📋 Шпаргалка

```python
# Типы данных
int    # Целое число: 10, -5, 0
float  # Дробное: 3.14, -0.5, 99.99
str    # Строка: 'текст', "text"
bool   # Логический: True, False

# Преобразования
int('123')      # '123' → 123
float('3.14')   # '3.14' → 3.14
str(456)        # 456 → '456'
bool(1)         # 1 → True

# Проверки
type(x)              # Узнать тип
isinstance(x, int)   # Проверить тип
value.isdigit()      # Строка из цифр?
value.isalpha()      # Строка из букв?
```

## 🎓 Итог

- **int** - целые числа (10, -5, 0)
- **float** - дробные числа (3.14, 99.99)
- **str** - текст ('привет', "мир")
- **bool** - True или False
- Преобразуй типы функциями: int(), float(), str(), bool()
- Python сам выбирает тип при создании переменной
- Нельзя складывать числа и строки напрямую!

Понимание типов данных - ключ к работе без ошибок! 💪
