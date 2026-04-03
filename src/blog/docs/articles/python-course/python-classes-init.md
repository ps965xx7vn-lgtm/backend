# Создаём классы: `__init__` и загадка `self` 🏗️

Ты знаешь что такое ООП. Теперь **создадим первый класс** и разберёмся с двумя главными тайнами Python:

1. **`__init__`** — что за странное имя?
2. **`self`** — почему он везде?

Погнали! 🚀

## 🎯 Создание класса: синтаксис

### Базовая структура

```python
class ИмяКласса:
    def __init__(self, параметры):
        # Инициализация атрибутов
        self.атрибут = значение

    def метод(self):
        # Действия объекта
        pass
```

### Пример: Зомби

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def groan(self):
        print(f"{self.name}: Граааах! 🧟")

# Создание объекта
walker = Zombie("Ходок", 50)
walker.groan()  # Ходок: Граааах! 🧟
```

**Что происходит?**

1. `class Zombie:` — объявляем класс
2. `__init__(self, name, health)` — конструктор (запускается при создании)
3. `self.name = name` — сохраняем атрибуты
4. `walker = Zombie("Ходок", 50)` — создаём объект

## 🔑 Метод `__init__`: конструктор

### Что это?

**`__init__`** = **конструктор** = метод, который вызывается **автоматически** при создании объекта.

**Аналогия:** Когда рождается ребёнок 👶, ему сразу дают имя, пол, дату рождения. `__init__` делает то же для объектов.

### Синтаксис

```python
def __init__(self, параметр1, параметр2):
    self.атрибут1 = параметр1
    self.атрибут2 = параметр2
```

**Важно:**
- Имя **всегда** `__init__` (две подчёркивания с каждой стороны)
- Первый параметр **всегда** `self`
- Вызывается **автоматически** при `Zombie("Ходок", 50)`

### Пример: Человек

```python
class Human:
    def __init__(self, name, health, age):
        self.name = name
        self.health = health
        self.age = age
        self.kills = 0  # Можно задать значение по умолчанию!

rick = Human("Рик", 100, 35)
print(rick.name)   # Рик
print(rick.kills)  # 0 (хотя не передавали!)
```

**Что здесь произошло:**

1. Вызвали `Human("Рик", 100, 35)`
2. Python **автоматически** вызвал `__init__(self, "Рик", 100, 35)`
3. Сохранились атрибуты: `name`, `health`, `age`, `kills`
4. Вернулся готовый объект `rick`

## 🤔 Загадка `self`: что это?

### Определение

**`self`** = **ссылка на сам объект**.

Когда ты пишешь `self.name`, ты говоришь: "Атрибут `name` **этого конкретного объекта**".

### Проблема без `self`

```python
class Zombie:
    def __init__(self, name):
        name = name  # ❌ Не работает!

walker = Zombie("Ходок")
print(walker.name)  # AttributeError: 'Zombie' object has no attribute 'name'
```

**Почему не работает?**
`name` — это **локальная переменная** внутри `__init__`. Она умрёт после выполнения метода!

### Решение: `self`

```python
class Zombie:
    def __init__(self, name):
        self.name = name  # ✅ Работает!

walker = Zombie("Ходок")
print(walker.name)  # Ходок
```

**`self.name`** = "Атрибут `name` объекта `walker`". Он **сохраняется** в объекте!

### Визуализация

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name      # walker.name = "Ходок"
        self.health = health  # walker.health = 50

walker = Zombie("Ходок", 50)
runner = Zombie("Бегун", 30)

# walker и runner — разные объекты!
print(walker.name)   # Ходок
print(runner.name)   # Бегун

# У каждого свои атрибуты
print(walker.health)  # 50
print(runner.health)  # 30
```

**`self`** позволяет каждому объекту иметь **свои** атрибуты!

## 🔄 `self` в методах

### Доступ к атрибутам

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def groan(self):
        # Используем self для доступа к name
        print(f"{self.name}: Граааах!")

    def take_damage(self, damage):
        # Используем self для доступа к health
        self.health -= damage
        print(f"{self.name} получил {damage} урона. Здоровье: {self.health}")

walker = Zombie("Ходок", 50)
walker.groan()            # Ходок: Граааах!
walker.take_damage(20)    # Ходок получил 20 урона. Здоровье: 30
```

**Без `self`** методы не знали бы какие атрибуты использовать!

### Вызов методов из методов

```python
class Zombie:
    def __init__(self, name):
        self.name = name

    def groan(self):
        print(f"{self.name}: Граааах!")

    def attack(self):
        self.groan()  # ✅ Вызов другого метода через self!
        print(f"{self.name} атакует!")

