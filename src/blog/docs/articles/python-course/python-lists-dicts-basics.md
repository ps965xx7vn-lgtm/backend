# Списки и словари в Python: работай с данными 📦

**До сих пор:** одна переменная = одно значение.

**Проблема:** Хочешь хранить 1000 студентов → 1000 переменных? 😱

**Решение:** **Коллекции** - списки и словари для хранения множества данных!

## 📋 Списки (Lists) - упорядоченные коллекции

**Список** - это последовательность элементов под одним именем.

### Создание списков:

```python
# Пустой список:
empty_list = []

# Список чисел:
numbers = [1, 2, 3, 4, 5]

# Список строк:
fruits = ["яблоко", "банан", "апельсин"]

# Смешанный список (разные типы):
mixed = ["текст", 42, True, 3.14, [1, 2, 3]]
```

### Доступ к элементам (индексация):

**⚠️ ВАЖНО: Индексы начинаются с 0!**

```python
fruits = ["яблоко", "банан", "апельсин"]
#          0          1          2

print(fruits[0])   # яблоко (первый!)
print(fruits[1])   # банан
print(fruits[2])   # апельсин
print(fruits[-1])  # апельсин (последний)
print(fruits[-2])  # банан (предпоследний)
```

### Изменение элементов:

```python
fruits[1] = "груша"  # Меняем второй элемент
print(fruits)  # ["яблоко", "груша", "апельсин"]
```

### Длина списка:

```python
print(len(fruits))  # 3 элемента
```

---

## ➕ Добавление и удаление элементов

### append() - добавить в конец:

```python
fruits = ["яблоко", "банан"]
fruits.append("апельсин")
print(fruits)  # ["яблоко", "банан", "апельсин"]

fruits.append("груша")
print(fruits)  # ["яблоко", "банан", "апельсин", "груша"]
```

### insert() - вставить на позицию:

```python
fruits = ["яблоко", "апельсин"]
fruits.insert(1, "банан")  # Вставить на индекс 1
print(fruits)  # ["яблоко", "банан", "апельсин"]
```

### remove() - удалить по значению:

```python
fruits = ["яблоко", "банан", "апельсин"]
fruits.remove("банан")
print(fruits)  # ["яблоко", "апельсин"]
```

**Удаляет первое вхождение!**

### pop() - удалить по индексу (и получить значение):

```python
fruits = ["яблоко", "банан", "апельсин"]

# Удалить последний:
last = fruits.pop()
print(last)    # апельсин
print(fruits)  # ["яблоко", "банан"]

# Удалить по индексу:
first = fruits.pop(0)
print(first)   # яблоко
print(fruits)  # ["банан"]
```

### clear() - очистить весь список:

```python
fruits.clear()
print(fruits)  # []
```

---

## 🔪 Срезы (Slicing) - части списка

**Синтаксис:** `список[start:end:step]`

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Элементы с 2 по 5 (не включая 5):
print(numbers[2:5])  # [2, 3, 4]

# С начала до индекса 5:
print(numbers[:5])   # [0, 1, 2, 3, 4]

# С индекса 5 до конца:
print(numbers[5:])   # [5, 6, 7, 8, 9]

# Все элементы (копия):
print(numbers[:])    # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Каждый второй элемент:
print(numbers[::2])  # [0, 2, 4, 6, 8]

# Каждый третий:
print(numbers[::3])  # [0, 3, 6, 9]

# Перевернуть список:
print(numbers[::-1]) # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

# Последние 3 элемента:
print(numbers[-3:])  # [7, 8, 9]

# Первые 3 элемента:
print(numbers[:3])   # [0, 1, 2]
```

**Срезы создают НОВЫЙ список**, оригинал не меняется!

---

## 🔧 Полезные методы списков

### sort() - сортировать:

```python
numbers = [3, 1, 4, 1, 5, 9, 2]
numbers.sort()
print(numbers)  # [1, 1, 2, 3, 4, 5, 9]

# Обратная сортировка:
numbers.sort(reverse=True)
print(numbers)  # [9, 5, 4, 3, 2, 1, 1]
```

### reverse() - перевернуть:

```python
letters = ['A', 'B', 'C', 'D']
letters.reverse()
print(letters)  # ['D', 'C', 'B', 'A']
```

### count() - подсчитать вхождения:

```python
numbers = [1, 2, 3, 2, 4, 2, 5]
print(numbers.count(2))  # 3 (три раза встречается 2)
```

### index() - найти индекс элемента:

```python
fruits = ["яблоко", "банан", "апельсин"]
index = fruits.index("банан")
print(index)  # 1
```

### extend() - добавить несколько элементов:

```python
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list1.extend(list2)
print(list1)  # [1, 2, 3, 4, 5, 6]
```

### Проверка наличия (in):

```python
fruits = ["яблоко", "банан", "апельсин"]

if "банан" in fruits:
    print("Банан есть!")  # Выведется

