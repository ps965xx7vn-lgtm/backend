# JSON: Сохранение данных как в большой игре 💾

**Цель:** Научиться сохранять и загружать данные в формате JSON.

---

## 🤔 Зачем сохранять данные?

Представь: ты создал игру, пользователь играл 2 часа, набрал 1000 очков... и закрыл программу. Открывает снова — всё обнулилось! 😱

**Проблема:** Переменные в Python живут только пока программа работает.

**Решение:** Сохранять данные в **файл**, чтобы они остались навсегда!

---

## 📦 Что такое JSON?

**JSON** (JavaScript Object Notation) — это формат текстовых файлов для хранения данных.

**Выглядит почти как словарь Python:**
```json
{
  "name": "Алиса",
  "age": 25,
  "balance": 1000.50,
  "transactions": ["deposit", "withdraw", "deposit"]
}
```

**Почему JSON так популярен:**
- ✅ Читается людьми (не бинарный код)
- ✅ Поддерживается всеми языками программирования
- ✅ Используют сайты, API, базы данных
- ✅ Встроенная поддержка в Python!

---

## 🔄 Python ⇔ JSON - Соответствие типов

| Python | JSON |
|--------|------|
| `dict` | Object `{}` |
| `list` | Array `[]` |
| `str` | String `"текст"` |
| `int`, `float` | Number `42`, `3.14` |
| `True`, `False` | `true`, `false` |
| `None` | `null` |

**Пример:**
```python
# Python данные
data = {
    "name": "Иван",
    "scores": [10, 20, 30],
    "is_active": True,
    "balance": None
}

# В JSON файле это будет:
# {
#   "name": "Иван",
#   "scores": [10, 20, 30],
#   "is_active": true,
#   "balance": null
# }
```

---

## 📝 Импорт модуля JSON

```python
import json
```

**Основные функции:**
- `json.dump()` — сохранить в файл
- `json.dumps()` — преобразовать в строку
- `json.load()` — загрузить из файла
- `json.loads()` — преобразовать из строки

---

## 💾 Сохранение данных - json.dump()

### Сохранение простых данных

```python
import json

user = {
    "name": "Алиса",
    "age": 25,
    "balance": 1000
}

# Открываем файл для записи и сохраняем
with open("user.json", "w", encoding="utf-8") as file:
    json.dump(user, file)

print("Данные сохранены!")
```

**Что происходит:**
1. `open("user.json", "w")` — открываем файл для записи
2. `json.dump(user, file)` — записываем словарь в файл
3. Файл `user.json` создан!

**Содержимое user.json:**
```json
{"name": "Алиса", "age": 25, "balance": 1000}
```

---

### Красивое форматирование - indent

```python
with open("user.json", "w", encoding="utf-8") as file:
    json.dump(user, file, indent=4, ensure_ascii=False)
```

**Параметры:**
- `indent=4` — отступы для красоты
- `ensure_ascii=False` — сохраняет кириллицу

**Результат в файле:**
```json
{
    "name": "Алиса",
    "age": 25,
    "balance": 1000
}
```

Намного читаемее! 📖

---

## 📂 Загрузка данных - json.load()

```python
import json

# Открываем файл для чтения и загружаем
with open("user.json", "r", encoding="utf-8") as file:
    user = json.load(file)

print(user["name"])    # Алиса
print(user["balance"]) # 1000
```

**Что происходит:**
1. Открываем файл в режиме чтения `"r"`
2. `json.load(file)` — читаем и преобразуем в Python словарь
3. Работаем с данными как с обычным dict!

---

## 🛡️ Безопасная загрузка с Try/Except

**Проблема:** Файл может не существовать!

```python
import json

try:
    with open("user.json", "r", encoding="utf-8") as file:
        user = json.load(file)
    print("Данные загружены!")
except FileNotFoundError:
    print("Файл не найден! Создаём новый профиль.")
    user = {"name": "Незнакомец", "age": 0, "balance": 0}
except json.JSONDecodeError:
    print("Файл повреждён! Используем значения по умолчанию.")
    user = {"name": "Незнакомец", "age": 0, "balance": 0}

print(user)
```

