# Try/Except: Укрощение ошибок ❗

**Цель:** Научиться обрабатывать ошибки и делать программы надёжными.

---

## 🤔 Почему программы падают?

Представь: ты пишешь калькулятор. Пользователь вводит `10 / 0`. Программа КРАШИТСЯ! 💥

```python
number = 10 / 0  # ZeroDivisionError: division by zero
```

**Проблема:** Python не знает, что делать, когда что-то идёт не так.

**Решение:** Научить программу **обрабатывать ошибки** с помощью `try/except`.

---

## 🛡️ Базовый синтаксис Try/Except

```python
try:
    # Опасный код, который может упасть
    result = 10 / 0
except:
    # Что делать, если произошла ошибка
    print("Произошла ошибка!")
```

**Как это работает:**
1. Python **пытается** (`try`) выполнить код
2. Если возникает ошибка, переходит в блок `except`
3. Программа **не падает**, а продолжает работу!

---

## 🎯 Ловим конкретные ошибки

**Плохо:** Ловить все ошибки подряд
```python
try:
    result = int("abc")
except:
    print("Ошибка!")  # Какая именно? Непонятно!
```

**Хорошо:** Ловить конкретный тип ошибки
```python
try:
    result = int("abc")
except ValueError:
    print("Это не число! Введите число.")
```

**Зачем это нужно:**
- Разные ошибки требуют разных действий
- Легче понять, что пошло не так
- Код становится надёжнее

---

## 📋 Популярные типы ошибок

### 1. **ValueError** - неверное значение
```python
try:
    age = int("двадцать")  # Нельзя преобразовать текст в число
except ValueError:
    print("Введите число цифрами!")
```

**Когда возникает:**
- `int("abc")` - преобразование невалидного текста
- `float("xyz")` - то же для дробных чисел

---

### 2. **ZeroDivisionError** - деление на ноль
```python
try:
    result = 100 / 0
except ZeroDivisionError:
    print("Нельзя делить на ноль!")
```

**Когда возникает:**
- Любое деление на ноль
- Математические операции с нулевым знаменателем

---

### 3. **FileNotFoundError** - файл не найден
```python
try:
    with open("missing.txt", "r") as f:
        data = f.read()
except FileNotFoundError:
    print("Файл не найден! Проверьте путь.")
```

**Когда возникает:**
- Попытка открыть несуществующий файл
- Неверный путь к файлу

---

### 4. **TypeError** - неверный тип данных
```python
try:
    result = "5" + 10  # Нельзя складывать строку и число
except TypeError:
    print("Несовместимые типы данных!")
```

**Когда возникает:**
- Операции между несовместимыми типами
- Вызов функции с неправильными аргументами

---

### 5. **KeyError** - ключ не найден в словаре
```python
try:
    user = {"name": "Alice"}
    age = user["age"]  # Ключа "age" нет!
except KeyError:
    print("Такого ключа нет в словаре!")
```

**Когда возникает:**
- Обращение к несуществующему ключу словаря
- Попытка получить значение по отсутствующему ключу

---

### 6. **IndexError** - индекс вне диапазона
```python
try:
    numbers = [1, 2, 3]
    print(numbers[10])  # Индекса 10 нет!
except IndexError:
    print("Индекс вне диапазона списка!")
```

**Когда возникает:**
- Обращение к несуществующему индексу списка
- Попытка получить элемент за пределами списка

---

## 🎭 Несколько Except блоков

Можно обрабатывать разные ошибки по-разному:

```python
try:
    age = int(input("Ваш возраст: "))
    result = 100 / age
except ValueError:
    print("Введите число!")
except ZeroDivisionError:
    print("Возраст не может быть нулём!")
```

**Порядок важен:**
- Сначала конкретные ошибки
- Потом общие (если нужно)

---

## 📦 Получение информации об ошибке

```python
try:
    number = int("abc")
except ValueError as e:
    print(f"Ошибка: {e}")
    # Вывод: Ошибка: invalid literal for int() with base 10: 'abc'
```

**Переменная `e`:**
- Содержит объект исключения
- Можно вывести подробности
- Полезно для логирования

---

## 🧹 Блок Finally - всегда выполняется

```python
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("Файл не найден!")
finally:
    print("Этот код выполнится в любом случае")
    # Закрыть файл, очистить ресурсы и т.д.
```

**Когда использовать `finally`:**
- Закрытие файлов
- Освобождение ресурсов
- Очистка временных данных
- Код, который **должен выполниться** независимо от ошибок

**Пример с файлами:**
```python
file = None
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("Файл не найден!")
finally:
    if file:
        file.close()  # Гарантировано закроем файл
```

> **Примечание:** С `with open()` `finally` не нужен — файл закрывается автоматически!

---

## 🔄 Блок Else - если ошибок не было

```python
try:
    age = int(input("Возраст: "))
except ValueError:
    print("Это не число!")
else:
    print(f"Ваш возраст: {age}")
    # Выполнится, только если НЕ было ошибки
```

**Когда использовать `else`:**
- Код, который должен выполниться **только при успехе**
- Логика, которая зависит от успешного `try`

---

## ⚠️ Когда НЕ нужен Try/Except

### ❌ Плохо: Скрывать проблемы
```python
try:
    hacky_code_here()
except:
    pass  # Игнорируем все ошибки - ПЛОХО!
```

**Почему плохо:**
- Скрывает реальные проблемы в коде
- Сложно найти баги
- Может привести к непредсказуемому поведению

