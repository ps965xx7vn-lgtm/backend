# Методы классов: Объекты оживают! ⚡

Класс без методов — как зомби без мозгов: существует, но ничего не делает. 🧟

**Методы** — это **действия**, которые может выполнять объект. Давай оживим объекты!

## 🎯 Что такое метод?

**Метод** = функция, которая принадлежит объекту.

### Синтаксис

```python
class ИмяКласса:
    def название_метода(self, параметры):
        # Код метода
        pass
```

**Ключевое отличие от функций:**
- ❌ Функция: `def groan(zombie):`
- ✅ Метод: `def groan(self):`

Метод **всегда** принимает `self` первым параметром!

## 🧟 Пример: Зомби издаёт звуки

```python
class Zombie:
    def __init__(self, name):
        self.name = name

    def groan(self):  # ← Метод
        print(f"{self.name}: Граааах! 🧟")

walker = Zombie("Ходок")
walker.groan()  # Ходок: Граааах! 🧟
```

**Что происходит?**

1. `walker.groan()` вызывает метод
2. Python автоматически передаёт `walker` как `self`
3. Метод выполняется, используя `self.name`

## 🔄 Методы с параметрами

### Метод принимает аргументы

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def take_damage(self, damage):  # ← Параметр damage
        self.health -= damage
        print(f"{self.name} получил {damage} урона!")
        print(f"Здоровье: {self.health}")

walker = Zombie("Ходок", 50)
walker.take_damage(20)
# Ходок получил 20 урона!
# Здоровье: 30
```

**Обрати внимание:**
- Метод: `def take_damage(self, damage)` — **2 параметра**
- Вызов: `walker.take_damage(20)` — **1 аргумент**

**Почему?** Python автоматически передаёт `walker` как `self`!

### Несколько параметров

```python
class Human:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def attack(self, target, weapon_damage):
        damage = weapon_damage + 10  # Базовый урон + оружие
        target.health -= damage
        print(f"{self.name} атакует {target.name}!")
        print(f"Урон: {damage}")

rick = Human("Рик", 100)
walker = Zombie("Ходок", 50)

rick.attack(walker, 15)
# Рик атакует Ходок!
# Урон: 25
```

## 📤 Методы с возвратом (return)

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def is_alive(self):  # ← Возвращает True/False
        return self.health > 0

    def attack(self):  # ← Возвращает урон
        import random
        return random.randint(5, 15)

walker = Zombie("Ходок", 30)

# Используем возвращаемое значение
if walker.is_alive():
    damage = walker.attack()
    print(f"Зомби атакует! Урон: {damage}")
else:
    print("Зомби мёртв")
```

**Зачем `return`?**
- Метод может **вернуть результат** вычислений
- Можно использовать в условиях, присваиваниях и т.д.

## 🔗 Методы вызывают методы

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def groan(self):
        print(f"{self.name}: Граааах!")

    def walk(self):
        print(f"{self.name} идёт...")

    def approach(self):  # ← Вызывает другие методы!
        self.walk()
        self.groan()
        print(f"{self.name} приближается!")

walker = Zombie("Ходок", 50)
walker.approach()
# Ходок идёт...
# Ходок: Граааах!
# Ходок приближается!
```

**`self.walk()`** = "Вызови метод `walk` **этого** объекта".

## 🎮 Взаимодействие объектов через методы

Методы могут **изменять другие объекты**!

```python
class Human:
    def __init__(self, name, health):
        self.name = name
        self.health = health
        self.kills = 0

    def attack(self, zombie):
        damage = 20
        zombie.health -= damage  # ← Меняем другой объект!
        print(f"{self.name} атакует {zombie.name}!")

        if zombie.health <= 0:
            print(f"{zombie.name} повержен!")
            self.kills += 1

class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

rick = Human("Рик", 100)
walker = Zombie("Ходок", 40)

rick.attack(walker)
# Рик атакует Ходок!

rick.attack(walker)
# Рик атакует Ходок!
# Ходок повержен!

print(f"Убийств: {rick.kills}")  # 1
```

**Это и есть магия ООП:** Объекты общаются через методы! 🌟

## 📝 Методы изменяют атрибуты

```python
class Human:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.ammo = 12

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1  # ← Изменяем атрибут
            return True
        else:
            print("Патроны кончились!")
            return False

    def reload(self):
        self.ammo = 12  # ← Изменяем атрибут
        print(f"{self.name} перезарядился!")

    def heal(self, amount):
        self.health += amount  # ← Изменяем атрибут
        if self.health > 100:
            self.health = 100  # Максимум 100
        print(f"{self.name} восстановил {amount} HP. Здоровье: {self.health}")

