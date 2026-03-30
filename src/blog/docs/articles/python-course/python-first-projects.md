# 10 идей для первых Python-проектов 💡

Уже знаешь основы Python? Пора применить знания на практике! Вот 10 проектов от простых к сложным.

## 1. 🎲 Генератор случайных чисел

**Что нужно знать:** print(), input(), random

```python
import random

print('🎲 Генератор случайных чисел\\n')

min_num = int(input('Минимум: '))
max_num = int(input('Максимум: '))

result = random.randint(min_num, max_num)
print(f'\\nСлучайное число: {result}')
```

**Идеи для улучшения:**
- Генерировать несколько чисел
- Добавить генерацию без повторов
- Сделать лотерейный билет (6 чисел)

## 2. 💱 Конвертер валют

**Что нужно знать:** print(), input(), float, математика

```python
print('💱 Конвертер валют\\n')

# Курсы
USD_TO_RUB = 75
EUR_TO_RUB = 85

currency = input('Валюта (USD/EUR): ').upper()
amount = float(input('Сумма: '))

if currency == 'USD':
    result = amount * USD_TO_RUB
    print(f'${amount} = {result} ₽')
elif currency == 'EUR':
    result = amount * EUR_TO_RUB
    print(f'€{amount} = {result} ₽')
else:
    print('Неизвестная валюта')
```

**Идеи для улучшения:**
- Добавить больше валют
- Конвертация в обе стороны
- Получать курсы из интернета

## 3. 🌡️ Конвертер температур

**Что нужно знать:** if/elif, формулы, round()

```python
print('🌡️ Конвертер температур\\n')

temp = float(input('Температура: '))
unit = input('Из чего конвертировать (C/F): ').upper()

if unit == 'C':
    fahrenheit = temp * 9/5 + 32
    print(f'{temp}°C = {fahrenheit:.1f}°F')
elif unit == 'F':
    celsius = (temp - 32) * 5/9
    print(f'{temp}°F = {celsius:.1f}°C')
```

**Идеи для улучшения:**
- Добавить Кельвины
- Показать все три шкалы
- Добавить описание (холодно/тепло/жарко)

## 4. 🧮 Калькулятор BMI

**Что нужно знать:** input(), float, if/elif, математика

```python
print('🧮 Калькулятор индекса массы тела\\n')

weight = float(input('Вес (кг): '))
height = float(input('Рост (м): '))

bmi = weight / (height ** 2)

print(f'\\nТвой BMI: {bmi:.1f}')

if bmi < 18.5:
    print('Недостаточный вес')
elif bmi < 25:
    print('Нормальный вес')
elif bmi < 30:
    print('Избыточный вес')
else:
    print('Ожирение')
```

**Идеи для улучшения:**
- Добавить расчёт идеального веса
- Советы по питанию
- График изменения веса

## 5. 🔐 Генератор паролей

**Что нужно знать:** random, string, циклы

```python
import random
import string

print('🔐 Генератор паролей\\n')

length = int(input('Длина пароля: '))

# Символы для пароля
chars = string.ascii_letters + string.digits + '!@#$%^&*'

# Генерируем
password = ''
for i in range(length):
    password += random.choice(chars)

print(f'\\nТвой пароль: {password}')
```

**Идеи для улучшения:**
- Выбор: только буквы/с цифрами/со спецсимволами
- Проверка сложности пароля
- Генерация нескольких вариантов

## 6. 📝 TODO-список

**Что нужно знать:** списки, циклы, функции

```python
tasks = []

while True:
    print('\\n=== TODO ===')
    print('1. Показать задачи')
    print('2. Добавить задачу')
    print('3. Удалить задачу')
    print('4. Выход')

    choice = input('\\nВыбери действие: ')

    if choice == '1':
        if tasks:
            for i, task in enumerate(tasks, 1):
                print(f'{i}. {task}')
        else:
            print('Нет задач')

    elif choice == '2':
        task = input('Новая задача: ')
        tasks.append(task)
        print('✅ Добавлено!')

    elif choice == '3':
        num = int(input('Номер задачи: ')) - 1
        if 0 <= num < len(tasks):
            removed = tasks.pop(num)
            print(f'❌ Удалено: {removed}')

    elif choice == '4':
        break
```

**Идеи для улучшения:**
- Отметка выполненных задач
- Приоритеты (важные/обычные)
- Сохранение в файл