if "груша" not in fruits:
    print("Груши нет")    # Выведется
```

---

## 📖 Словари (Dictionaries) - пары ключ-значение

**Списки:** доступ по индексу (0, 1, 2...)
**Словари:** доступ по **ключу** (name, age, email...)

### Создание словарей:

```python
# Пустой словарь:
empty_dict = {}

# Словарь с данными:
student = {
    "name": "Анна",
    "age": 16,
    "city": "Москва",
    "grade": 10
}

# Ключи могут быть строками или числами:
scores = {
    1: 100,
    2: 85,
    3: 92
}
```

### Доступ к значениям:

```python
student = {
    "name": "Анна",
    "age": 16,
    "city": "Москва"
}

print(student["name"])  # Анна
print(student["age"])   # 16
print(student["city"])  # Москва
```

### Изменение значений:

```python
student["age"] = 17
student["grade"] = 11
print(student)  # Возраст и класс изменены!
```

### Добавление новых ключей:

```python
student["email"] = "anna@example.com"
student["phone"] = "+7-123-456-78-90"
print(student)  # Добавлены email и phone
```

### Удаление ключей:

```python
# del - удалить ключ:
del student["phone"]

# pop() - удалить и получить значение:
email = student.pop("email")
print(email)  # anna@example.com
print(student)  # email удалён
```

---

## 🔑 Методы словарей

### get() - безопасное получение (без ошибок):

```python
student = {"name": "Анна", "age": 16}

# Обычный способ (может быть KeyError):
print(student["email"])  # ❌ KeyError!

# Безопасный способ:
email = student.get("email", "No email")
print(email)  # "No email" (default значение)

age = student.get("age", 0)
print(age)  # 16 (ключ есть)
```

### keys() - все ключи:

```python
student = {"name": "Анна", "age": 16, "city": "Москва"}

keys = student.keys()
print(keys)  # dict_keys(['name', 'age', 'city'])
print(list(keys))  # ['name', 'age', 'city']
```

### values() - все значения:

```python
values = student.values()
print(values)  # dict_values(['Анна', 16, 'Москва'])
print(list(values))  # ['Анна', 16, 'Москва']
```

### items() - пары ключ-значение:

```python
items = student.items()
print(items)
# dict_items([('name', 'Анна'), ('age', 16), ('city', 'Москва')])

# Итерация:
for key, value in student.items():
    print(f"{key}: {value}")
# name: Анна
# age: 16
# city: Москва
```

### update() - обновить несколько ключей:

```python
student = {"name": "Анна", "age": 16}

student.update({
    "age": 17,
    "city": "Москва",
    "grade": 11
})

print(student)
# {"name": "Анна", "age": 17, "city": "Москва", "grade": 11}
```

### clear() - очистить словарь:

```python
student.clear()
print(student)  # {}
```

### Проверка наличия ключа:

```python
if "name" in student:
    print("Имя есть!")

if "email" not in student:
    print("Email отсутствует")
```

---

## 🔄 Итерация по спискам и словарям

### Списки:

```python
fruits = ["яблоко", "банан", "апельсин"]

# Простая итерация:
for fruit in fruits:
    print(fruit)

# С индексом (enumerate):
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: яблоко
# 1: банан
# 2: апельсин

# С индексом начиная с 1:
for i, fruit in enumerate(fruits, 1):
    print(f"{i}. {fruit}")
# 1. яблоко
# 2. банан
# 3. апельсин
```

### Словари:

```python
student = {"name": "Анна", "age": 16, "city": "Москва"}

# Только ключи:
for key in student:
    print(key)
# name
# age
# city

# Только значения:
for value in student.values():
    print(value)
# Анна
# 16
# Москва

# Ключи и значения:
for key, value in student.items():
    print(f"{key}: {value}")
# name: Анна
# age: 16
# city: Москва
```

---

## 🎯 Практические примеры

### 1. TODO список:

```python
tasks = []

# Добавление:
tasks.append("Учёба")
tasks.append("Спорт")
tasks.append("Чтение")

# Показ:
print("📝 Мои задачи:")
for i, task in enumerate(tasks, 1):
    print(f"{i}. {task}")

# Удаление:
tasks.remove("Спорт")

# Проверка:
if "Учёба" in tasks:
    print("Учёба ещё не выполнена!")
```

### 2. Подсчёт голосов:

```python
votes = ["Python", "JavaScript", "Python", "Java", "Python", "JavaScript"]

# Подсчёт:
vote_count = {}
for vote in votes:
    if vote in vote_count:
        vote_count[vote] += 1
    else:
        vote_count[vote] = 1

print(vote_count)
# {'Python': 3, 'JavaScript': 2, 'Java': 1}

# Победитель:
winner = max(vote_count, key=vote_count.get)
print(f"Победитель: {winner}")
```

### 3. База студентов:

```python
students = [
    {"name": "Анна", "age": 16, "grade": 10},
    {"name": "Боб", "age": 17, "grade": 11},
    {"name": "Света", "age": 16, "grade": 10}
]