rick = Human("Рик")
rick.shoot()  # Выстрел (патронов: 11)
rick.heal(20)  # Рик восстановил 20 HP. Здоровье: 100
```

## 🛠️ Типы методов

### 1. Геттеры (получение данных)

```python
class Zombie:
    def __init__(self, health):
        self.health = health

    def is_alive(self):  # ← Геттер
        return self.health > 0

    def get_status(self):  # ← Геттер
        if self.health > 30:
            return "Здоров"
        elif self.health > 0:
            return "Ранен"
        else:
            return "Мёртв"
```

### 2. Сеттеры (изменение данных)

```python
class Zombie:
    def __init__(self, health):
        self.health = health

    def set_health(self, new_health):  # ← Сеттер
        if new_health < 0:
            self.health = 0
        else:
            self.health = new_health
```

### 3. Действия (выполнение операций)

```python
class Zombie:
    def __init__(self, name):
        self.name = name

    def attack(self):  # ← Действие
        print(f"{self.name} атакует!")
        return 10

    def groan(self):  # ← Действие
        print(f"{self.name}: Граааах!")
```

## ⚠️ Частые ошибки

### Ошибка 1: Забыли `self`

```python
class Zombie:
    def __init__(self, name):
        self.name = name

    def groan():  # ❌ Нет self!
        print("Граааах!")

walker = Zombie("Ходок")
walker.groan()  # TypeError: groan() takes 0 positional arguments but 1 was given
```

**Исправление:**
```python
def groan(self):  # ✅ Добавили self
```

### Ошибка 2: Обращение к атрибуту без `self`

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

### Ошибка 3: Вызов метода без скобок

```python
walker = Zombie("Ходок", 50)
damage = walker.attack  # ❌ Нет ()

print(damage)  # <bound method Zombie.attack of <__main__.Zombie object at 0x...>>
```

**Исправление:**
```python
damage = walker.attack()  # ✅ Со скобками
```

## 📊 Сравнение: функция VS метод

### Функция (Урок 4)

```python
def zombie_attack(zombie):
    return 10

def human_attack(human, zombie):
    zombie["health"] -= 20

walker = {"name": "Ходок", "health": 50}
human_attack(rick, walker)
```

**Проблемы:**
- ❌ Функции и данные **отдельно**
- ❌ Легко передать не те аргументы
- ❌ Нет связи между данными и действиями

### Метод (Урок 5)

```python
class Human:
    def attack(self, zombie):
        zombie.health -= 20

rick = Human("Рик", 100)
walker = Zombie("Ходок", 50)
rick.attack(walker)
```

**Преимущества:**
- ✅ Метод принадлежит объекту
- ✅ Понятно кто и что делает
- ✅ Данные и действия **вместе**

## 💡 Лучшие практики

### ✅ Хорошие методы:

**1. Говорящие имена**
```python
def is_alive(self):  # ✅ Понятно что возвращает
def attack(self):    # ✅ Понятно что делает
```

**2. Одна ответственность**
```python
def shoot(self):
    if self.ammo > 0:
        self.ammo -= 1
        return True
    return False
    # ✅ Только стреляет, ничего лишнего
```

**3. Возвращают значение когда нужно**
```python
def is_alive(self):
    return self.health > 0  # ✅ Возвращает результат
```

### ❌ Плохие методы:

**1. Неясные имена**
```python
def do(self):  # ❌ Что делает?
def proc(self):  # ❌ Что обрабатывает?
```

**2. Делают слишком много**
```python
def do_everything(self):
    self.shoot()
    self.reload()
    self.heal(20)
    self.walk()
    # ❌ Слишком много ответственности!
```

## 📝 Чек-лист: Проверь себя

- [ ] Знаю как создать метод в классе
- [ ] Понимаю что `self` всегда первый параметр
- [ ] Умею передавать параметры в метод
- [ ] Умею возвращать значения из метода (`return`)
- [ ] Понимаю как методы изменяют атрибуты
- [ ] Понимаю как методы вызывают другие методы
- [ ] Понимаю как объекты взаимодействуют через методы

## 🚀 Итого

**Метод** — функция, принадлежащая объекту.

**Синтаксис:**
```python
class ИмяКласса:
    def название_метода(self, параметры):
        # Код
        return результат
```

**Вызов:**
```python
объект.метод(аргументы)
```

**Особенности:**
- ✅ Всегда принимает `self` первым
- ✅ Может обращаться к атрибутам (`self.атрибут`)
- ✅ Может вызывать другие методы (`self.метод()`)
- ✅ Может изменять атрибуты (`self.атрибут = новое_значение`)
- ✅ Может возвращать значения (`return`)

**Ключевая идея:** Методы — это **действия** объектов. Объекты взаимодействуют и изменяют друг друга через методы!

**Следующий шаг:** Научись красиво выводить объекты с помощью `__str__`! 🎨