**Типы ошибок:**
- `FileNotFoundError` — файл не существует
- `json.JSONDecodeError` — файл повреждён (невалидный JSON)

---

## 🔄 Полный цикл: Сохранение → Изменение → Загрузка

```python
import json

# 1. Создание данных
user = {
    "name": "Алиса",
    "balance": 1000,
    "transactions": []
}

# 2. Сохранение
with open("account.json", "w", encoding="utf-8") as file:
    json.dump(user, file, indent=4, ensure_ascii=False)

print("Данные сохранены!")

# 3. Загрузка
with open("account.json", "r", encoding="utf-8") as file:
    loaded_user = json.load(file)

# 4. Изменение
loaded_user["balance"] += 500
loaded_user["transactions"].append("deposit +500")

# 5. Сохранение изменений
with open("account.json", "w", encoding="utf-8") as file:
    json.dump(loaded_user, file, indent=4, ensure_ascii=False)

print("Изменения сохранены!")
```

---

## 🎯 Пример: Банковский счёт

```python
import json

class BankAccount:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.transactions = []

    def deposit(self, amount):
        """Пополнить счёт."""
        self.balance += amount
        self.transactions.append(f"Пополнение: +{amount}")
        print(f"Пополнено: {amount} руб.")

    def withdraw(self, amount):
        """Снять деньги."""
        if amount > self.balance:
            print("Недостаточно средств!")
            return

        self.balance -= amount
        self.transactions.append(f"Снятие: -{amount}")
        print(f"Снято: {amount} руб.")

    def save(self, filename):
        """Сохранить счёт в JSON."""
        data = {
            "name": self.name,
            "balance": self.balance,
            "transactions": self.transactions
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Счёт сохранён в {filename}")

    @staticmethod
    def load(filename):
        """Загрузить счёт из JSON."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            account = BankAccount(data["name"], data["balance"])
            account.transactions = data["transactions"]
            print(f"Счёт загружен из {filename}")
            return account

        except FileNotFoundError:
            print("Файл не найден!")
            return None

# Использование
account = BankAccount("Алиса", 1000)
account.deposit(500)
account.withdraw(200)
account.save("alice.json")

# В другом месте программы или при следующем запуске
loaded = BankAccount.load("alice.json")
print(f"Баланс: {loaded.balance} руб.")
print(f"История: {loaded.transactions}")
```

**Содержимое alice.json:**
```json
{
    "name": "Алиса",
    "balance": 1300,
    "transactions": [
        "Пополнение: +500",
        "Снятие: -200"
    ]
}
```

---

## 📋 Сохранение списка объектов

**Задача:** Сохранить несколько счетов в один файл.

```python
import json

accounts = [
    {"name": "Алиса", "balance": 1000},
    {"name": "Боб", "balance": 500},
    {"name": "Чарли", "balance": 2000}
]

# Сохранение
with open("bank.json", "w", encoding="utf-8") as file:
    json.dump(accounts, file, indent=4, ensure_ascii=False)

# Загрузка
with open("bank.json", "r", encoding="utf-8") as file:
    loaded_accounts = json.load(file)

for account in loaded_accounts:
    print(f"{account['name']}: {account['balance']} руб.")
```

**Содержимое bank.json:**
```json
[
    {
        "name": "Алиса",
        "balance": 1000
    },
    {
        "name": "Боб",
        "balance": 500
    },
    {
        "name": "Чарли",
        "balance": 2000
    }
]
```

---

## 🎯 Паттерн: Автосохранение

