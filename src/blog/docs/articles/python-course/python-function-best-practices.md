# Функции: Лучшие практики 🎯

**Цель:** Научиться писать **правильные** функции, которые легко читать, тестировать и использовать.

---

## 🤔 Что делает функцию хорошей?

**Плохая функция:**
```python
def f(x, y):
    print("Результат:")
    z = x + y
    print(z)
    return z
```

**Хорошая функция:**
```python
def calculate_sum(first_number, second_number):
    """Вычислить сумму двух чисел."""
    return first_number + second_number
```

**Разница:**
- ✅ Понятное название
- ✅ Понятные имена параметров
- ✅ Документация (docstring)
- ✅ Только вычисления, без вывода
- ✅ Простая и предсказуемая

---

## 📝 Правило #1: Название должно говорить, ЧТО делает функция

### ❌ Плохие названия

```python
def f():          # Что делает "f"?
def data():       # Что с данными?
def process():    # Что обрабатываем?
def do_stuff():   # Какие "штуки"?
def x():          # Что это вообще?
```

**Проблема:** Нужно читать код внутри, чтобы понять назначение.

---

### ✅ Хорошие названия

```python
def calculate_total_price():
def send_email():
def validate_user_input():
def find_max_value():
def save_to_database():
```

**Принцип:** Название — это **глагол** + **что делаем**.

---

### 🎯 Шаблоны названий

| Действие | Примеры |
|----------|---------|
| **Получить** | `get_user()`, `get_balance()`, `get_settings()` |
| **Установить** | `set_name()`, `set_balance()`, `set_status()` |
| **Вычислить** | `calculate_total()`, `calculate_tax()`, `calculate_discount()` |
| **Создать** | `create_account()`, `create_user()`, `create_report()` |
| **Проверить** | `validate_email()`, `check_balance()`, `is_valid()` |
| **Найти** | `find_user()`, `search_products()`, `locate_file()` |
| **Сохранить** | `save_data()`, `save_to_file()`, `save_user()` |
| **Загрузить** | `load_data()`, `load_from_file()`, `load_settings()` |
| **Удалить** | `delete_user()`, `remove_item()`, `clear_cache()` |
| **Обновить** | `update_balance()`, `refresh_data()`, `sync_data()` |

---

### 🔍 Специальные префиксы

**`is_` / `has_` / `can_` — для логических функций:**
```python
def is_adult(age):
    """Проверить, совершеннолетний ли."""
    return age >= 18

def has_permission(user):
    """Проверить, есть ли права."""
    return user.role == "admin"

def can_withdraw(balance, amount):
    """Проверить, можно ли снять деньги."""
    return balance >= amount
```

**Возвращают:** `True` или `False`

---

## 📝 Правило #2: Одна функция — одна задача (SRP)

**SRP (Single Responsibility Principle)** — принцип единственной ответственности.

### ❌ Плохо: Функция делает всё

```python
def process_user(name, age):
    print(f"Обработка пользователя {name}...")

    if age < 18:
        print("Несовершеннолетний!")
        return False

    with open("users.txt", "a") as f:
        f.write(f"{name},{age}\n")

    print("Отправка email...")
    # отправка email

    print("Запись в базу...")
    # запись в БД

    print("Готово!")
    return True
```

**Проблемы:**
- 🔴 Делает 4 разные вещи
- 🔴 Сложно тестировать
- 🔴 Нельзя переиспользовать части
- 🔴 Сложно понять, что происходит

---

### ✅ Хорошо: Разбить на маленькие функции

```python
def is_adult(age):
    """Проверить, совершеннолетний ли."""
    return age >= 18

def save_user_to_file(name, age):
    """Сохранить пользователя в файл."""
    with open("users.txt", "a") as f:
        f.write(f"{name},{age}\n")

def send_welcome_email(name):
    """Отправить приветственное письмо."""
    # отправка email
    pass

def save_user_to_database(name, age):
    """Сохранить пользователя в базу данных."""
    # запись в БД
    pass

def register_user(name, age):
    """Зарегистрировать нового пользователя."""
    if not is_adult(age):
        return False

    save_user_to_file(name, age)
    send_welcome_email(name)
    save_user_to_database(name, age)
    return True
```

**Преимущества:**
- ✅ Каждая функция делает **одно дело**
- ✅ Легко тестировать по отдельности
- ✅ Можно переиспользовать
- ✅ Легко читать и понимать

