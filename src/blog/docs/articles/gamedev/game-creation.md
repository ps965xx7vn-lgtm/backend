# Создаём игру на Python: пошаговый гайд 🎮

Игры - лучший способ учиться программированию! Разберём как создать свою первую игру.

## 🎯 Что делает игру игрой?

Любая игра состоит из:
1. **Правила** - что можно и нельзя делать
2. **Цель** - что нужно достичь
3. **Обратная связь** - игрок видит результат действий
4. **Повторяемость** - можно играть снова

## 🚀 Шаг 1: Простая текстовая игра

### Игра "Угадай число"

```python
import random

# Начальная настройка
secret = random.randint(1, 100)
attempts = 0
max_attempts = 7

print('🎯 УГАДАЙ ЧИСЛО')
print(f'У тебя {max_attempts} попыток!\\n')

# Основной игровой цикл
while attempts < max_attempts:
    guess = int(input(f'Попытка {attempts + 1}/{max_attempts}: '))
    attempts += 1

    # Логика игры
    if guess == secret:
        print(f'\\n🎉 ПОБЕДА за {attempts} попыток!')
        break
    elif guess < secret:
        print('↗️ Больше!')
    else:
        print('↘️ Меньше!')

    # Проверка на конец попыток
    if attempts == max_attempts:
        print(f'\\n💀 Проигрыш! Было: {secret}')
```

**Что здесь есть:**
- ✅ Правила (угадай число за 7 попыток)
- ✅ Цель (угадать число)
- ✅ Обратная связь (больше/меньше)
- ✅ Повторяемость (можно запустить снова)

## 🎲 Шаг 2: Добавляем функции

Разобьём игру на части:

```python
import random

def start_game():
    """Запускает новую игру"""
    secret = random.randint(1, 100)
    attempts = 0
    max_attempts = 7

    print('🎯 УГАДАЙ ЧИСЛО')
    print(f'У тебя {max_attempts} попыток!\\n')

    return secret, attempts, max_attempts

def get_player_input(current_attempt, max_attempts):
    """Получает ввод игрока"""
    while True:
        try:
            guess = int(input(f'Попытка {current_attempt}/{max_attempts}: '))
            if 1 <= guess <= 100:
                return guess
            else:
                print('Число должно быть от 1 до 100!')
        except ValueError:
            print('Введи число!')

def check_guess(guess, secret):
    """Проверяет догадку"""
    if guess == secret:
        return 'win'
    elif guess < secret:
        return 'higher'
    else:
        return 'lower'

def play_game():
    """Основная функция игры"""
    secret, attempts, max_attempts = start_game()

    while attempts < max_attempts:
        attempts += 1
        guess = get_player_input(attempts, max_attempts)
        result = check_guess(guess, secret)

        if result == 'win':
            print(f'\\n🎉 ПОБЕДА за {attempts} попыток!')
            return
        elif result == 'higher':
            print('↗️ Больше!')
        else:
            print('↘️ Меньше!')

    print(f'\\n💀 Проигрыш! Было: {secret}')

# Запуск
if __name__ == '__main__':
    play_game()
```

**Преимущества функций:**
- Код легче читать
- Можно переиспользовать части
- Легче тестировать
- Проще добавлять новые фичи

## 💪 Шаг 3: Добавляем фичи

### Система уровней сложности

```python
def choose_difficulty():
    """Выбор сложности"""
    print('Выбери сложность:')
    print('1 - Легко (1-50, 10 попыток)')
    print('2 - Средне (1-100, 7 попыток)')
    print('3 - Сложно (1-200, 5 попыток)')

    choice = input('\\nТвой выбор: ')

    if choice == '1':
        return 1, 50, 10
    elif choice == '2':
        return 1, 100, 7
    elif choice == '3':
        return 1, 200, 5
    else:
        return 1, 100, 7  # По умолчанию
```

### Система очков

```python
def calculate_score(attempts, max_attempts):
    """Подсчёт очков"""
    # Чем меньше попыток, тем больше очков
    base_score = 1000
    penalty = (attempts - 1) * 100
    score = max(base_score - penalty, 100)
    return score
```

### Таблица рекордов

```python
records = []

def save_record(name, score):
    """Сохраняет рекорд"""
    records.append({'name': name, 'score': score})
    # Сортируем по убыванию очков
    records.sort(key=lambda x: x['score'], reverse=True)

def show_records():
    """Показывает топ-5"""
    print('\\n🏆 ТАБЛИЦА РЕКОРДОВ')
    for i, record in enumerate(records[:5], 1):
        print(f'{i}. {record["name"]}: {record["score"]} очков')
```

## 🎨 Шаг 4: Улучшаем интерфейс

### Добавляем цвета (если терминал поддерживает)

```python
# ANSI escape codes
class Colors:
    GREEN = '\\033[92m'
    RED = '\\033[91m'
    YELLOW = '\\033[93m'
    BLUE = '\\033[94m'
    RESET = '\\033[0m'

def print_colored(text, color):
    """Цветной вывод"""
    print(f'{color}{text}{Colors.RESET}')

# Использование
print_colored('✅ Правильно!', Colors.GREEN)
print_colored('❌ Ошибка!', Colors.RED)
```

