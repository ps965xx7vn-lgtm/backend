# Логические операторы в Python: and, or, not 🔗

**Одно условие это хорошо.** Но что если нужно проверить **несколько условий сразу**?

Представь: пустят на аттракцион только если `возраст >= 10 И рост >= 140`
Или: выходной если `суббота ИЛИ воскресенье`

Логические операторы помогают **объединять условия**!

## 🤝 Оператор AND - оба должны быть правдой

**`and`** = "И" = все условия должны быть True

### Синтаксис:

```python
if условие1 and условие2:
    код выполнится только если ОБА True
```

### Пример:

```python
age = 17
has_license = True

if age >= 16 and has_license:
    print("Можешь водить скутер! 🛵")
else:
    print("Пока нельзя")
```

**Что происходит:**
- `age >= 16` → `17 >= 16` → True ✅
- `has_license` → True ✅
- True **and** True → **True** → код выполняется!

Измени `age = 15`:
- `15 >= 16` → False ❌
- True **and** False → **False** → код НЕ выполняется

### Реальный пример - доступ к фильму:

```python
age = int(input("Возраст: "))
has_ticket = input("Есть билет? (да/нет): ") == "да"

if age >= 16 and has_ticket:
    print("🎬 Проходи, приятного просмотра!")
else:
    if age < 16:
        print("❌ Фильм с 16 лет")
    elif not has_ticket:
        print("❌ Нужен билет")
```

### Можно больше двух условий:

```python
age = 18
has_license = True
has_car = True

if age >= 18 and has_license and has_car:
    print("🚗 Можешь ехать!")
else:
    print("❌ Условия не выполнены")
```

**Все три должны быть True!**

## 💫 Оператор OR - хотя бы одно правда

**`or`** = "ИЛИ" = достаточно одного True

### Синтаксис:

```python
if условие1 or условие2:
    код выполнится если ХОТЯ БЫ ОДНО True
```

### Пример:

```python
day = input("Какой день? ")

if day == "суббота" or day == "воскресенье":
    print("🎉 Выходной!")
else:
    print("📚 Будний день")
```

**Что происходит:**
- Если "суббота" → первое True → результат True
- Если "воскресенье" → второе True → результат True
- Если "понедельник" → оба False → результат False

### Проверка прав доступа:

```python
role = "admin"

if role == "admin" or role == "moderator":
    print("✅ Доступ к админке разрешён")
else:
    print("❌ Доступ запрещён")
```

### Несколько `or`:

```python
grade = input("Оценка: ")

if grade == "A" or grade == "B" or grade == "C":
    print("✅ Зачёт!")
else:
    print("❌ Не зачёт")
```

**Хотя бы одна из оценок A, B или C → зачёт**

## 🔄 Оператор NOT - инверсия (переворачивание)

**`not`** = "НЕ" = переворачивает True в False и наоборот

### Синтаксис:

```python
if not условие:
    код выполнится если условие False
```

### Пример:

```python
is_raining = False

if not is_raining:
    print("☀️ Можно гулять!")
else:
    print("☔ Останься дома")
```

**Что происходит:**
- `is_raining` → False
- `not False` → True
- Код выполняется!

### С переменными:

```python
is_logged_in = False

if not is_logged_in:
    print("❌ Пожалуйста, войди в систему")
else:
    print("✅ Добро пожаловать!")
```

### NOT с операторами:

```python
age = 15

if not age >= 18:  # То же что: age < 18
    print("Ты младше 18")
```

**Хотя чаще пишут просто:**

```python
if age < 18:
    print("Ты младше 18")
```

## 📊 Таблицы истинности

### AND - все должны быть True:

```python
True  and True   = True   # Только этот случай даёт True!
True  and False  = False
False and True   = False
False and False  = False
```

**Простое правило:** Хотя бы один False → результат False

### OR - хотя бы один True:

```python
True  or True   = True
True  or False  = True   # Любой True → результат True
False or True   = True
False or False  = False  # Только оба False → результат False
```

**Простое правило:** Хотя бы один True → результат True

### NOT - переворачивает:

```python
not True  = False
not False = True
```

## 🎯 Комбинирование операторов

Можно объединять `and`, `or`, `not`!

### Пример - доступ к аттракциону:

```python
age = int(input("Возраст: "))
height = int(input("Рост (см): "))

# Пустят если:
# (возраст >= 10 И рост >= 140) ИЛИ возраст >= 16

if (age >= 10 and height >= 140) or age >= 16:
    print("🎢 Проходи!")
else:
    print("❌ К сожалению, нельзя")
```

**Рассмотрим случаи:**
1. Возраст 12, рост 145: (12≥10 and 145≥140) → True → пускают ✅
2. Возраст 9, рост 145: (9≥10 and 145≥140) → False, 9≥16 → False → не пускают ❌
3. Возраст 17, рост 130: (17≥10 and 130≥140) → False, но 17≥16 → True → пускают! ✅

### Сложный пример - VIP доступ:

