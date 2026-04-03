# `with open`: Работа с файлами по-правильному 💾

Игра без сохранений — как зомби-апокалипсис без убежища: всё теряется! 😱

Научись **записывать данные в файлы** и **читать их** с помощью **`with open`** — правильного способа работы с файлами.

## 🤔 Зачем нужны файлы?

### Проблема: данные исчезают

```python
class Human:
    def __init__(self, name):
        self.name = name
        self.kills = 0

rick = Human("Рик")
rick.kills = 10

# Закрыли программу...
# ...открыли снова
# Данные потеряны! 😱
```

**Решение:** Сохранять в файл!

```python
# Запись в файл
with open("saves/rick.txt", "w") as f:
    f.write(f"{rick.name}\n")
    f.write(f"{rick.kills}\n")

# Закрыли программу...
# ...открыли снова

# Чтение из файла
with open("saves/rick.txt", "r") as f:
    name = f.readline().strip()
    kills = int(f.readline().strip())

print(f"{name}: {kills} убийств")  # Рик: 10 убийств ✅
```

## 📝 Запись в файл: `"w"` режим

### Синтаксис

```python
with open("имя_файла.txt", "w") as f:
    f.write("текст")
```

**`"w"`** = **write** (запись). Создаёт новый файл или **перезаписывает** существующий!

### Пример 1: Лог битвы

```python
with open("battle_log.txt", "w") as f:
    f.write("=== ЛОГ БИТВЫ ===\n")
    f.write("Рик атакует Ходока\n")
    f.write("Урон: 20\n")
    f.write("Зомби повержен!\n")

# Создан файл battle_log.txt:
# === ЛОГ БИТВЫ ===
# Рик атакует Ходока
# Урон: 20
# Зомби повержен!
```

### Пример 2: Сохранение статистики

```python
class Human:
    def __init__(self, name):
        self.name = name
        self.kills = 0
        self.health = 100

    def save(self):
        with open(f"saves/{self.name}.txt", "w") as f:
            f.write(f"{self.name}\n")
            f.write(f"{self.kills}\n")
            f.write(f"{self.health}\n")
        print(f"Сохранение {self.name} завершено!")

rick = Human("Рик")
rick.kills = 5
rick.save()
# Создан файл saves/Рик.txt с данными
```

## 📖 Чтение из файла: `"r"` режим

### Синтаксис

```python
with open("имя_файла.txt", "r") as f:
    content = f.read()  # Весь файл
```

**`"r"`** = **read** (чтение).

### Способы чтения

#### 1. `read()` — весь файл сразу

```python
with open("battle_log.txt", "r") as f:
    content = f.read()
    print(content)
# Выведет весь файл одной строкой
```

#### 2. `readline()` — одна строка

```python
with open("saves/Рик.txt", "r") as f:
    name = f.readline().strip()    # Первая строка
    kills = f.readline().strip()   # Вторая строка
    health = f.readline().strip()  # Третья строка

print(f"{name}: {kills} убийств, {health} HP")
```

**`strip()`** убирает `\n` (перевод строки) в конце.

#### 3. `readlines()` — все строки в список

```python
with open("battle_log.txt", "r") as f:
    lines = f.readlines()  # ['=== ЛОГ БИТВЫ ===\n', 'Рик атакует...\n', ...]

for line in lines:
    print(line.strip())  # Выводим каждую строку
```

### Пример: Загрузка персонажа

```python
class Human:
    def __init__(self, name):
        self.name = name
        self.kills = 0
        self.health = 100

    @staticmethod
    def load(name):
        """Загружает персонажа из файла"""
        with open(f"saves/{name}.txt", "r") as f:
            loaded_name = f.readline().strip()
            kills = int(f.readline().strip())
            health = int(f.readline().strip())

        # Создаём объект с загруженными данными
        human = Human(loaded_name)
        human.kills = kills
        human.health = health
        print(f"Загружен {loaded_name}!")
        return human

# Использование
rick = Human.load("Рик")
print(f"{rick.name}: {rick.kills} убийств, {rick.health} HP")
```