---

## 📝 Правило #3: Функция НЕ должна печатать (чистые функции)

### ❌ Плохо: Функция с print внутри

```python
def calculate_discount(price, discount_percent):
    discount = price * discount_percent / 100
    final_price = price - discount
    print(f"Цена: {price} руб.")
    print(f"Скидка: {discount} руб.")
    print(f"Итого: {final_price} руб.")
    return final_price
```

**Проблемы:**
- 🔴 Нельзя использовать без вывода
- 🔴 Сложно тестировать
- 🔴 Нарушает принцип одной задачи
- 🔴 Смешивает логику и отображение

---

### ✅ Хорошо: Разделить логику и отображение

```python
def calculate_discount(price, discount_percent):
    """Вычислить цену со скидкой."""
    discount = price * discount_percent / 100
    final_price = price - discount
    return final_price

# Отдельно — отображение
def show_discount_info(price, discount_percent):
    """Показать информацию о скидке."""
    final_price = calculate_discount(price, discount_percent)
    discount = price - final_price

    print(f"Цена: {price} руб.")
    print(f"Скидка: {discount} руб.")
    print(f"Итого: {final_price} руб.")

# Использование
price = calculate_discount(1000, 20)  # Просто вычисления
show_discount_info(1000, 20)          # С выводом
```

**Преимущества:**
- ✅ `calculate_discount()` — чистая функция
- ✅ Можно использовать в тестах
- ✅ Можно использовать без вывода
- ✅ Логика отделена от отображения

---

## 🎯 Чистая функция (Pure Function)

**Чистая функция:**
1. **Возвращает результат** (не печатает)
2. **Не меняет внешние данные** (нет побочных эффектов)
3. **Всегда один результат** при одинаковых аргументах

### ✅ Чистые функции

```python
def add(a, b):
    """Сложить два числа."""
    return a + b

def calculate_area(width, height):
    """Вычислить площадь."""
    return width * height

def is_even(number):
    """Проверить, чётное ли число."""
    return number % 2 == 0
```

**Признаки:**
- Только `return`, без `print`
- Не меняют переменные вне функции
- Предсказуемые

---

### ❌ Нечистые функции

```python
total = 0

def add_to_total(value):
    """Добавить к глобальной переменной."""
    global total
    total += value  # Меняет внешнюю переменную!

def print_greeting(name):
    """Напечатать приветствие."""
    print(f"Привет, {name}!")  # Печатает, не возвращает!

def get_random_number():
    """Получить случайное число."""
    import random
    return random.randint(1, 100)  # Каждый раз разный результат!
```

**Почему нечистые:**
- Меняют внешние данные (`global`)
- Печатают вместо возврата
- Зависят от случайности/времени

---

## 📝 Правило #4: Параметры должны быть понятными

### ❌ Плохо

```python
def f(x, y, z):
    return x + y * z

result = f(10, 5, 2)  # Что здесь что?
```

---

### ✅ Хорошо

```python
def calculate_total_price(base_price, quantity, tax_rate):
    """Вычислить общую стоимость с налогом."""
    return base_price + quantity * tax_rate

result = calculate_total_price(
    base_price=10,
    quantity=5,
    tax_rate=2
)
```

**Преимущества:**
- ✅ Понятно, что передаём
- ✅ Можно менять порядок
- ✅ Самодокументируемый код

---

## 📝 Правило #5: Возвращай результат, не изменяй аргументы

### ❌ Плохо: Изменение аргумента

```python
def add_item(items, new_item):
    """Добавить элемент в список."""
    items.append(new_item)  # Меняет исходный список!

my_list = [1, 2, 3]
add_item(my_list, 4)  # my_list теперь [1, 2, 3, 4]
```

**Проблема:** Неожиданное изменение внешних данных!

---

### ✅ Хорошо: Возврат нового значения

```python
def add_item(items, new_item):
    """Создать новый список с добавленным элементом."""
    return items + [new_item]  # Возвращаем новый список

my_list = [1, 2, 3]
new_list = add_item(my_list, 4)  # my_list остался [1, 2, 3]
print(new_list)  # [1, 2, 3, 4]
```

**Преимущество:** Исходные данные **не изменяются**.

---

## 📝 Правило #6: Используй значения по умолчанию