## 7. 🎯 Угадай число

**Что нужно знать:** random, циклы, счётчики

```python
import random

print('🎯 Угадай число от 1 до 100\\n')

secret = random.randint(1, 100)
attempts = 0

while True:
    guess = int(input('Твоё число: '))
    attempts += 1

    if guess < secret:
        print('↗️ Больше!')
    elif guess > secret:
        print('↘️ Меньше!')
    else:
        print(f'🎉 Угадал за {attempts} попыток!')
        break
```

**Идеи для улучшения:**
- Уровни сложности (разные диапазоны)
- Ограничение попыток
- Таблица рекордов

## 8. 📊 Анализатор текста

**Что нужно знать:** строки, методы строк, циклы

```python
print('📊 Анализатор текста\\n')

text = input('Введи текст: ')

# Статистика
words = text.split()
letters = [c for c in text if c.isalpha()]

print(f'\\nСимволов: {len(text)}')
print(f'Букв: {len(letters)}')
print(f'Слов: {len(words)}')
print(f'Предложений: {text.count(".") + text.count("!") + text.count("?")}')

# Самое длинное слово
if words:
    longest = max(words, key=len)
    print(f'Самое длинное слово: {longest} ({len(longest)} букв)')
```

**Идеи для улучшения:**
- Частота букв
- Поиск палиндромов
- Проверка орфографии

## 9. 🎲 Игра "Камень-Ножницы-Бумага"

**Что нужно знать:** random, if/elif, циклы

```python
import random

choices = ['камень', 'ножницы', 'бумага']
score = {'player': 0, 'computer': 0}

while True:
    print(f'\\n🎲 Счёт {score["player"]}:{score["computer"]}')

    player = input('Твой выбор (к/н/б) или q для выхода: ').lower()

    if player == 'q':
        break

    if player not in ['к', 'н', 'б']:
        continue

    computer = random.choice(['к', 'н', 'б'])

    print(f'Компьютер: {computer}')

    # Проверка победителя
    if player == computer:
        print('Ничья!')
    elif (player == 'к' and computer == 'н') or \\
         (player == 'н' and computer == 'б') or \\
         (player == 'б' and computer == 'к'):
        print('Ты выиграл!')
        score['player'] += 1
    else:
        print('Компьютер выиграл!')
        score['computer'] += 1
```

**Идеи для улучшения:**
- Добавить "ящерица" и "Спок"
- Режим на время
- Сохранять статистику

## 10. 💰 Личный бюджет

**Что нужно знать:** списки, словари, функции

```python
expenses = []
income = []

while True:
    print('\\n💰 Личный бюджет')
    print('1. Добавить доход')
    print('2. Добавить расход')
    print('3. Показать баланс')
    print('4. Выход')

    choice = input('\\nВыбери: ')

    if choice == '1':
        amount = float(input('Сумма: '))
        note = input('Откуда: ')
        income.append({'amount': amount, 'note': note})
        print('✅ Добавлено!')

    elif choice == '2':
        amount = float(input('Сумма: '))
        note = input('На что: ')
        expenses.append({'amount': amount, 'note': note})
        print('✅ Добавлено!')

    elif choice == '3':
        total_income = sum(x['amount'] for x in income)
        total_expenses = sum(x['amount'] for x in expenses)
        balance = total_income - total_expenses

        print(f'\\nДоходы: {total_income} ₽')
        print(f'Расходы: {total_expenses} ₽')
        print(f'Баланс: {balance} ₽')

    elif choice == '4':
        break
```

**Идеи для улучшения:**
- Категории расходов
- График трат
- Цели накопления

## 🎓 Советы

### Начинай с простого
Не пытайся сделать всё и сразу! Сначала базовая версия, потом улучшения.

### Используй комментарии
```python
# Это помогает понять код потом
score = 0  # Счёт игрока
```

### Тестируй постоянно
Не пиши весь код сразу. Добавил функцию → протестировал → добавил следующую.

### Не бойся ошибок
Каждая ошибка учит чему-то новому! Читай сообщения об ошибках.

## 📚 Что дальше?

После этих проектов попробуй:
- Telegram-боты (библиотека python-telegram-bot)
- Веб-приложения (Flask)
- Игры с графикой (Pygame)
- Анализ данных (Pandas)

Главное - программируй каждый день, даже по 15 минут! 💪