### Анимированные эффекты

```python
import time

def loading_animation(text, duration=2):
    """Анимация загрузки"""
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration

    i = 0
    while time.time() < end_time:
        print(f'\\r{chars[i % len(chars)]} {text}', end='', flush=True)
        time.sleep(0.1)
        i += 1

    print('\\r' + ' ' * (len(text) + 3), end='\\r')  # Очистка

# Использование
loading_animation('Подготовка игры', 1)
```

## 🔄 Шаг 5: Игровое меню

```python
def show_menu():
    """Главное меню"""
    while True:
        print('\\n' + '='*40)
        print('🎮 УГАДАЙ ЧИСЛО')
        print('='*40)
        print('1. 🎯 Играть')
        print('2. 🏆 Рекорды')
        print('3. ℹ️  Правила')
        print('4. 🚪 Выход')

        choice = input('\\nВыбери действие: ')

        if choice == '1':
            play_game()
        elif choice == '2':
            show_records()
        elif choice == '3':
            show_rules()
        elif choice == '4':
            print('\\nСпасибо за игру! 👋')
            break
        else:
            print('❌ Неверный выбор!')

def show_rules():
    """Показывает правила"""
    print('\\n' + '='*40)
    print('📜 ПРАВИЛА ИГРЫ')
    print('='*40)
    print('1. Компьютер загадывает число')
    print('2. Угадай его за ограниченное число попыток')
    print('3. После каждой попытки получишь подсказку')
    print('4. Чем быстрее угадаешь, тем больше очков!')
    input('\\nНажми Enter для продолжения...')
```

## 🎮 Полный пример: Продвинутая игра

```python
import random
import time

class Game:
    def __init__(self):
        self.records = []
        self.difficulty_settings = {
            '1': {'min': 1, 'max': 50, 'attempts': 10, 'name': 'Легко'},
            '2': {'min': 1, 'max': 100, 'attempts': 7, 'name': 'Средне'},
            '3': {'min': 1, 'max': 200, 'attempts': 5, 'name': 'Сложно'}
        }

    def play(self):
        # Выбор сложности
        settings = self.choose_difficulty()

        # Игровая сессия
        secret = random.randint(settings['min'], settings['max'])
        attempts = 0

        print(f"\\n🎯 Начинаем! Уровень: {settings['name']}")
        print(f"Число от {settings['min']} до {settings['max']}")
        print(f"Попыток: {settings['attempts']}\\n")

        # Игровой цикл
        while attempts < settings['attempts']:
            attempts += 1
            guess = self.get_input(attempts, settings['attempts'])

            if guess == secret:
                score = self.calculate_score(attempts, settings['attempts'])
                print(f"\\n🎉 ПОБЕДА! Очков: {score}")
                self.save_result(score)
                return

            self.give_hint(guess, secret)

        print(f"\\n💀 Попытки кончились! Было: {secret}")

    def choose_difficulty(self):
        print('\\nВыбери сложность:')
        for key, settings in self.difficulty_settings.items():
            print(f"{key} - {settings['name']}")

        choice = input('\\nТвой выбор: ')
        return self.difficulty_settings.get(choice, self.difficulty_settings['2'])

    def get_input(self, current, maximum):
        while True:
            try:
                guess = int(input(f'Попытка {current}/{maximum}: '))
                return guess
            except ValueError:
                print('❌ Введи число!')

    def give_hint(self, guess, secret):
        diff = abs(secret - guess)

        if diff > 50:
            print('🥶 Очень холодно!')
        elif diff > 20:
            print('❄️ Холодно')
        elif diff > 10:
            print('🌡️ Тепло')
        elif diff > 5:
            print('🔥 Горячо!')
        else:
            print('🔥🔥 Очень горячо!')

        if guess < secret:
            print('↗️ Больше')
        else:
            print('↘️ Меньше')

    def calculate_score(self, attempts, max_attempts):
        return max(1000 - (attempts - 1) * 100, 100)

    def save_result(self, score):
        name = input('\\nТвоё имя: ')
        self.records.append({'name': name, 'score': score})
        self.records.sort(key=lambda x: x['score'], reverse=True)

# Запуск
game = Game()
game.play()
```

## 📚 Что дальше?

### Простые улучшения:
- Звуки (библиотека `playsound`)
- Сохранение рекордов в файл
- Разные режимы игры

### Более сложные проекты:
- Текстовая RPG
- Игра с ASCII-графикой
- Игра с Pygame (графика!)

## 🎓 Советы по созданию игр

1. **Начни с простого** - сначала базовая версия
2. **Добавляй по одной фиче** - тестируй после каждой
3. **Используй функции** - разбивай на части
4. **Тестируй часто** - проверяй каждое изменение
5. **Спрашивай мнение** - дай поиграть друзьям

## 💡 Идеи для практики

Попробуй переделать игру "Угадай число":
- В викторину
- В поиск сокровищ
- В угадывание слова
- В математическую игру

Главное - начни программировать! 🚀