```python
def create_account(name, balance=0, currency="RUB"):
    """Создать банковский счёт."""
    return {
        "name": name,
        "balance": balance,
        "currency": currency
    }

# Разные способы вызова
account1 = create_account("Алиса")
account2 = create_account("Боб", 1000)
account3 = create_account("Чарли", 500, "USD")
```

**Преимущества:**
- ✅ Меньше аргументов при вызове
- ✅ Разумные значения по умолчанию
- ✅ Гибкость использования

---

## 📝 Правило #7: Документируй функции (Docstrings)

### ❌ Без документации

```python
def calc(p, d):
    return p - (p * d / 100)
```

**Проблема:** Непонятно, что делает, что за `p` и `d`.

---

### ✅ С документацией

```python
def calculate_discounted_price(price, discount_percent):
    """
    Вычислить цену со скидкой.

    Args:
        price: Начальная цена товара
        discount_percent: Процент скидки (0-100)

    Returns:
        Цена после применения скидки

    Example:
        >>> calculate_discounted_price(1000, 20)
        800.0
    """
    discount = price * discount_percent / 100
    return price - discount
```

**Формат docstring:**
1. Краткое описание (одна строка)
2. Подробное описание (если нужно)
3. Args: параметры
4. Returns: что возвращает
5. Example: пример использования

---

## 📝 Правило #8: Не делай функцию слишком длинной

### ❌ Плохо: Слишком длинная функция

```python
def process_order(order_id):
    # 100+ строк кода
    # проверка заказа
    # расчёт цены
    # проверка склада
    # отправка email
    # запись в БД
    # обновление статистики
    # логирование
    # ...
    pass
```

**Проблема:** Сложно читать, тестировать, понимать.

---

### ✅ Хорошо: Разбить на маленькие функции

```python
def validate_order(order_id):
    """Проверить корректность заказа."""
    # ...

def calculate_order_total(order):
    """Вычислить итоговую сумму."""
    # ...

def check_inventory(order):
    """Проверить наличие на складе."""
    # ...

def send_confirmation_email(order):
    """Отправить письмо подтверждения."""
    # ...

def save_order_to_database(order):
    """Сохранить заказ в базу."""
    # ...

def process_order(order_id):
    """Обработать заказ полностью."""
    order = validate_order(order_id)
    total = calculate_order_total(order)

    if not check_inventory(order):
        return False

    save_order_to_database(order)
    send_confirmation_email(order)
    return True
```

**Правило:** Функция должна помещаться **на один экран** (~20-30 строк максимум).

---

## 📝 Правило #9: Возвращай значимые результаты

### ❌ Плохо: Неинформативный возврат

```python
def save_user(name):
    # сохранение...
    return True  # Что значит True?
```

---

### ✅ Хорошо: Информативный возврат

```python
def save_user(name):
    """Сохранить пользователя."""
    try:
        # сохранение...
        return {"success": True, "message": "Пользователь сохранён"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка: {e}"}

result = save_user("Алиса")
if result["success"]:
    print(result["message"])
```

**Или лучше — исключения:**
```python
def save_user(name):
    """Сохранить пользователя. Бросает исключение при ошибке."""
    # сохранение...
    # если ошибка, то raise Exception("...")

try:
    save_user("Алиса")
    print("Сохранено!")
except Exception as e:
    print(f"Ошибка: {e}")
```

---

## 📝 Правило #10: Избегай слишком много параметров

### ❌ Плохо: 7+ параметров

```python
def create_user(name, age, email, phone, address, city, country, postal_code):
    # ...
```

**Проблема:** Сложно запомнить порядок, легко ошибиться.

---

### ✅ Хорошо: Используй словарь или класс

```python
def create_user(user_data):
    """Создать пользователя из словаря."""
    name = user_data["name"]
    age = user_data["age"]
    email = user_data["email"]
    # ...

user_data = {
    "name": "Алиса",
    "age": 25,
    "email": "alice@example.com",
    "phone": "+7...",
    "address": "...",
    "city": "Москва",
    "country": "Россия",
    "postal_code": "123456"
}

create_user(user_data)
```

**Правило:** Больше 3-4 параметров — используй словарь или структуру данных.

---

## 🎯 Пример: До и После

### ❌ Плохой код

```python
def f(x, y):
    print("Calculating...")
    r = x + y
    print("Result:", r)
    if r > 100:
        print("Big number!")
        with open("log.txt", "a") as f:
            f.write(f"{r}\n")
    return r

result = f(50, 60)
```

