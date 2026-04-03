# Магия `__str__`: Красивый вывод объектов 🎨

Представь: выводишь зомби в консоль и видишь: `<__main__.Zombie object at 0x10e8c4d90>` 😱

Бесполезно! Хочется видеть **имя**, **здоровье**, **статус**. Для этого есть магический метод **`__str__`** ✨

## 🤔 Проблема: некрасивый вывод

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

walker = Zombie("Ходок", 50)
print(walker)
# <__main__.Zombie object at 0x10e8c4d90>  ← Бесполезно!
```

**Что не так?**
Python не знает **как** выводить твой класс. Он показывает адрес в памяти.

## ✨ Решение: `__str__`

**`__str__`** — магический метод, который вызывается при `print(объект)` или `str(объект)`.

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def __str__(self):  # ← Магический метод!
        return f"Зомби '{self.name}' (HP: {self.health})"

walker = Zombie("Ходок", 50)
print(walker)
# Зомби 'Ходок' (HP: 50)  ← Красиво! ✨
```

**Что изменилось?**
- Добавили метод `__str__`
- Он **возвращает строку** (обязательно `return`)
- Python автоматически вызывает его при `print()`

## 🎨 Примеры красивого вывода

### Пример 1: Зомби с эмодзи

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def __str__(self):
        status = "🟢" if self.health > 30 else "🔴"
        return f"{status} Зомби '{self.name}' | HP: {self.health}"

walker = Zombie("Ходок", 50)
runner = Zombie("Бегун", 20)

print(walker)  # 🟢 Зомби 'Ходок' | HP: 50
print(runner)  # 🔴 Зомби 'Бегун' | HP: 20
```

### Пример 2: Человек с инвентарём

```python
class Human:
    def __init__(self, name, health):
        self.name = name
        self.health = health
        self.ammo = 12
        self.kills = 0

    def __str__(self):
        return (f"👤 {self.name}\n"
                f"   ❤️  HP: {self.health}/100\n"
                f"   🔫 Патроны: {self.ammo}\n"
                f"   💀 Убийств: {self.kills}")

rick = Human("Рик", 85)
rick.kills = 3
print(rick)
# 👤 Рик
#    ❤️  HP: 85/100
#    🔫 Патроны: 12
#    💀 Убийств: 3
```

### Пример 3: Оружие

```python
class Weapon:
    def __init__(self, name, damage, ammo):
        self.name = name
        self.damage = damage
        self.ammo = ammo

    def __str__(self):
        return f"🔫 {self.name} (Урон: {self.damage}, Патроны: {self.ammo})"

pistol = Weapon("Пистолет", 20, 12)
rifle = Weapon("Винтовка", 50, 30)

print(pistol)  # 🔫 Пистолет (Урон: 20, Патроны: 12)
print(rifle)   # 🔫 Винтовка (Урон: 50, Патроны: 30)
```

## 🔄 Использование `__str__`

### 1. С `print()`

```python
walker = Zombie("Ходок", 50)
print(walker)  # Автоматически вызывает walker.__str__()
```

### 2. С `str()`

```python
walker = Zombie("Ходок", 50)
text = str(walker)  # Вызывает walker.__str__()
print(text)  # Зомби 'Ходок' (HP: 50)
```

### 3. В f-строках

```python
walker = Zombie("Ходок", 50)
message = f"Появился {walker}!"
print(message)
# Появился Зомби 'Ходок' (HP: 50)!
```

### 4. В списках

```python
zombies = [
    Zombie("Ходок", 50),
    Zombie("Бегун", 30),
    Zombie("Танк", 100)
]

for zombie in zombies:
    print(zombie)
# Зомби 'Ходок' (HP: 50)
# Зомби 'Бегун' (HP: 30)
# Зомби 'Танк' (HP: 100)
```

## 📋 Правила `__str__`

### ✅ Правильно:

**1. Всегда возвращает строку**
```python
def __str__(self):
    return f"Зомби '{self.name}'"  # ✅ Строка
```

**2. Краткий и информативный**
```python
def __str__(self):
    return f"{self.name} (HP: {self.health})"  # ✅ Понятно
```

**3. Читабельный для человека**
```python
def __str__(self):
    return f"👤 {self.name} | ❤️ {self.health}"  # ✅ Красиво
```

### ❌ Неправильно:

**1. Не возвращает строку**
```python
def __str__(self):
    print(f"Зомби '{self.name}'")  # ❌ print вместо return!
    # Вернёт None!
```

**2. Возвращает не строку**
```python
def __str__(self):
    return self.health  # ❌ Число, не строка!
```

**3. Слишком много информации**
```python
def __str__(self):
    return f"""
    Имя: {self.name}
    Здоровье: {self.health}
    Скорость: {self.speed}
    Создан: {self.created_at}
    Последнее обновление: {self.updated_at}
    ...ещё 50 строк...
    """  # ❌ Слишком много!
