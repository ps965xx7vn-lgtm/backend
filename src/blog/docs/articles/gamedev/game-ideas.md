# 10 идей для игр на Python 🎮

Хочешь создать свою игру? Вот 10 идей от простых к сложным с готовым кодом!

## 1. 🎲 Угадай число

**Сложность:** ⭐ Легко
**Что нужно знать:** random, циклы, if/else

```python
import random

secret = random.randint(1, 100)
attempts = 0

print('🎲 Угадай число от 1 до 100!\\n')

while True:
    guess = int(input('Твоё число: '))
    attempts += 1

    if guess == secret:
        print(f'🎉 Угадал за {attempts} попыток!')
        break
    elif guess < secret:
        print('↗️ Больше!')
    else:
        print('↘️ Меньше!')
```

**Идеи улучшений:**
- Уровни сложности (разные диапазоны)
- Подсказки (горячо/холодно)
- Ограничение попыток
- Таблица рекордов

## 2. ✊✋✌️ Камень-Ножницы-Бумага

**Сложность:** ⭐ Легко
**Что нужно знать:** random, словари, логика

```python
import random

choices = ['камень', 'ножницы', 'бумага']
wins = {'камень': 'ножницы', 'ножницы': 'бумага', 'бумага': 'камень'}

score = {'player': 0, 'computer': 0}

while True:
    print(f'\\n🎮 Счёт {score["player"]}:{score["computer"]}')

    player = input('Твой выбор (или "выход"): ').lower()
    if player == 'выход':
        break

    if player not in choices:
        print('❌ Неверный выбор!')
        continue

    computer = random.choice(choices)
    print(f'Компьютер: {computer}')

    if player == computer:
        print('Ничья!')
    elif wins[player] == computer:
        print('✅ Ты выиграл!')
        score['player'] += 1
    else:
        print('❌ Компьютер выиграл!')
        score['computer'] += 1

print(f'\\nИтоговый счёт: {score["player"]}:{score["computer"]}')
```

**Идеи улучшений:**
- Добавить "ящерица" и "Спок"
- Режим до N побед
- Статистика выборов

## 3. 🔤 Виселица (Hangman)

**Сложность:** ⭐⭐ Средне
**Что нужно знать:** строки, списки, множества

```python
import random

words = ['python', 'программа', 'компьютер', 'игра', 'код']
word = random.choice(words)
guessed = set()
attempts = 6

print('🔤 ВИСЕЛИЦА\\n')

while attempts > 0:
    # Показываем текущее состояние
    display = ''.join(letter if letter in guessed else '_' for letter in word)
    print(f'\\nСлово: {display}')
    print(f'Попыток: {attempts}')
    print(f'Использовано: {" ".join(sorted(guessed))}')

    # Проверка победы
    if '_' not in display:
        print('\\n🎉 Ты выиграл!')
        break

    # Ввод буквы
    letter = input('\\nВведи букву: ').lower()

    if len(letter) != 1:
        print('❌ Введи одну букву!')
        continue

    if letter in guessed:
        print('⚠️ Уже использовал!')
        continue

    guessed.add(letter)

    if letter not in word:
        attempts -= 1
        print('❌ Неверно!')
else:
    print(f'\\n💀 Проигрыш! Было: {word}')
```

**Идеи улучшений:**
- ASCII-рисунок виселицы
- Разные категории слов
- Подсказки

## 4. 🐍 Змейка (текстовая версия)

**Сложность:** ⭐⭐⭐ Сложно
**Что нужно знать:** списки, координаты, логика движения

```python
import random
import time
import os

# Настройки
width, height = 10, 10
snake = [[5, 5], [5, 4], [5, 3]]
direction = 'right'
food = [random.randint(0, width-1), random.randint(0, height-1)]
score = 0

def draw():
    os.system('clear' if os.name == 'posix' else 'cls')

    print(f'🐍 Змейка | Счёт: {score}\\n')

    for y in range(height):
        for x in range(width):
            if [x, y] == snake[0]:
                print('🟢', end='')
            elif [x, y] in snake:
                print('🟩', end='')
            elif [x, y] == food:
                print('🍎', end='')
            else:
                print('⬜', end='')
        print()

    print('\\nУправление: w/a/s/d или стрелки')

# Основной цикл игры (упрощённая версия для демонстрации)
while True:
    draw()

    # Автоматическое движение (для демо)
    head = snake[0].copy()

    if direction == 'right':
        head[0] += 1
    elif direction == 'left':
        head[0] -= 1
    elif direction == 'up':
        head[1] -= 1
    elif direction == 'down':
        head[1] += 1

    # Проверка границ
    if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
        print('💀 Врезался в стену!')
        break

    # Проверка еды
    if head == food:
        score += 1
        food = [random.randint(0, width-1), random.randint(0, height-1)]
    else:
        snake.pop()

    snake.insert(0, head)
    time.sleep(0.3)
```