```python
class BankAccount:
    def __init__(self, name, balance=0, filename=None):
        self.name = name
        self.balance = balance
        self.filename = filename or f"{name}.json"

    def _autosave(self):
        """Автоматическое сохранение."""
        data = {"name": self.name, "balance": self.balance}
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def deposit(self, amount):
        """Пополнить счёт с автосохранением."""
        self.balance += amount
        self._autosave()  # Сохраняем после каждого изменения!
        print(f"Пополнено: {amount}. Баланс: {self.balance}")

    def withdraw(self, amount):
        """Снять деньги с автосохранением."""
        if amount <= self.balance:
            self.balance -= amount
            self._autosave()  # Сохраняем!
            print(f"Снято: {amount}. Осталось: {self.balance}")

# Использование
account = BankAccount("Алиса", 1000)
account.deposit(500)  # Автоматически сохранится!
account.withdraw(200) # Автоматически сохранится!
```

**Преимущества:**
- ✅ Данные всегда актуальны
- ✅ Не потеряются при сбое
- ✅ Не нужно помнить про save()

---

## 📝 JSON.dumps() и JSON.loads() - работа со строками

### dumps() - в строку

```python
import json

data = {"name": "Алиса", "age": 25}
json_string = json.dumps(data, ensure_ascii=False)

print(json_string)  # {"name": "Алиса", "age": 25}
print(type(json_string))  # <class 'str'>
```

**Когда использовать:**
- Отправка данных через сеть
- Хранение в базе данных
- Логирование

---

### loads() - из строки

```python
import json

json_string = '{"name": "Боб", "balance": 500}'
data = json.loads(json_string)

print(data["name"])  # Боб
print(type(data))    # <class 'dict'>
```

**Когда использовать:**
- Получение данных из API
- Чтение из базы данных
- Парсинг конфигурации

---

## ⚠️ Что НЕЛЬЗЯ сохранить в JSON

### ❌ Функции
```python
data = {"func": print}  # Не сработает!
json.dump(data, file)   # TypeError!
```

### ❌ Объекты классов (напрямую)
```python
class User:
    def __init__(self, name):
        self.name = name

user = User("Алиса")
json.dump(user, file)  # TypeError: Object of type User is not JSON serializable
```

**Решение:** Преобразовать в словарь!
```python
user_dict = {"name": user.name}
json.dump(user_dict, file)  # Работает!
```

### ❌ Множества (set)
```python
data = {"numbers": {1, 2, 3}}  # set не поддерживается
json.dump(data, file)  # TypeError!

# Решение: преобразовать в список
data = {"numbers": list({1, 2, 3})}
```

---

## 🎯 Паттерн: Конфигурационный файл

```python
import json

# config.json
# {
#   "app_name": "MyBank",
#   "version": "1.0",
#   "debug": true,
#   "max_accounts": 100
# }

def load_config(filename="config.json"):
    """Загрузить конфигурацию."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # Значения по умолчанию
        return {
            "app_name": "MyApp",
            "version": "1.0",
            "debug": False,
            "max_accounts": 10
        }

config = load_config()
print(f"Приложение: {config['app_name']} v{config['version']}")
```

---

## 🎯 Паттерн: База данных на JSON

```python
import json

class Database:
    def __init__(self, filename="database.json"):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        """Загрузить данные."""
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _save(self):
        """Сохранить данные."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def set(self, key, value):
        """Установить значение."""
        self.data[key] = value
        self._save()

    def get(self, key, default=None):
        """Получить значение."""
        return self.data.get(key, default)

    def delete(self, key):
        """Удалить значение."""
        if key in self.data:
            del self.data[key]
            self._save()

# Использование
db = Database()
db.set("user_alice", {"balance": 1000, "age": 25})
db.set("user_bob", {"balance": 500, "age": 30})

alice = db.get("user_alice")
print(alice)  # {'balance': 1000, 'age': 25}
```

---

## 🔒 Безопасность JSON

### ⚠️ Не храни пароли открытым текстом!

```python
# ❌ Плохо
user = {
    "login": "alice",
    "password": "12345"  # НИКОГДА ТАК НЕ ДЕЛАЙ!
}

# ✅ Хорошо - хранить хеш
import hashlib

password = "12345"
password_hash = hashlib.sha256(password.encode()).hexdigest()

user = {
    "login": "alice",
    "password_hash": password_hash
}
```