## ➕ Дозапись в файл: `"a"` режим

**`"a"`** = **append** (добавить в конец). Не перезаписывает, а **добавляет**!

```python
# Первая запись
with open("kills.txt", "w") as f:
    f.write("Убийства:\n")

# Добавляем новые записи
with open("kills.txt", "a") as f:
    f.write("Рик убил Ходока\n")
    f.write("Дэрил убил Бегуна\n")

# Ещё одна запись позже
with open("kills.txt", "a") as f:
    f.write("Мишон убила Танка\n")

# В файле:
# Убийства:
# Рик убил Ходока
# Дэрил убил Бегуна
# Мишон убила Танка
```

### Пример: Лог битвы

```python
class BattleLogger:
    def __init__(self, filename):
        self.filename = filename
        # Создаём файл с заголовком
        with open(self.filename, "w") as f:
            f.write("=== ЛОГ БИТВЫ ===\n\n")

    def log(self, message):
        # Добавляем в конец файла
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")

logger = BattleLogger("battle.txt")
logger.log("Рик атакует Ходока (урон: 20)")
logger.log("Ходок побеждён!")
logger.log("Дэрил стреляет в Бегуна (урон: 50)")
```

## 🔒 Зачем `with`?

### ❌ Старый способ (без `with`):

```python
f = open("data.txt", "w")
f.write("Данные")
f.close()  # ← Легко забыть!
```

**Проблемы:**
- ❌ Можно забыть `.close()`
- ❌ Если ошибка — файл не закроется
- ❌ Утечка ресурсов

### ✅ Правильный способ (с `with`):

```python
with open("data.txt", "w") as f:
    f.write("Данные")
# Файл закрывается автоматически!
```

**Преимущества:**
- ✅ Файл **автоматически закрывается** (даже при ошибке)
- ✅ Короче и понятнее
- ✅ Безопаснее

## 📊 Режимы открытия файлов

| Режим | Название | Что делает | Если файла нет |
|-------|----------|------------|----------------|
| `"r"` | read | Читает | Ошибка |
| `"w"` | write | Записывает (перезаписывает) | Создаёт новый |
| `"a"` | append | Добавляет в конец | Создаёт новый |
| `"r+"` | read+write | Читает и пишет | Ошибка |
| `"w+"` | write+read | Пишет и читает (перезаписывает) | Создаёт новый |

**Чаще всего нужны:** `"r"`, `"w"`, `"a"`

## 🎮 Полный пример: Игра с сохранениями

```python
class Game:
    def __init__(self):
        self.player_name = ""
        self.level = 1
        self.kills = 0
        self.health = 100

    def new_game(self, name):
        """Новая игра"""
        self.player_name = name
        self.level = 1
        self.kills = 0
        self.health = 100
        print(f"Новая игра начата: {name}")

    def save_game(self):
        """Сохранить игру"""
        filename = f"saves/{self.player_name}_save.txt"
        with open(filename, "w") as f:
            f.write(f"{self.player_name}\n")
            f.write(f"{self.level}\n")
            f.write(f"{self.kills}\n")
            f.write(f"{self.health}\n")
        print(f"✅ Игра сохранена: {filename}")

    def load_game(self, name):
        """Загрузить игру"""
        filename = f"saves/{name}_save.txt"
        try:
            with open(filename, "r") as f:
                self.player_name = f.readline().strip()
                self.level = int(f.readline().strip())
                self.kills = int(f.readline().strip())
                self.health = int(f.readline().strip())
            print(f"✅ Игра загружена: {filename}")
        except FileNotFoundError:
            print(f"❌ Сохранение не найдено: {filename}")

    def status(self):
        """Показать статус"""
        print(f"\n{'='*40}")
        print(f"Игрок: {self.player_name}")
        print(f"Уровень: {self.level}")
        print(f"Убийств: {self.kills}")
        print(f"Здоровье: {self.health}")
        print(f"{'='*40}\n")

# Использование
game = Game()
game.new_game("Рик")
game.kills = 10
game.level = 3
game.status()
game.save_game()

# Закрыли программу...
# Открыли снова

game2 = Game()
game2.load_game("Рик")
game2.status()  # Данные восстановлены! ✅
```