### ❌ Плохо: Заменять проверки
```python
# Плохо
try:
    if user["age"] > 18:
        print("Совершеннолетний")
except KeyError:
    print("Возраст неизвестен")

# Хорошо
if "age" in user and user["age"] > 18:
    print("Совершеннолетний")
else:
    print("Возраст неизвестен")
```

**Правило:** Если можно проверить условие **до** ошибки, лучше это сделать!

---

## ✅ Когда НУЖЕН Try/Except

### ✅ Работа с файлами
```python
try:
    with open("data.txt", "r") as f:
        data = f.read()
except FileNotFoundError:
    print("Создаём новый файл...")
    with open("data.txt", "w") as f:
        f.write("Начальные данные")
```

### ✅ Ввод пользователя
```python
while True:
    try:
        age = int(input("Введите возраст: "))
        break  # Успех! Выходим из цикла
    except ValueError:
        print("Это не число! Попробуйте ещё раз.")
```

### ✅ Работа с сетью/API
```python
try:
    response = api.get_data()
except ConnectionError:
    print("Нет подключения к интернету!")
except TimeoutError:
    print("Сервер не отвечает!")
```

### ✅ Преобразование данных
```python
try:
    data = json.loads(json_string)
except json.JSONDecodeError:
    print("Невалидный JSON!")
```

---

## 🎯 Паттерн: Безопасный ввод

**Задача:** Запрашивать число, пока пользователь не введёт корректное значение.

```python
def get_number(prompt):
    """Безопасный ввод числа с повторными попытками."""
    while True:
        try:
            value = int(input(prompt))
            return value  # Успех! Возвращаем число
        except ValueError:
            print("Ошибка! Введите целое число.")

# Использование
age = get_number("Введите ваш возраст: ")
print(f"Вам {age} лет")
```

**Преимущества:**
- Программа не падает
- Пользователь получает понятные сообщения
- Можно повторить ввод

---

## 🎯 Паттерн: Значение по умолчанию

```python
def get_setting(key, default=None):
    """Получить настройку или вернуть значение по умолчанию."""
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            return settings[key]
    except (FileNotFoundError, KeyError):
        return default

# Использование
theme = get_setting("theme", "dark")  # Вернёт "dark", если файла нет
```

---

## 🎯 Паттерн: Retry (повторные попытки)

```python
def save_data(data, attempts=3):
    """Сохранить данные с повторными попытками."""
    for attempt in range(attempts):
        try:
            with open("data.json", "w") as f:
                json.dump(data, f)
            print("Данные сохранены!")
            return True
        except IOError:
            print(f"Попытка {attempt + 1} не удалась...")

    print("Не удалось сохранить данные!")
    return False
```

---

## ⚡ Лучшие практики

### ✅ Делай:
1. **Ловить конкретные исключения** (`except ValueError:`)
2. **Давать понятные сообщения** ("Введите число от 1 до 100")
3. **Логировать ошибки** (print или запись в файл)
4. **Использовать finally** для очистки ресурсов
5. **Делать узкий try блок** (только опасный код)

### ❌ Не делай:
1. **Не используй голый except:** (без указания типа ошибки)
2. **Не игнорируй ошибки** (`except: pass`)
3. **Не делай try слишком широким** (весь код в try)
4. **Не скрывай баги** (try/except вместо исправления)

---

## 📝 Пример: Валидация банковского счёта

```python
class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        """Пополнить счёт."""
        try:
            amount = float(amount)  # Преобразуем в число

            if amount <= 0:
                print("Сумма должна быть положительной!")
                return False

            self.balance += amount
            print(f"Пополнено: {amount} руб. Баланс: {self.balance} руб.")
            return True

        except ValueError:
            print("Введите число!")
            return False

    def withdraw(self, amount):
        """Снять деньги."""
        try:
            amount = float(amount)

            if amount <= 0:
                print("Сумма должна быть положительной!")
                return False

            if amount > self.balance:
                print("Недостаточно средств!")
                return False

            self.balance -= amount
            print(f"Снято: {amount} руб. Осталось: {self.balance} руб.")
            return True

        except ValueError:
            print("Введите число!")
            return False

# Использование
account = BankAccount(1000)
account.deposit("500")      # ОК
account.deposit("abc")      # Ошибка валидации
account.withdraw("2000")    # Недостаточно средств
account.withdraw("300")     # ОК
```

---

## 🎓 Резюме

**Try/Except - это:**
- ✅ Защита от падения программы
- ✅ Обработка непредсказуемых ситуаций
- ✅ Улучшение пользовательского опыта
- ✅ Надёжность кода

**Золотое правило:** Используй `try/except` там, где **не можешь предсказать** результат (ввод пользователя, файлы, сеть), но **не используй** вместо обычных проверок!

**Структура:**
```python
try:
    # Опасный код
    ...
except SpecificError:
    # Обработка конкретной ошибки
    ...
except AnotherError as e:
    # Обработка другой ошибки
    print(f"Ошибка: {e}")
else:
    # Выполнится, если ошибок не было
    ...
finally:
    # Выполнится в любом случае
    ...
```

---

## 🔗 Связанные темы

- <a href="/ru/blog/article/python-function-best-practices/" target="_blank">Лучшие практики функций 🎯</a>
- <a href="/ru/blog/article/python-json-basics/" target="_blank">JSON: Сохранение данных 💾</a>
- <a href="/ru/blog/article/python-with-statement/" target="_blank">With: Работа с файлами 📄</a>

Теперь твой код **не падает**, а **грациозно обрабатывает ошибки**! 🛡️
