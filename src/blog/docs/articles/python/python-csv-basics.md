# CSV: Работа с таблицами 📊

**Цель:** Научиться читать и записывать табличные данные в формате CSV.

---

## 🤔 Что такое CSV?

**CSV** (Comma-Separated Values) — формат текстовых файлов для хранения **табличных данных**.

**Пример CSV файла:**
```csv
name,age,balance
Алиса,25,1000
Боб,30,500
Чарли,22,2000
```

**Как выглядит в Excel:**
| name | age | balance |
|------|-----|---------|
| Алиса | 25 | 1000 |
| Боб | 30 | 500 |
| Чарли | 22 | 2000 |

**Особенности:**
- ✅ Простой текстовый формат
- ✅ Открывается в Excel, Google Sheets
- ✅ Используется для экспорта/импорта данных
- ✅ Встроенная поддержка в Python!

---

## 📝 Импорт модуля CSV

```python
import csv
```

**Основные функции:**
- `csv.writer()` — записать CSV
- `csv.reader()` — прочитать CSV
- `csv.DictWriter()` — запись со словарями
- `csv.DictReader()` — чтение со словарями

---

## 💾 Запись CSV - csv.writer()

### Простая запись

```python
import csv

# Данные для записи
data = [
    ["name", "age", "balance"],
    ["Алиса", 25, 1000],
    ["Боб", 30, 500],
    ["Чарли", 22, 2000]
]

# Запись в файл
with open("users.csv", "w", encoding="utf-8", newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)  # Записываем все строки

print("CSV файл создан!")
```

**Что происходит:**
1. `csv.writer(file)` — создаём объект для записи
2. `writerows(data)` — записываем все строки разом
3. Файл `users.csv` создан!

**Результат (users.csv):**
```csv
name,age,balance
Алиса,25,1000
Боб,30,500
Чарли,22,2000
```

---

### Запись построчно

```python
import csv

with open("accounts.csv", "w", encoding="utf-8", newline='') as file:
    writer = csv.writer(file)

    # Заголовки
    writer.writerow(["name", "balance", "status"])

    # Данные
    writer.writerow(["Алиса", 1000, "active"])
    writer.writerow(["Боб", 500, "blocked"])

print("Готово!")
```

**`writerow()`** — записать **одну** строку
**`writerows()`** — записать **несколько** строк

---

## 📂 Чтение CSV - csv.reader()

```python
import csv

with open("users.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)

    for row in reader:
        print(row)

# Вывод:
# ['name', 'age', 'balance']
# ['Алиса', '25', '1000']
# ['Боб', '30', '500']
# ['Чарли', '22', '2000']
```

**Что происходит:**
- `csv.reader(file)` — создаём читатель
- Каждая строка — **список строк**
- Первая строка — заголовки

---

### Пропуск заголовков

```python
import csv

with open("users.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Пропускаем первую строку (заголовки)

    for row in reader:
        name = row[0]
        age = int(row[1])
        balance = int(row[2])
        print(f"{name}: {age} лет, баланс {balance} руб.")

# Вывод:
# Алиса: 25 лет, баланс 1000 руб.
# Боб: 30 лет, баланс 500 руб.
# Чарли: 22 лет, баланс 2000 руб.
```

**`next(reader)`** — прочитать и пропустить одну строку.

---

## 📚 Работа со словарями - DictWriter/DictReader

### Запись со словарями - csv.DictWriter()

```python
import csv

accounts = [
    {"name": "Алиса", "balance": 1000, "currency": "RUB"},
    {"name": "Боб", "balance": 500, "currency": "USD"},
    {"name": "Чарли", "balance": 2000, "currency": "RUB"}
]

with open("accounts.csv", "w", encoding="utf-8", newline='') as file:
    fields = ["name", "balance", "currency"]
    writer = csv.DictWriter(file, fieldnames=fields)

    writer.writeheader()    # Записываем заголовки
    writer.writerows(accounts)  # Записываем данные

print("CSV создан!")
```

**Преимущества:**
- ✅ Работа со словарями (удобнее)
- ✅ Не нужно помнить порядок колонок
- ✅ Автоматические заголовки

---

### Чтение со словарями - csv.DictReader()

```python
import csv

with open("accounts.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        print(f"{row['name']}: {row['balance']} {row['currency']}")

# Вывод:
# Алиса: 1000 RUB
# Боб: 500 USD
# Чарли: 2000 RUB
```

**Каждая строка — словарь!**
- Ключи — названия колонок
- Значения — данные из строки

---

## 🎯 Пример: Экспорт транзакций банка