## ⚠️ Частые ошибки

### Ошибка 1: Забыли режим

```python
with open("data.txt") as f:  # ❌ Нет режима!
    f.write("Данные")  # Ошибка: not writable
```

**Исправление:**
```python
with open("data.txt", "w") as f:  # ✅ Указали "w"
```

### Ошибка 2: Пытаемся писать в режиме `"r"`

```python
with open("data.txt", "r") as f:
    f.write("Данные")  # ❌ UnsupportedOperation: not writable
```

**Исправление:**
```python
with open("data.txt", "w") as f:  # ✅ Режим "w"
```

### Ошибка 3: Забыли `.strip()` при чтении

```python
with open("saves/data.txt", "r") as f:
    kills = int(f.readline())  # ❌ '10\n' → ошибка преобразования

# Исправление:
kills = int(f.readline().strip())  # ✅ '10'
```

### Ошибка 4: Файл не найден

```python
with open("saves/данные.txt", "r") as f:  # ❌ FileNotFoundError
    content = f.read()
```

**Исправление:** Проверяй существование или используй `try-except`:
```python
try:
    with open("saves/данные.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("Файл не найден!")
```

## 💡 Лучшие практики

### ✅ Хорошо:

**1. Используй `with`**
```python
with open("data.txt", "w") as f:  # ✅ Автоматически закроется
    f.write("Данные")
```

**2. Указывай путь к папке**
```python
with open("saves/player.txt", "w") as f:  # ✅ Организация
```

**3. Используй `try-except` для чтения**
```python
try:
    with open("data.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("Файл не найден")
```

**4. `.strip()` при чтении строк**
```python
name = f.readline().strip()  # ✅ Убирает \n
```

### ❌ Плохо:

**1. Без `with`**
```python
f = open("data.txt", "w")  # ❌ Забыть закрыть
f.write("Данные")
f.close()
```

**2. Путаница в режимах**
```python
with open("data.txt", "w") as f:
    content = f.read()  # ❌ Режим "w" не для чтения!
```

## 📝 Чек-лист: Проверь себя

- [ ] Знаю зачем нужны файлы (сохранение данных)
- [ ] Понимаю синтаксис `with open(...) as f:`
- [ ] Знаю режимы: `"r"` (чтение), `"w"` (запись), `"a"` (дозапись)
- [ ] Умею записывать данные: `f.write()`
- [ ] Умею читать данные: `f.read()`, `f.readline()`
- [ ] Понимаю зачем нужен `with` (автозакрытие)
- [ ] Умею использовать `.strip()` при чтении
- [ ] Умею обрабатывать `FileNotFoundError`

## 🚀 Итого

**`with open`** — правильный способ работы с файлами.

**Синтаксис:**
```python
# Запись
with open("файл.txt", "w") as f:
    f.write("данные")

# Чтение
with open("файл.txt", "r") as f:
    content = f.read()

# Дозапись
with open("файл.txt", "a") as f:
    f.write("ещё данные")
```

**Режимы:**
- `"r"` — чтение (read)
- `"w"` — запись (write, перезаписывает)
- `"a"` — дозапись (append, добавляет в конец)

**Зачем `with`?**
- ✅ Автоматически закрывает файл
- ✅ Безопаснее (закроется даже при ошибке)
- ✅ Короче и понятнее

**Методы:**
- `f.write(text)` — записать текст
- `f.read()` — прочитать весь файл
- `f.readline()` — прочитать одну строку
- `f.readlines()` — прочитать все строки в список

**Зачем нужны файлы?**
Сохранять прогресс, логи, статистику — всё, что должно пережить закрытие программы! 💾

**Следующий шаг:** Используй файлы в классах для сохранения объектов! 🎮