# Показ всех:
for student in students:
    print(f"{student['name']}, {student['age']} лет, {student['grade']} класс")

# Поиск:
search_name = "Анна"
for student in students:
    if student["name"] == search_name:
        print(f"Найдена: {student}")
        break

# Фильтр по классу:
grade_10 = [s for s in students if s["grade"] == 10]
print(f"В 10 классе: {len(grade_10)} студентов")
```

### 4. Инвентарь игры:

```python
inventory = {
    "меч": 1,
    "щит": 1,
    "зелье здоровья": 5,
    "зелье маны": 3,
    "золото": 150
}

# Показ инвентаря:
print("🎒 Инвентарь:")
for item, count in inventory.items():
    print(f"  {item}: {count}")

# Использование предмета:
if inventory["зелье здоровья"] > 0:
    inventory["зелье здоровья"] -= 1
    print("🧪 Использовал зелье здоровья!")
    print(f"Осталось: {inventory['зелье здоровья']}")

# Добавление золота:
inventory["золото"] += 50
print(f"💰 Золото: {inventory['золото']}")
```

---

## 📚 Вложенные структуры

### Список словарей:

```python
users = [
    {"username": "anna", "age": 16, "city": "Moscow"},
    {"username": "bob", "age": 18, "city": "SPb"},
    {"username": "charlie", "age": 17, "city": "Moscow"}
]

# Доступ:
print(users[0]["username"])  # anna
print(users[1]["age"])       # 18

# Поиск пользователей из Москвы:
moscow_users = [u for u in users if u["city"] == "Moscow"]
print(f"Из Москвы: {len(moscow_users)}")
```

### Словарь со списками:

```python
courses = {
    "python": ["Анна", "Боб", "Света"],
    "javascript": ["Петя", "Маша"],
    "java": ["Иван", "Катя", "Алекс"]
}

# Доступ:
print(courses["python"])  # ['Анна', 'Боб', 'Света']
print(courses["python"][0])  # Анна

# Добавление студента:
courses["python"].append("Новый студент")

# Количество студентов на курсе:
for course, students in courses.items():
    print(f"{course}: {len(students)} студентов")
```

### Словарь словарей:

```python
contacts = {
    "anna": {
        "phone": "+7-123-456",
        "email": "anna@mail.com",
        "city": "Moscow"
    },
    "bob": {
        "phone": "+7-987-654",
        "email": "bob@mail.com",
        "city": "SPb"
    }
}

# Доступ:
print(contacts["anna"]["email"])  # anna@mail.com
print(contacts["bob"]["phone"])   # +7-987-654

# Добавление нового контакта:
contacts["charlie"] = {
    "phone": "+7-555-123",
    "email": "charlie@mail.com",
    "city": "Kazan"
}
```

---

## ⚠️ Распространённые ошибки

### 1. IndexError - выход за границы:

```python
fruits = ["яблоко", "банан"]
print(fruits[2])  # ❌ IndexError!

# Решение - проверка:
if len(fruits) > 2:
    print(fruits[2])
```

### 2. KeyError - ключ не найден:

```python
student = {"name": "Анна"}
print(student["age"])  # ❌ KeyError!

# Решение - get():
age = student.get("age", 0)
print(age)  # 0
```

### 3. Изменение списка во время итерации:

```python
# ❌ Опасно:
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)  # Может пропустить элементы!

# ✅ Правильно - создай новый:
numbers = [1, 2, 3, 4, 5]
odd_numbers = [n for n in numbers if n % 2 != 0]
print(odd_numbers)  # [1, 3, 5]
```

### 4. Копирование списков:

```python
# ❌ Ссылка, не копия:
list1 = [1, 2, 3]
list2 = list1
list2[0] = 999
print(list1)  # [999, 2, 3] - изменился!

# ✅ Копия:
list1 = [1, 2, 3]
list2 = list1.copy()  # или list1[:]
list2[0] = 999
print(list1)  # [1, 2, 3] - не изменился!
```

---

## 🚀 Итого

**Списки и словари - основа работы с данными!**

Ты научился:

✅ Создавать и использовать списки
✅ Добавлять, удалять, изменять элементы
✅ Использовать срезы для получения частей
✅ Работать со словарями (ключ-значение)
✅ Применять методы списков и словарей
✅ Итерировать по коллекциям
✅ Создавать вложенные структуры

**С коллекциями ты можешь:**
- Хранить любое количество данных
- Организовывать сложные структуры
- Создавать базы данных
- Обрабатывать большие объёмы информации
- Решать реальные задачи

---

**Практикуй в CodeHS!** Создавай:
- TODO списки
- Адресные книги
- Базы данных студентов
- Игровые инвентари
- Статистику и аналитику

**Коллекции везде:** файлы, базы данных, API, веб-разработка, data science! 💪

**Следующий шаг:** Изучи работу с файлами и библиотеки Python! 📂