```

## 🪄 Другие магические методы

`__str__` — не единственный магический метод! Их много:

### `__repr__` — для отладки

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def __str__(self):
        return f"Зомби '{self.name}'"  # Для пользователя

    def __repr__(self):
        return f"Zombie(name='{self.name}', health={self.health})"  # Для программиста

walker = Zombie("Ходок", 50)
print(walker)      # Зомби 'Ходок'  ← Вызывает __str__()
print(repr(walker))  # Zombie(name='Ходок', health=50)  ← Вызывает __repr__()
```

**Разница:**
- `__str__` — красиво для пользователя
- `__repr__` — точно для разработчика (можно скопировать код)

### `__len__` — для `len()`

```python
class Horde:
    def __init__(self):
        self.zombies = []

    def add(self, zombie):
        self.zombies.append(zombie)

    def __len__(self):  # ← Для len()
        return len(self.zombies)

horde = Horde()
horde.add(Zombie("Ходок", 50))
horde.add(Zombie("Бегун", 30))

print(len(horde))  # 2  ← Вызывает horde.__len__()
```

### `__eq__` — для сравнения `==`

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def __eq__(self, other):  # ← Для ==
        return self.name == other.name and self.health == other.health

z1 = Zombie("Ходок", 50)
z2 = Zombie("Ходок", 50)
z3 = Zombie("Бегун", 30)

print(z1 == z2)  # True  ← Вызывает z1.__eq__(z2)
print(z1 == z3)  # False
```

### Список популярных магических методов:

| Метод | Вызов | Назначение |
|-------|-------|------------|
| `__init__` | `Zombie()` | Создание объекта |
| `__str__` | `print(obj)`, `str(obj)` | Строка для пользователя |
| `__repr__` | `repr(obj)` | Строка для отладки |
| `__len__` | `len(obj)` | Длина объекта |
| `__eq__` | `obj1 == obj2` | Сравнение на равенство |
| `__lt__` | `obj1 < obj2` | Меньше |
| `__add__` | `obj1 + obj2` | Сложение |
| `__getitem__` | `obj[index]` | Доступ по индексу |

*(Остальные изучим позже)*

## 💡 Когда использовать `__str__`?

### ✅ Используй когда:

- Нужно **выводить объект** в консоль
- Хочешь **отладить** код (видеть состояние объектов)
- Создаёшь **игру** (вывод персонажей, предметов)
- Пишешь **логи** (записывать состояние)

### Пример: отладка боя

```python
class Zombie:
    def __init__(self, name, health):
        self.name = name
        self.health = health

    def __str__(self):
        return f"Зомби '{self.name}' (HP: {self.health})"

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self} получил {damage} урона")
        #    ↑ Использует __str__!

walker = Zombie("Ходок", 50)
walker.take_damage(20)
# Зомби 'Ходок' (HP: 30) получил 20 урона  ← Красиво!
```

## ⚠️ Частые ошибки

### Ошибка 1: `print` вместо `return`

```python
class Zombie:
    def __str__(self):
        print(f"Зомби '{self.name}'")  # ❌ print!

walker = Zombie("Ходок", 50)
print(walker)
# Зомби 'Ходок'
# None  ← Вернул None!
```

**Исправление:**
```python
def __str__(self):
    return f"Зомби '{self.name}'"  # ✅ return
```

### Ошибка 2: Возврат не строки

```python
class Zombie:
    def __str__(self):
        return self.health  # ❌ Число!

walker = Zombie("Ходок", 50)
print(walker)  # TypeError: __str__ returned non-string
```

**Исправление:**
```python
def __str__(self):
    return str(self.health)  # ✅ Преобразуем в строку
    # Или
    return f"HP: {self.health}"  # ✅ f-строка
```

### Ошибка 3: Забыли `self`

```python
class Zombie:
    def __str__():  # ❌ Нет self!
        return "Зомби"

walker = Zombie("Ходок", 50)
print(walker)  # TypeError
```

**Исправление:**
```python
def __str__(self):  # ✅ Добавили self
```

## 📝 Чек-лист: Проверь себя

- [ ] Знаю зачем нужен `__str__`
- [ ] Понимаю что `__str__` должен **возвращать строку**
- [ ] Умею создать `__str__` в классе
- [ ] Знаю что `__str__` вызывается при `print()`
- [ ] Понимаю разницу между `__str__` и `__repr__`
- [ ] Умею делать красивый вывод с эмодзи

## 🚀 Итого

**`__str__`** — магический метод для **красивого вывода** объектов.

**Синтаксис:**
```python
class ИмяКласса:
    def __str__(self):
        return "строка с описанием объекта"
```

**Использование:**
```python
print(объект)  # Вызывает __str__()
str(объект)    # Вызывает __str__()
f"{объект}"    # Вызывает __str__()
```

**Правила:**
- ✅ Всегда **возвращает строку** (`return`, не `print`)
- ✅ Краткий и информативный
- ✅ Читабельный для человека

**Другие магические методы:**
- `__repr__` — для отладки (точное представление)
- `__len__` — для `len(объект)`
- `__eq__` — для `объект1 == объект2`

**Зачем?**
Красивый вывод упрощает отладку и делает код понятнее! 🎨

**Следующий шаг:** Научись записывать данные в файлы! 💾