**Проблемы:**
- Непонятное название `f`
- Непонятные параметры `x`, `y`
- Смешивание вычислений и вывода
- Несколько задач в одной функции

---

### ✅ Хороший код

```python
def calculate_sum(first_number, second_number):
    """
    Вычислить сумму двух чисел.

    Args:
        first_number: Первое число
        second_number: Второе число

    Returns:
        Сумма двух чисел
    """
    return first_number + second_number

def is_big_number(number):
    """Проверить, большое ли число (> 100)."""
    return number > 100

def log_number(number, filename="log.txt"):
    """Записать число в файл."""
    with open(filename, "a") as file:
        file.write(f"{number}\n")

def show_result(number):
    """Показать результат вычисления."""
    print(f"Result: {number}")
    if is_big_number(number):
        print("Big number!")

# Использование
result = calculate_sum(50, 60)
show_result(result)

if is_big_number(result):
    log_number(result)
```

**Преимущества:**
- ✅ Понятные названия
- ✅ Каждая функция делает **одно дело**
- ✅ Чистые функции (без print в вычислениях)
- ✅ Легко тестировать
- ✅ Легко переиспользовать

---

## ⚡ Чек-лист хорошей функции

✅ **Название говорит, ЧТО делает** (глагол + объект)
✅ **Одна функция — одна задача** (SRP)
✅ **Возвращает результат, не печатает** (чистая функция)
✅ **Понятные имена параметров**
✅ **Не изменяет аргументы**
✅ **Есть документация** (docstring)
✅ **Длина до 20-30 строк** (помещается на экран)
✅ **Максимум 3-4 параметра**
✅ **Использует значения по умолчанию** (где нужно)
✅ **Легко протестировать**

---

## 🎯 Пример: Банковская система

### ❌ Плохо

```python
def process(acc, amt, t):
    print("Processing...")
    if t == "d":
        acc["b"] += amt
        print("Done")
    elif t == "w":
        if acc["b"] >= amt:
            acc["b"] -= amt
            print("Done")
        else:
            print("Error")
    print(f"Balance: {acc['b']}")
```

---

### ✅ Хорошо

```python
def deposit(account, amount):
    """
    Пополнить счёт.

    Args:
        account: Словарь со счётом
        amount: Сумма пополнения

    Returns:
        Обновлённый баланс
    """
    account["balance"] += amount
    return account["balance"]

def withdraw(account, amount):
    """
    Снять деньги со счёта.

    Args:
        account: Словарь со счётом
        amount: Сумма снятия

    Returns:
        Обновлённый баланс или None, если недостаточно средств
    """
    if amount > account["balance"]:
        return None

    account["balance"] -= amount
    return account["balance"]

def show_balance(account):
    """Показать баланс счёта."""
    print(f"Баланс: {account['balance']} руб.")

# Использование
account = {"name": "Алиса", "balance": 1000}

new_balance = deposit(account, 500)
if new_balance:
    print(f"Пополнено! Новый баланс: {new_balance}")

new_balance = withdraw(account, 200)
if new_balance is not None:
    print(f"Снято! Новый баланс: {new_balance}")
else:
    print("Недостаточно средств!")

show_balance(account)
```

---

## 🎓 Резюме

**Золотые правила функций:**

1. **Имя = действие** (глагол + что делает)
2. **Одна задача** (SRP — Single Responsibility)
3. **Чистая функция** (return, не print)
4. **Понятные параметры** (названия говорят сами за себя)
5. **Не меняй аргументы** (возвращай новое значение)
6. **Документируй** (docstring обязателен)
7. **Короткая** (до 30 строк)
8. **Мало параметров** (до 4)
9. **Тестируемая** (легко проверить)
10. **Переиспользуемая** (можно применять в разных местах)

**Принцип:** Функция должна **говорить сама за себя**. Если нужно читать код внутри — название плохое!

---

## 🔗 Связанные темы

- <a href="/ru/blog/article/python-functions-basics/" target="_blank">Основы функций 📦</a>
- <a href="/ru/blog/article/python-clean-code-comments/" target="_blank">Чистый код: Комментарии 💬</a>
- <a href="/ru/blog/article/python-kiss-principle/" target="_blank">KISS: Пиши просто 🎯</a>
- <a href="/ru/blog/article/python-dry-principle/" target="_blank">DRY: Не повторяйся 🔄</a>

Теперь твои функции **говорят сами за себя**! 🎯✨
