# Переменные в Python простыми словами 📦

Переменная - это как коробка с именем, куда можно положить любое значение и потом использовать его много раз!

## 🎯 Что такое переменная?

Представь: у тебя есть коробка. На ней написано "age" (возраст). Положил туда число 16. Теперь везде где нужен возраст - просто открываешь эту коробку!

```python
# Создаём переменную
age = 16

# Используем её
print(age)        # 16
print(age + 5)    # 21
print(age * 2)    # 32
```

## ✏️ Как создать переменную

Очень просто: `имя = значение`

```python
name = 'Алекс'
age = 20
height = 1.75
is_student = True
```

**Важно:** Знак `=` это не "равно"! Это "присвоить значение".

## 📝 Правила именования

### ✅ Разрешено

```python
name = 'Иван'
user_age = 25
firstName = 'Мария'
count_2 = 10
_private = 'секрет'
```

### ❌ Запрещено

```python
2name = 'error'     # Нельзя начинать с цифры
user-age = 25       # Нельзя использовать дефис
first name = 'test' # Нельзя использовать пробел
if = 5              # Нельзя использовать ключевые слова
```

## 🔄 Изменение значения

Переменную можно изменить в любой момент!

```python
score = 0
print(score)  # 0

score = 10
print(score)  # 10

score = score + 5
print(score)  # 15

# Короткая запись
score += 5    # То же что: score = score + 5
print(score)  # 20
```

## 🎨 Типы переменных

Python сам понимает что ты хочешь сохранить!

```python
# Строка (текст)
name = 'Анна'
city = "Москва"
message = '''Длинный
текст на
нескольких строках'''

# Целое число
age = 18
year = 2026
temperature = -5

# Дробное число
height = 1.65
price = 99.99
pi = 3.14159

# Логический тип
is_adult = True
has_license = False
```

## 🔍 Узнать тип переменной

```python
name = 'Олег'
age = 25
height = 1.80
is_student = True

print(type(name))       # <class 'str'>
print(type(age))        # <class 'int'>
print(type(height))     # <class 'float'>
print(type(is_student)) # <class 'bool'>
```

## 💡 Работа с переменными

### Копирование

```python
x = 10
y = x     # y получает КОПИЮ значения x
y = 20    # Меняем y, но x остался 10!

print(x)  # 10
print(y)  # 20
```

### Обмен значениями

```python
# Простой способ в Python!
a = 5
b = 10

a, b = b, a  # Обмен значениями

print(a)  # 10
print(b)  # 5
```

### Множественное присваивание

```python
# Одно значение нескольким переменным
x = y = z = 0
print(x, y, z)  # 0 0 0

# Разные значения сразу
name, age, city = 'Иван', 20, 'Москва'
print(name)  # Иван
print(age)   # 20
print(city)  # Москва
```

## 🎯 Частые ошибки

### Ошибка 1: Использование до создания

```python
# ❌ Ошибка!
print(name)  # NameError: name 'name' is not defined
name = 'Петя'

# ✅ Правильно
name = 'Петя'
print(name)  # Сначала создаём, потом используем
```

### Ошибка 2: Кавычки vs без кавычек

```python
name = 'Вася'

print('name')  # Выведет: name (это текст)
print(name)    # Выведет: Вася (это значение переменной)

# С кавычками - это текст
# Без кавычек - это переменная
```

### Ошибка 3: Регистр важен!

```python
age = 16
Age = 20
AGE = 25

print(age)  # 16
print(Age)  # 20
print(AGE)  # 25

# Это три РАЗНЫЕ переменные!
```

### Ошибка 4: Русские имена

```python
# ⚠️ Технически работает, но не рекомендуется
имя = 'Вася'
print(имя)  # Вася

# ✅ Лучше использовать английские имена
name = 'Вася'
print(name)  # Вася
```

## 💪 Хорошие практики

### 1. Понятные имена

```python
# ❌ Плохо
a = 16
x = 'Москва'
tmp = 1.75

# ✅ Хорошо
age = 16
city = 'Москва'
height = 1.75
```

### 2. Snake_case для переменных

```python
# ✅ Принято в Python
user_name = 'Иван'
first_name = 'Мария'
total_score = 100
```

### 3. Константы ЗАГЛАВНЫМИ

```python
# Значения которые не меняются
MAX_SPEED = 120
PI = 3.14159
API_KEY = 'secret123'
```

## 🚀 Практические примеры

### Пример 1: Анкета

```python
print('=== Анкета ===')

name = input('Имя: ')
age = int(input('Возраст: '))
city = input('Город: ')
hobby = input('Хобби: ')

print(f'\\n📝 Твои данные:')
print(f'Имя: {name}')
print(f'Возраст: {age}')
print(f'Город: {city}')
print(f'Хобби: {hobby}')
```

### Пример 2: Калькулятор возраста

```python
current_year = 2026
birth_year = int(input('В каком году ты родился? '))

age = current_year - birth_year

print(f'Тебе {age} лет')
print(f'Через 10 лет тебе будет {age + 10}')
print(f'5 лет назад тебе было {age - 5}')
```

### Пример 3: Обмен валют

```python
# Курсы валют
usd_to_rub = 75
eur_to_rub = 85

dollars = float(input('Сколько у тебя долларов? '))
euros = float(input('Сколько у тебя евро? '))

rubles_from_usd = dollars * usd_to_rub
rubles_from_eur = euros * eur_to_rub
total_rubles = rubles_from_usd + rubles_from_eur

print(f'\\nВсего в рублях: {total_rubles:.2f} ₽')
```

## 📋 Шпаргалка

```python
# Создание
variable = value

# Изменение
variable = new_value
variable += 5  # Увеличить на 5
variable -= 3  # Уменьшить на 3
variable *= 2  # Умножить на 2
variable /= 4  # Разделить на 4

# Узнать тип
type(variable)

# Преобразование типов
str(123)    # '123'
int('456')  # 456
float('1.5') # 1.5
bool(1)     # True
```

## 🎓 Итог

- Переменная = именованное хранилище для значения
- Создаётся как `name = value`
- Можно менять в любой момент
- Имя пишется на английском, snake_case
- Python сам определяет тип данных
- Используй понятные имена!

Переменные - основа программирования. С ними код становится гибким и понятным! 💪