```python
import csv

class BankAccount:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.transactions = []

    def deposit(self, amount):
        """Пополнить счёт."""
        self.balance += amount
        self.transactions.append({
            "type": "deposit",
            "amount": amount,
            "balance": self.balance
        })

    def withdraw(self, amount):
        """Снять деньги."""
        if amount > self.balance:
            return False

        self.balance -= amount
        self.transactions.append({
            "type": "withdraw",
            "amount": amount,
            "balance": self.balance
        })
        return True

    def export_transactions(self, filename):
        """Экспортировать транзакции в CSV."""
        with open(filename, "w", encoding="utf-8", newline='') as file:
            fields = ["type", "amount", "balance"]
            writer = csv.DictWriter(file, fieldnames=fields)

            writer.writeheader()
            writer.writerows(self.transactions)

        print(f"Транзакции экспортированы в {filename}")

# Использование
account = BankAccount("Алиса", 1000)
account.deposit(500)
account.withdraw(200)
account.deposit(300)
account.export_transactions("alice_transactions.csv")
```

**Результат (alice_transactions.csv):**
```csv
type,amount,balance
deposit,500,1500
withdraw,200,1300
deposit,300,1600
```

---

## 🎯 Пример: Экспорт всех счетов банка

```python
import csv

class Bank:
    def __init__(self):
        self.accounts = []

    def create_account(self, name, balance=0):
        """Создать счёт."""
        account = {"name": name, "balance": balance}
        self.accounts.append(account)

    def export_all_accounts(self, filename):
        """Экспортировать все счета в CSV."""
        with open(filename, "w", encoding="utf-8", newline='') as file:
            fields = ["name", "balance"]
            writer = csv.DictWriter(file, fieldnames=fields)

            writer.writeheader()
            writer.writerows(self.accounts)

        print(f"Все счета экспортированы в {filename}")

# Использование
bank = Bank()
bank.create_account("Алиса", 1000)
bank.create_account("Боб", 500)
bank.create_account("Чарли", 2000)
bank.export_all_accounts("bank_accounts.csv")
```

**Результат (bank_accounts.csv):**
```csv
name,balance
Алиса,1000
Боб,500
Чарли,2000
```

---

## 🛡️ Безопасное чтение CSV

```python
import csv

def load_accounts_from_csv(filename):
    """Загрузить счета из CSV."""
    accounts = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    account = {
                        "name": row["name"],
                        "balance": float(row["balance"])
                    }
                    accounts.append(account)
                except (KeyError, ValueError) as e:
                    print(f"Ошибка в строке: {row}. Пропускаем.")

        print(f"Загружено {len(accounts)} счетов")
        return accounts

    except FileNotFoundError:
        print("Файл не найден!")
        return []

# Использование
accounts = load_accounts_from_csv("bank_accounts.csv")
for account in accounts:
    print(f"{account['name']}: {account['balance']} руб.")
```

---

## 📊 Использование разделителей

По умолчанию CSV использует запятую `,`, но можно изменить:

### Точка с запятой (`;`)

```python
import csv

data = [["name", "balance"], ["Алиса", 1000]]

with open("data.csv", "w", encoding="utf-8", newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerows(data)

# Результат: name;balance
```

### Табуляция (`\t`)

```python
writer = csv.writer(file, delimiter='\t')
```

---

## ⚡ Лучшие практики

### ✅ Делай:
1. **Используй `encoding="utf-8"`** для кириллицы
2. **Используй `newline=''`** при записи
3. **Используй DictWriter/DictReader** для удобства
4. **Оборачивай в try/except** чтение файлов
5. **Валидируй данные** при чтении

### ❌ Не делай:
1. **Не забывай заголовки** (`writeheader()`)
2. **Не смешивай разделители**
3. **Не игнорируй ошибки** при чтении

---

## 🎓 Резюме

**CSV - это:**
- ✅ Табличный формат данных
- ✅ Открывается в Excel
- ✅ Простой экспорт/импорт
- ✅ Встроенная поддержка в Python

**Основные функции:**
- `csv.writer()` → запись списков
- `csv.reader()` → чтение списков
- `csv.DictWriter()` → запись словарей
- `csv.DictReader()` → чтение словарей

**Золотое правило:** Используй `DictWriter/DictReader` для работы со словарями — это удобнее и понятнее!

---

## 🔗 Связанные темы

- <a href="/ru/blog/article/python-json-basics/" target="_blank">JSON: Сохранение данных 💾</a>
- <a href="/ru/blog/article/python-with-statement/" target="_blank">With: Работа с файлами 📄</a>
- <a href="/ru/blog/article/python-exceptions/" target="_blank">Try/Except: Обработка ошибок ❗</a>

Теперь ты можешь **экспортировать данные в Excel**! 📊✨