**Идеи улучшений:**
- Управление клавишами (библиотека keyboard)
- Разные уровни скорости
- Препятствия

## 5. 🎰 Слот-машина

**Сложность:** ⭐⭐ Средне
**Что нужно знать:** random, списки, подсчёт

```python
import random
import time

symbols = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
balance = 100

def spin():
    """Крутит барабаны"""
    return [random.choice(symbols) for _ in range(3)]

def calculate_win(reels):
    """Подсчитывает выигрыш"""
    if reels[0] == reels[1] == reels[2]:
        if reels[0] == '💎':
            return 50
        elif reels[0] == '7️⃣':
            return 30
        else:
            return 10
    elif reels[0] == reels[1] or reels[1] == reels[2]:
        return 2
    return 0

print('🎰 СЛОТ-МАШИНА\\n')

while balance > 0:
    print(f'💰 Баланс: {balance} монет')
    bet = input('\\nСтавка (или "выход"): ')

    if bet == 'выход':
        break

    bet = int(bet)
    if bet > balance:
        print('❌ Недостаточно денег!')
        continue

    balance -= bet

    # Анимация
    for _ in range(5):
        reels = spin()
        print(f'\\r{" ".join(reels)}', end='', flush=True)
        time.sleep(0.1)

    # Финальный результат
    reels = spin()
    print(f'\\r{" ".join(reels)}')

    win = calculate_win(reels) * bet
    if win > 0:
        print(f'\\n🎉 Выигрыш: {win} монет!')
        balance += win
    else:
        print('\\n💀 Проигрыш!')

print(f'\\nИтоговый баланс: {balance} монет')
```

**Идеи улучшений:**
- Разные типы ставок
- Бонусные игры
- Прогресс-бары

## 6. 🎯 Быки и коровы

**Сложность:** ⭐⭐ Средне
**Что нужно знать:** строки, списки, логика

```python
import random

secret = ''.join(random.sample('0123456789', 4))
attempts = 0

print('🎯 БЫКИ И КОРОВЫ')
print('Угадай 4-значное число (цифры не повторяются)\\n')

while True:
    guess = input('Твоё число: ')
    attempts += 1

    if len(guess) != 4 or not guess.isdigit():
        print('❌ Введи 4 цифры!')
        continue

    if guess == secret:
        print(f'🎉 Угадал за {attempts} попыток!')
        break

    bulls = sum(g == s for g, s in zip(guess, secret))
    cows = sum(g in secret for g in guess) - bulls

    print(f'🐂 Быков: {bulls}, 🐄 Коров: {cows}')
```

**Подсказка:**
- Бык = правильная цифра на правильном месте
- Корова = правильная цифра на неправильном месте

## 7. 🃏 Блэкджек (упрощённый)

**Сложность:** ⭐⭐⭐ Сложно
**Что нужно знать:** списки, словари, логика игры

```python
import random

def create_deck():
    """Создаёт колоду"""
    values = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    suits = ['♠','♥','♦','♣']
    return [{'value': v, 'suit': s} for v in values for s in suits]

def card_value(card):
    """Значение карты"""
    if card['value'] in ['J', 'Q', 'K']:
        return 10
    elif card['value'] == 'A':
        return 11
    return int(card['value'])

def hand_value(hand):
    """Сумма руки"""
    total = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card['value'] == 'A')

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

# Игра
deck = create_deck()
random.shuffle(deck)

player = [deck.pop(), deck.pop()]
dealer = [deck.pop(), deck.pop()]

print('🃏 БЛЭКДЖЕК\\n')
print(f'Твои карты: {player[0]["value"]}{player[0]["suit"]} {player[1]["value"]}{player[1]["suit"]} ({hand_value(player)})')
print(f'Карта дилера: {dealer[0]["value"]}{dealer[0]["suit"]}\\n')

# Ход игрока
while hand_value(player) < 21:
    action = input('Ещё карту? (да/нет): ').lower()
    if action == 'да':
        card = deck.pop()
        player.append(card)
        print(f'Взял: {card["value"]}{card["suit"]}')
        print(f'Сумма: {hand_value(player)}')
    else:
        break

player_sum = hand_value(player)
dealer_sum = hand_value(dealer)

# Ход дилера
if player_sum <= 21:
    print(f'\\nДилер открывает: {dealer[1]["value"]}{dealer[1]["suit"]} ({dealer_sum})')

    while dealer_sum < 17:
        card = deck.pop()
        dealer.append(card)
        dealer_sum = hand_value(dealer)
        print(f'Дилер взял: {card["value"]}{card["suit"]} ({dealer_sum})')

# Результат
print()
if player_sum > 21:
    print('💀 Перебор! Проигрыш')
elif dealer_sum > 21:
    print('🎉 Дилер перебрал! Победа!')
elif player_sum > dealer_sum:
    print('🎉 Победа!')
elif player_sum < dealer_sum:
    print('💀 Проигрыш')
else:
    print('🤝 Ничья')
```