```python
age = 20
is_member = True
has_discount = False

# VIP если:
# (возраст >= 18 И member) ИЛИ (NOT has_discount И возраст >= 21)

if (age >= 18 and is_member) or (not has_discount and age >= 21):
    print("⭐ VIP доступ!")
else:
    print("🎫 Обычный доступ")
```

**Используй скобки** для ясности!

## 📍 Приоритет операций

При использовании нескольких операторов:

1. **Сначала `not`**
2. **Потом `and`**
3. **Потом `or`**

### Пример:

```python
x = True
y = False
z = True

result = not x and y or z
# Выполняется так:
# 1. not x → not True → False
# 2. False and y → False and False → False
# 3. False or z → False or True → True
# Итог: True
```

**Совет:** Лучше используй скобки чтобы было понятнее!

```python
result = ((not x) and y) or z  # Так яснее!
```

## 💡 Реальные примеры

### 1. Проверка пароля:

```python
password = input("Пароль: ")
length_ok = len(password) >= 8
has_digit = any(char.isdigit() for char in password)

if length_ok and has_digit:
    print("✅ Пароль надёжный")
else:
    if not length_ok:
        print("❌ Пароль слишком короткий (нужно >= 8)")
    if not has_digit:
        print("❌ Пароль должен содержать цифру")
```

### 2. Определение сезона:

```python
month = int(input("Месяц (1-12): "))

if month == 12 or month == 1 or month == 2:
    season = "Зима ❄️"
elif month >= 3 and month <= 5:
    season = "Весна 🌸"
elif month >= 6 and month <= 8:
    season = "Лето ☀️"
elif month >= 9 and month <= 11:
    season = "Осень 🍂"
else:
    season = "Некорректный месяц"

print(season)
```

### 3. Валидация email (упрощённая):

```python
email = input("Email: ")

has_at = "@" in email
has_dot = "." in email
not_empty = len(email) > 0

if has_at and has_dot and not_empty:
    print("✅ Email выглядит корректно")
else:
    print("❌ Email некорректный")
```

### 4. Игра - можно ли атаковать:

```python
health = 80
mana = 30
has_weapon = True

# Атаковать можно если:
# здоровье > 20 И (мана >= 10 ИЛИ есть оружие)

if health > 20 and (mana >= 10 or has_weapon):
    print("⚔️ Атака!")
else:
    print("🛡️ Защита...")
```

## ⚠️ Частые ошибки

### 1. Лишний повтор переменной:

```python
# ❌ Неправильно:
if age >= 10 and >= 18:
    print("OK")

# ✅ Правильно:
if age >= 10 and age <= 18:
    print("OK")

# ✅ Ещё лучше (Python фишка):
if 10 <= age <= 18:
    print("OK")
```

### 2. Использование `=` вместо `==`:

```python
# ❌ Присваивание!
if age = 18 and has_ticket:
    print("OK")

# ✅ Проверка:
if age == 18 and has_ticket:
    print("OK")
```

### 3. Путаница `and` и `or`:

```python
# Задача: пустить если ЛИБО возраст >= 18, ЛИБО есть parents

# ❌ Неправильно (нужно И ТО И ДР УГОЕуётоЕ!):
if age >= 18 and has_parents:
    print("OK")

# ✅ Правильно (достаточно ОДНОГО):
if age >= 18 or has_parents:
    print("OK")
```

### 4. Забыл ключевое слово:

```python
# ❌ Забыл слово 'and':
if age >= 10 height >= 140:
    print("OK")

# ✅ Правильно:
if age >= 10 and height >= 140:
    print("OK")
```

## 🎮 Практические задачи

### Лёгкий уровень:

**1. Проверка диапазона**
Число в диапазоне 10-20 включительно?

**2. Выходной день**
День "суббота" или "воскресенье"?

**3. НЕ чётное**
Число НЕ чётное? (используй `not`)

### Средний уровень:

**4. Допуск к экзамену**
Допустят если: (посещаемость > 80% И все ДЗ сданы) ИЛИ есть индивидуальный план

**5. Скидка**
Скидка 20% если: (покупка >= 5000 И есть карта) ИЛИ покупка >= 10000

**6. Можно ли водить**
Разрешение если: возраст >= 18 И есть права И НЕ лишён прав

### Сложный уровень:

**7. Доступ к курсу**
Доступ если: (student И оплачено) ИЛИ (teacher) ИЛИ (admin И НЕ заблокирован)

**8. Определение типа треугольника**
По трём сторонам определи: равносторонний / равнобедренный / разносторонний

## 🚀 Итого

**Ты научился:**

✅ Использовать `and` чтобы требовать ВСЕ условия
✅ Использовать `or` когда достаточно ОДНОГО условия
✅ Использовать `not` для инверсии
✅ Комбинировать операторы
✅ Понимать приоритет операций
✅ Избегать распространённых ошибок

**С логическими операторами твои программы становятся намного умнее!** 🧠

---

**Практикуйся в CodeHS!** Создавай программы с разными комбинациями условий. Экспериментируй! 💪