---

## ⚡ Лучшие практики

### ✅ Делай:
1. **Используй encoding="utf-8"** для кириллицы
2. **Используй indent=4** для читаемости
3. **Используй ensure_ascii=False** для русских букв
4. **Оборачивай в try/except** загрузку файлов
5. **Проверяй данные** после загрузки
6. **Делай backup** перед перезаписью

### ❌ Не делай:
1. **Не храни пароли** в открытом виде
2. **Не сохраняй объекты** напрямую (только словари/списки)
3. **Не забывай about encoding** (будут крякозябры)
4. **Не игнорируй ошибки** при загрузке

---

## 📝 Пример: Полная банковская система

```python
import json

class Bank:
    def __init__(self, filename="bank_data.json"):
        self.filename = filename
        self.accounts = self._load_accounts()

    def _load_accounts(self):
        """Загрузить все счета."""
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def _save_accounts(self):
        """Сохранить все счета."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.accounts, file, indent=4, ensure_ascii=False)

    def create_account(self, name, initial_balance=0):
        """Создать новый счёт."""
        if name in self.accounts:
            print("Счёт уже существует!")
            return

        self.accounts[name] = {
            "balance": initial_balance,
            "transactions": []
        }
        self._save_accounts()
        print(f"Счёт {name} создан! Баланс: {initial_balance} руб.")

    def deposit(self, name, amount):
        """Пополнить счёт."""
        if name not in self.accounts:
            print("Счёт не найден!")
            return

        self.accounts[name]["balance"] += amount
        self.accounts[name]["transactions"].append(f"Пополнение: +{amount}")
        self._save_accounts()
        print(f"Пополнено: {amount} руб. Баланс: {self.accounts[name]['balance']} руб.")

    def withdraw(self, name, amount):
        """Снять деньги."""
        if name not in self.accounts:
            print("Счёт не найден!")
            return

        if amount > self.accounts[name]["balance"]:
            print("Недостаточно средств!")
            return

        self.accounts[name]["balance"] -= amount
        self.accounts[name]["transactions"].append(f"Снятие: -{amount}")
        self._save_accounts()
        print(f"Снято: {amount} руб. Осталось: {self.accounts[name]['balance']} руб.")

    def show_account(self, name):
        """Показать информацию о счёте."""
        if name not in self.accounts:
            print("Счёт не найден!")
            return

        account = self.accounts[name]
        print(f"\n=== Счёт: {name} ===")
        print(f"Баланс: {account['balance']} руб.")
        print("История транзакций:")
        for transaction in account["transactions"]:
            print(f"  - {transaction}")

# Использование
bank = Bank()
bank.create_account("Алиса", 1000)
bank.deposit("Алиса", 500)
bank.withdraw("Алиса", 200)
bank.show_account("Алиса")

# При следующем запуске данные загрузятся автоматически!
```

---

## 🎓 Резюме

**JSON - это:**
- ✅ Универсальный формат хранения данных
- ✅ Читаемый для людей
- ✅ Поддерживается везде
- ✅ Встроен в Python

**Основные функции:**
- `json.dump(data, file)` — сохранить в файл
- `json.load(file)` — загрузить из файла
- `json.dumps(data)` — в строку
- `json.loads(string)` — из строки

**Золотое правило:** Всегда используй `try/except` при загрузке, `encoding="utf-8"` для кириллицы и `indent=4` для красоты!

---

## 🔗 Связанные темы

- <a href="/ru/blog/article/python-exceptions/" target="_blank">Try/Except: Обработка ошибок ❗</a>
- <a href="/ru/blog/article/python-with-statement/" target="_blank">With: Работа с файлами 📄</a>
- <a href="/ru/blog/article/python-oop-basics/" target="_blank">ООП: Основы 🏗️</a>

Теперь твои данные **не исчезнут** при закрытии программы! 💾✨