## 8. 🏃 Бесконечный бегун (текстовый)

**Сложность:** ⭐⭐⭐ Сложно
**Что нужно знать:** время, анимация, реакция

```python
import random
import time
import sys

score = 0
position = 1
game_over = False

print('🏃 БЕСКОНЕЧНЫЙ БЕГУН')
print('Прыгай пробелом, избегай препятствий!\\n')
time.sleep(2)

while not game_over:
    # Генерируем поле
    obstacle = random.random() < 0.3

    # Отображение
    track = ['_'] * 5
    if obstacle:
        track[0] = '🌵'
    if position == 1:
        track[position] = '🏃'

    print('\\r' + ''.join(track), end='', flush=True)

    # Проверка столкновения
    if obstacle and position == 0:
        game_over = True
        print('\\n💀 Врезался!')
        break

    score += 1
    time.sleep(0.3)

print(f'Счёт: {score}')
```

## 9. 🧩 Крестики-нолики с ИИ

**Сложность:** ⭐⭐⭐ Сложно
**Что нужно знать:** двумерные списки, минимакс (упрощённый)

```python
board = [[' ' for _ in range(3)] for _ in range(3)]

def print_board():
    print('\\n  0 1 2')
    for i, row in enumerate(board):
        print(f'{i} {"|".join(row)}')
        if i < 2:
            print('  -----')

def check_win(player):
    # Проверка линий
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):
            return True
        if all(board[j][i] == player for j in range(3)):
            return True

    # Диагонали
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True

    return False

def ai_move():
    # Простой ИИ - первая свободная клетка
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                return

# Игра
print('❌⭕ КРЕСТИКИ-НОЛИКИ')

for turn in range(9):
    print_board()

    if turn % 2 == 0:
        # Ход игрока
        row = int(input('\\nТвой ход, строка: '))
        col = int(input('Столбец: '))

        if board[row][col] == ' ':
            board[row][col] = 'X'
        else:
            print('Занято!')
            continue

        if check_win('X'):
            print_board()
            print('\\n🎉 Ты выиграл!')
            break
    else:
        # Ход ИИ
        ai_move()
        print('\\nХод компьютера')

        if check_win('O'):
            print_board()
            print('\\n💀 Компьютер выиграл!')
            break
else:
    print_board()
    print('\\n🤝 Ничья!')
```

## 10. 🎲 Текстовая RPG

**Сложность:** ⭐⭐⭐⭐ Очень сложно
**Что нужно знать:** классы, словари, игровая логика

```python
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.gold = 0
        self.inventory = []

    def is_alive(self):
        return self.hp > 0

class Enemy:
    def __init__(self, name, hp, damage, gold):
        self.name = name
        self.hp = hp
        self.damage = damage
        self.gold = gold

# Враги
enemies = [
    Enemy('Слизень', 20, 5, 10),
    Enemy('Гоблин', 40, 10, 25),
    Enemy('Орк', 60, 15, 50),
    Enemy('Дракон', 100, 25, 100)
]

# Игра
player = Player(input('Твоё имя: '))
print(f'\\nДобро пожаловать, {player.name}!\\n')

while player.is_alive():
    print(f'HP: {player.hp} | Золото: {player.gold}')
    print('\\n1. Искать врага')
    print('2. Отдохнуть (+20 HP)')
    print('3. Выход')

    choice = input('\\nДействие: ')

    if choice == '1':
        enemy = random.choice(enemies)
        print(f'\\n⚔️ Встретил: {enemy.name}!')

        while enemy.hp > 0 and player.is_alive():
            action = input('\\n[a]така / [б]ежать: ').lower()

            if action == 'a':
                damage = random.randint(10, 20)
                enemy.hp -= damage
                print(f'Нанёс {damage} урона!')

                if enemy.hp > 0:
                    player.hp -= enemy.damage
                    print(f'{enemy.name} нанёс {enemy.damage} урона!')
            else:
                print('Сбежал!')
                break

        if enemy.hp <= 0:
            print(f'\\n🎉 Победил {enemy.name}!')
            player.gold += enemy.gold
            print(f'Получил {enemy.gold} золота')

    elif choice == '2':
        player.hp = min(player.hp + 20, 100)
        print('Отдохнул (+20 HP)')

    elif choice == '3':
        break

print(f'\\nИгра окончена! Золото: {player.gold}')
```

## 🎓 Советы

1. **Начни с простого** - не пытайся сразу сделать сложную игру
2. **Тестируй часто** - после каждой новой фичи
3. **Добавляй постепенно** - сначала базовая механика, потом улучшения
4. **Играй сам** - лучший способ найти баги
5. **Дай поиграть друзьям** - они найдут то, что ты не заметил

## 🚀 Что дальше?

После текстовых игр попробуй:
- **Pygame** - 2D игры с графикой
- **Turtle** - простая графическая библиотека
- **Tkinter** - GUI для твоих игр

Создавай игры и учись программировать! 🎮