walker = Zombie("Ходок")
walker.attack()
# Ходок: Граааах!
# Ходок атакует!
```

**`self.groan()`** = "Вызвать метод `groan` **этого** объекта".

## 🎨 Полный пример: класс Human

```python
class Human:
    def __init__(self, name, health=100):
        self.name = name
        self.health = health
        self.ammo = 12
        self.kills = 0

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            print(f"{self.name} стреляет! Патронов: {self.ammo}")
            return True
        else:
            print(f"{self.name}: Патроны кончились!")
            return False

    def reload(self):
        self.ammo = 12
        print(f"{self.name} перезарядился!")

    def status(self):
        print(f"{'='*30}")
        print(f"Имя: {self.name}")
        print(f"Здоровье: {self.health}")
        print(f"Патроны: {self.ammo}")
        print(f"Убийств: {self.kills}")
        print(f"{'='*30}")

# Используем
rick = Human("Рик", 100)
rick.status()
# ==============================
# Имя: Рик
# Здоровье: 100
# Патроны: 12
# Убийств: 0
# ==============================

rick.shoot()  # Рик стреляет! Патронов: 11
rick.shoot()  # Рик стреляет! Патронов: 10
rick.reload() # Рик перезарядился!
```

## 📝 Параметры по умолчанию

```python
class Zombie:
    def __init__(self, name, health=50, speed=2):
        #                      ^^^^^^^^^^  ^^^^^^^
        #                      Значения по умолчанию
        self.name = name
        self.health = health
        self.speed = speed

# Можно не передавать health и speed
walker = Zombie("Ходок")
print(walker.health)  # 50 (по умолчанию)

# Или передать свои значения
runner = Zombie("Бегун", 30, 5)
print(runner.speed)  # 5
```

**Правило:** Параметры с умолчанием должны быть **после** обязательных.

## ⚠️ Частые ошибки

### Ошибка 1: Забыли `self`

```python
class Zombie:
    def __init__(self, name):
        name = name  # ❌ Локальная переменная!

walker = Zombie("Ходок")
print(walker.name)  # AttributeError
```

**Исправление:**
```python
self.name = name  # ✅ Атрибут объекта
```

### Ошибка 2: Забыли `self` в параметрах метода

```python
class Zombie:
    def __init__(name):  # ❌ Нет self!
        self.name = name

walker = Zombie("Ходок")  # TypeError
```

**Исправление:**
```python
def __init__(self, name):  # ✅ self первый параметр
```

### Ошибка 3: Опечатка в `__init__`

```python
class Zombie:
    def _init_(self, name):  # ❌ Одно подчёркивание!
        self.name = name

walker = Zombie("Ходок")  # TypeError
```

**Исправление:**
```python
def __init__(self, name):  # ✅ Два подчёркивания с каждой стороны
```

### Ошибка 4: Обращение к атрибуту без `self`

```python
class Zombie:
    def __init__(self, name):
        self.name = name

    def groan(self):
        print(f"{name}: Граааах!")  # ❌ Нет self!

walker = Zombie("Ходок")
walker.groan()  # NameError: name 'name' is not defined
```

**Исправление:**
```python
print(f"{self.name}: Граааах!")  # ✅ self.name
```

## 🎯 Когда что использовать?

| Что | Где | Зачем |
|-----|-----|-------|
| `self.атрибут` | В `__init__` | Сохранить данные объекта |
| `self.атрибут` | В методах | Прочитать/изменить данные |
| `self.метод()` | В методах | Вызвать другой метод |
| `параметр` | Без `self` | Локальная переменная (умрёт после метода) |

## 📚 Сравнение: функции VS классы

### Функции (Урок 4)

```python
def create_zombie(name, health):
    return {"name": name, "health": health}

def zombie_groan(zombie):
    print(f"{zombie['name']}: Граааах!")

walker = create_zombie("Ходок", 50)
zombie_groan(walker)
```

**Проблемы:**
- ❌ Функции и данные **раздельны**
- ❌ Легко ошибиться (передать не тот словарь)
- ❌ Нет структуры

### Классы (Урок 5)

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def groan(self):
        print(f"{self.name}: Граааах!")

walker = Zombie("Ходок", 50)
walker.groan()
```

**Преимущества:**
- ✅ Данные и методы **вместе**
- ✅ Понятная структура
- ✅ Меньше ошибок

## 💡 Чек-лист: Проверь себя

- [ ] Знаю как создать класс (`class ИмяКласса:`)
- [ ] Понимаю зачем нужен `__init__` (конструктор)
- [ ] Понимаю что такое `self` (ссылка на объект)
- [ ] Умею создавать атрибуты (`self.атрибут = значение`)
- [ ] Умею обращаться к атрибутам в методах (`self.атрибут`)
- [ ] Знаю почему `self` всегда первый параметр
- [ ] Понимаю разницу между `name` и `self.name`

## 🚀 Итого

**`__init__`** — конструктор, вызывается автоматически при создании объекта.

**`self`** — ссылка на сам объект, позволяет:
- Сохранять атрибуты: `self.name = name`
- Обращаться к атрибутам: `print(self.name)`
- Вызывать методы: `self.другой_метод()`

**Синтаксис:**
```python
class ИмяКласса:
    def __init__(self, параметры):
        self.атрибут = значение
```

**Создание объекта:**
```python
объект = ИмяКласса(аргументы)
```

**Следующий шаг:** Научись создавать методы — действия объектов! ⚔️
