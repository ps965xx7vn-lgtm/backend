# Python Achievements System — Gamification! 🏆

## Что такое система достижений?

**Achievements (Ачивки)** — награды за выполнение задач.

### Почему это важно?
```
Достижения = Мотивация + Вовлечённость
```

**Gamification увеличивает retention на 30-40%!** 🎮

---

## Базовая система достижений

### Achievement Class:

```python
class Achievement:
    """Достижение."""

    def __init__(self, id, name, description, points, condition):
        """
        Args:
            id: Уникальный ID
            name: Название
            description: Описание
            points: Сколько очков даёт
            condition: Функция проверки (вернёт True/False)
        """
        self.id = id
        self.name = name
        self.description = description
        self.points = points
        self.condition = condition
        self.unlocked = False
        self.unlocked_at = None

    def check(self, user_data):
        """Проверить, разблокировано ли."""
        if self.unlocked:
            return False  # Уже есть

        if self.condition(user_data):
            self.unlocked = True
            from datetime import datetime
            self.unlocked_at = datetime.now()
            return True

        return False

    def __str__(self):
        status = "🔓" if self.unlocked else "🔒"
        return f"{status} {self.name} ({self.points} pts)"

# Примеры условий
def first_login(data):
    """Первый вход."""
    return data.get("logins", 0) >= 1

def power_user(data):
    """100+ входов."""
    return data.get("logins", 0) >= 100

# Создание достижений
achievements = [
    Achievement(
        id="first_login",
        name="Первый шаг",
        description="Войди в систему первый раз",
        points=10,
        condition=first_login
    ),
    Achievement(
        id="power_user",
        name="Активист",
        description="100 входов",
        points=100,
        condition=power_user
    )
]

# Проверка
user = {"logins": 1}

for ach in achievements:
    if ach.check(user):
        print(f"🎉 Разблокировано: {ach.name} (+{ach.points} pts)")
```

---

## Progress Tracking (Отслеживание прогресса)

### ProgressTracker Class:

```python
class ProgressTracker:
    """Отслеживание прогресса пользователя."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.stats = {
            "logins": 0,
            "tasks_completed": 0,
            "points_earned": 0,
            "days_active": 0,
            "streak": 0,  # Дни подряд
            "lessons_finished": 0,
            "code_lines": 0
        }
        self.achievements_unlocked = []
        self.last_active = None

    def record_action(self, action_type, value=1):
        """Записать действие."""
        if action_type in self.stats:
            self.stats[action_type] += value

        # Проверка streak
        from datetime import datetime, timedelta
        today = datetime.now().date()

        if self.last_active:
            last_date = self.last_active.date()
            if today == last_date + timedelta(days=1):
                self.stats["streak"] += 1
            elif today != last_date:
                self.stats["streak"] = 1
        else:
            self.stats["streak"] = 1

        self.last_active = datetime.now()

    def get_progress_percent(self, achievement):
        """% прогресса до achievement."""
        # Если уже разблокировано
        if achievement.unlocked:
            return 100

        # Примерная проверка (упрощённо)
        # В реальности нужно parse condition
        return min(100, (self.stats.get("tasks_completed", 0) / 10) * 100)

    def get_summary(self):
        """Сводка прогресса."""
        return {
            "total_points": self.stats["points_earned"],
            "achievements": len(self.achievements_unlocked),
            "streak": self.stats["streak"],
            "tasks": self.stats["tasks_completed"]
        }

# Использование
tracker = ProgressTracker(user_id=1)

# Пользователь выполняет действия
tracker.record_action("logins")
tracker.record_action("tasks_completed")
tracker.record_action("points_earned", 50)

print(tracker.get_summary())
# {'total_points': 50, 'achievements': 0, 'streak': 1, 'tasks': 1}
```

---

## Achievement Manager

### Центральная система управления:

```python
class AchievementManager:
    """Управление всеми достижениями."""

    def __init__(self):
        self.achievements = []
        self.user_progresses = {}

    def register_achievement(self, achievement):
        """Зарегистрировать achievement."""
        self.achievements.append(achievement)

    def get_user_progress(self, user_id):
        """Получить прогресс пользователя."""
        if user_id not in self.user_progresses:
            self.user_progresses[user_id] = ProgressTracker(user_id)
        return self.user_progresses[user_id]

    def check_achievements(self, user_id):
        """Проверить все достижения для пользователя."""
        tracker = self.get_user_progress(user_id)
        newly_unlocked = []

        for achievement in self.achievements:
            if achievement.check(tracker.stats):
                tracker.achievements_unlocked.append(achievement.id)
                tracker.stats["points_earned"] += achievement.points
                newly_unlocked.append(achievement)

        return newly_unlocked

    def get_user_achievements(self, user_id):
        """Все достижения пользователя."""
        tracker = self.get_user_progress(user_id)

        result = {
            "unlocked": [],
            "locked": [],
            "total_points": tracker.stats["points_earned"]
        }

        for ach in self.achievements:
            if ach.id in tracker.achievements_unlocked:
                result["unlocked"].append({
                    "name": ach.name,
                    "points": ach.points,
                    "unlocked_at": ach.unlocked_at
                })
            else:
                result["locked"].append({
                    "name": ach.name,
                    "description": ach.description,
                    "points": ach.points
                })

        return result

# Пример использования
manager = AchievementManager()

# Регистрация достижений
manager.register_achievement(Achievement(
    "first_task", "Начало пути", "Выполни первую задачу",
    points=10,
    condition=lambda data: data.get("tasks_completed", 0) >= 1
))

manager.register_achievement(Achievement(
    "task_master", "Мастер задач", "Выполни 50 задач",
    points=200,
    condition=lambda data: data.get("tasks_completed", 0) >= 50
))

# Пользователь делает задачу
tracker = manager.get_user_progress(user_id=1)
tracker.record_action("tasks_completed")

# Проверка
new_achievements = manager.check_achievements(user_id=1)

for ach in new_achievements:
    print(f"🎉 {ach.name} (+{ach.points} pts)")
```

---

## Типы достижений

### 1. Milestone Achievements (За количество):

```python
def create_milestone_achievement(name, stat_key, threshold, points):
    """Achievement за достижение числа."""
    return Achievement(
        id=f"{stat_key}_{threshold}",
        name=name,
        description=f"Достигни {threshold} {stat_key}",
        points=points,
        condition=lambda data: data.get(stat_key, 0) >= threshold
    )

# Примеры
milestones = [
    create_milestone_achievement("Новичок", "lessons_finished", 1, 10),
    create_milestone_achievement("Ученик", "lessons_finished", 5, 50),
    create_milestone_achievement("Эксперт", "lessons_finished", 20, 200),
    create_milestone_achievement("Мастер", "lessons_finished", 50, 500)
]
```

### 2. Streak Achievements (За streak):

```python
def create_streak_achievement(days, points):
    """Achievement за дни подряд."""
    return Achievement(
        id=f"streak_{days}",
        name=f"{days} дней подряд",
        description=f"Заходи {days} дней подряд",
        points=points,
        condition=lambda data: data.get("streak", 0) >= days
    )

streaks = [
    create_streak_achievement(3, 30),
    create_streak_achievement(7, 100),
    create_streak_achievement(30, 500),
    create_streak_achievement(100, 2000)
]
```

### 3. Challenge Achievements (Особые):

```python
# Комбинированные условия
def early_bird_condition(data):
    """Ранняя пташка — зайти до 6 утра."""
    if not data.get("last_login_hour"):
        return False
    return data["last_login_hour"] < 6

def night_owl_condition(data):
    """Сова — зайти после 23:00."""
    if not data.get("last_login_hour"):
        return False
    return data["last_login_hour"] >= 23

challenges = [
    Achievement(
        "early_bird", "Ранняя пташка", "Зайди до 6:00", 50, early_bird_condition
    ),
    Achievement(
        "night_owl", "Сова", "Зайти после 23:00", 50, night_owl_condition
    )
]
```

---

## Badges & Tiers (Бейджи и уровни)

### Система уровней:

```python
class BadgeSystem:
    """Система бейджей."""

    TIERS = [
        {"name": "Новичок", "min_points": 0, "badge": "🥉"},
        {"name": "Ученик", "min_points": 100, "badge": "🥈"},
        {"name": "Эксперт", "min_points": 500, "badge": "🥇"},
        {"name": "Мастер", "min_points": 1000, "badge": "💎"},
        {"name": "Легенда", "min_points": 5000, "badge": "👑"}
    ]

    @classmethod
    def get_tier(cls, points):
        """Получить уровень по очкам."""
        current_tier = cls.TIERS[0]

        for tier in cls.TIERS:
            if points >= tier["min_points"]:
                current_tier = tier
            else:
                break

        return current_tier

    @classmethod
    def get_next_tier(cls, points):
        """Следующий уровень."""
        for tier in cls.TIERS:
            if points < tier["min_points"]:
                return tier
        return None

    @classmethod
    def progress_to_next(cls, points):
        """Прогресс до следующего уровня."""
        next_tier = cls.get_next_tier(points)

        if not next_tier:
            return 100  # Максимум

        current = cls.get_tier(points)
        needed = next_tier["min_points"] - current["min_points"]
        earned = points - current["min_points"]

        return (earned / needed) * 100 if needed > 0 else 100

# Использование
user_points = 350

tier = BadgeSystem.get_tier(user_points)
print(f"Текущий уровень: {tier['badge']} {tier['name']}")

next_tier = BadgeSystem.get_next_tier(user_points)
if next_tier:
    progress = BadgeSystem.progress_to_next(user_points)
    print(f"До {next_tier['name']}: {progress:.1f}%")
```

---

## Leaderboard (Таблица лидеров)

### Ranking система:

```python
class Leaderboard:
    """Таблица лидеров."""

    def __init__(self):
        self.users = []

    def add_user(self, user_id, username, points):
        """Добавить пользователя."""
        self.users.append({
            "user_id": user_id,
            "username": username,
            "points": points
        })

    def get_rankings(self, limit=10):
        """Топ пользователей."""
        sorted_users = sorted(
            self.users,
            key=lambda x: x["points"],
            reverse=True
        )

        # Добавить позицию
        for i, user in enumerate(sorted_users[:limit], 1):
            user["rank"] = i

            # Медали для топ-3
            if i == 1:
                user["medal"] = "🥇"
            elif i == 2:
                user["medal"] = "🥈"
            elif i == 3:
                user["medal"] = "🥉"
            else:
                user["medal"] = ""

        return sorted_users[:limit]

    def get_user_rank(self, user_id):
        """Позиция пользователя."""
        sorted_users = sorted(
            self.users,
            key=lambda x: x["points"],
            reverse=True
        )

        for i, user in enumerate(sorted_users, 1):
            if user["user_id"] == user_id:
                return {
                    "rank": i,
                    "total_users": len(self.users),
                    "percentile": ((len(self.users) - i) / len(self.users)) * 100
                }

        return None

# Пример
leaderboard = Leaderboard()

leaderboard.add_user(1, "Alice", 5000)
leaderboard.add_user(2, "Bob", 3500)
leaderboard.add_user(3, "Charlie", 4200)
leaderboard.add_user(4, "Diana", 2800)

print("🏆 Топ пользователей:")
for user in leaderboard.get_rankings():
    medal = user.get("medal", "")
    print(f"{medal} #{user['rank']} {user['username']}: {user['points']} pts")

# Позиция конкретного пользователя
rank_info = leaderboard.get_user_rank(4)
print(f"\nВаша позиция: #{rank_info['rank']}/{rank_info['total_users']}")
print(f"Топ {rank_info['percentile']:.0f}%")
```

---

## Notifications & Rewards

### Система уведомлений:

```python
class AchievementNotification:
    """Уведомления о достижениях."""

    @staticmethod
    def show_unlock(achievement):
        """Показать разблокировку."""
        print("=" * 50)
        print("🎉 ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО! 🎉")
        print("=" * 50)
        print(f"✨ {achievement.name}")
        print(f"📝 {achievement.description}")
        print(f"⭐ +{achievement.points} очков")
        print("=" * 50)

    @staticmethod
    def show_progress(achievement, percent):
        """Показать прогресс."""
        bar_length = 20
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"{achievement.name}: [{bar}] {percent:.0f}%")

    @staticmethod
    def show_tier_up(old_tier, new_tier):
        """Повышение уровня."""
        print("=" * 50)
        print("🎊 ПОВЫШЕНИЕ УРОВНЯ! 🎊")
        print("=" * 50)
        print(f"{old_tier['badge']} {old_tier['name']} → {new_tier['badge']} {new_tier['name']}")
        print("=" * 50)

# Пример
achievement = Achievement(
    "master", "Мастер Python", "Выполни 100 задач",
    points=500,
    condition=lambda x: x.get("tasks", 0) >= 100
)

# При разблокировке
AchievementNotification.show_unlock(achievement)

# Прогресс
AchievementNotification.show_progress(achievement, 75)
```

---

## Полная система

### Собираем всё вместе:

```python
class GamificationSystem:
    """Полная система gamification."""

    def __init__(self):
        self.achievement_manager = AchievementManager()
        self.badge_system = BadgeSystem()
        self.leaderboard = Leaderboard()

        # Регистрируем стандартные achievements
        self._register_default_achievements()

    def _register_default_achievements(self):
        """Базовые достижения."""
        # Milestones
        for tasks in [1, 10, 50, 100]:
            self.achievement_manager.register_achievement(
                create_milestone_achievement(
                    f"{tasks} задач",
                    "tasks_completed",
                    tasks,
                    tasks * 10
                )
            )

        # Streaks
        for days in [3, 7, 30]:
            self.achievement_manager.register_achievement(
                create_streak_achievement(days, days * 10)
            )

    def record_user_action(self, user_id, action_type, value=1):
        """Записать действие пользователя."""
        # Обновить tracker
        tracker = self.achievement_manager.get_user_progress(user_id)
        old_points = tracker.stats["points_earned"]
        old_tier = self.badge_system.get_tier(old_points)

        tracker.record_action(action_type, value)

        # Проверить achievements
        new_achievements = self.achievement_manager.check_achievements(user_id)

        # Показать уведомления
        for ach in new_achievements:
            AchievementNotification.show_unlock(ach)

        # Проверить tier up
        new_points = tracker.stats["points_earned"]
        new_tier = self.badge_system.get_tier(new_points)

        if new_tier["name"] != old_tier["name"]:
            AchievementNotification.show_tier_up(old_tier, new_tier)

        # Обновить leaderboard
        self._update_leaderboard(user_id, new_points)

    def _update_leaderboard(self, user_id, points):
        """Обновить leaderboard."""
        # Удалить старую запись
        self.leaderboard.users = [
            u for u in self.leaderboard.users if u["user_id"] != user_id
        ]

        # Добавить новую
        self.leaderboard.add_user(user_id, f"User{user_id}", points)

    def get_user_dashboard(self, user_id):
        """Дашборд пользователя."""
        tracker = self.achievement_manager.get_user_progress(user_id)
        points = tracker.stats["points_earned"]
        tier = self.badge_system.get_tier(points)
        rank_info = self.leaderboard.get_user_rank(user_id)

        return {
            "tier": tier,
            "points": points,
            "rank": rank_info,
            "achievements": self.achievement_manager.get_user_achievements(user_id),
            "stats": tracker.stats
        }

# Использование
system = GamificationSystem()

# Пользователь выполняет задачи
system.record_user_action(user_id=1, action_type="tasks_completed")
system.record_user_action(user_id=1, action_type="tasks_completed")
system.record_user_action(user_id=1, action_type="tasks_completed")

# Dashboard
dashboard = system.get_user_dashboard(user_id=1)
print(f"\n{dashboard['tier']['badge']} {dashboard['tier']['name']}")
print(f"Очки: {dashboard['points']}")
print(f"Разблокировано ачивок: {len(dashboard['achievements']['unlocked'])}")
```

---

## Частые ошибки

### ❌ Ошибка 1: Слишком легкие достижения
```python
# ПЛОХО: разблокируется сразу
Achievement("easy", "Привет", "Просто зайди", 1000,
            lambda x: True)  # Слишком легко!

# ✅ ХОРОШО: реальные цели
Achievement("hard", "Мастер", "100 задач", 500,
            lambda x: x.get("tasks", 0) >= 100)
```

### ❌ Ошибка 2: Слишком сложные
```python
# ПЛОХО: impossible
Achievement("impossible", "Бог", "1 миллион задач", 1,
            lambda x: x.get("tasks", 0) >= 1000000)  # Нереально!

# ✅ ХОРОШО: challenging, но достижимо
Achievement("challenge", "Герой", "500 задач", 1000,
            lambda x: x.get("tasks", 0) >= 500)
```

### ❌ Ошибка 3: Нет прогресса
```python
# ПЛОХО: не показываем прогресс
show_only_unlocked()  # Пользователь не знает, к чему стремиться

# ✅ ХОРОШО: показываем прогресс
for ach in all_achievements:
    progress = tracker.get_progress_percent(ach)
    AchievementNotification.show_progress(ach, progress)
```

---

## Best Practices

### 1. Балансировка наград:
```python
reward_tiers = {
    "easy": (1, 50),      # Первые достижения
    "medium": (50, 200),  # Средние
    "hard": (200, 500),   # Сложные
    "epic": (500, 2000)   # Эпические
}
```

### 2. Разнообразие:
```python
achievement_types = [
    "milestones",    # За количество
    "streaks",       # За регулярность
    "challenges",    # За особые условия
    "hidden",        # Секретные (не показываем условие)
    "time_limited"   # Ограниченные по времени
]
```

### 3. Engagement Loops:
```python
def create_engagement_loop():
    """Цикл вовлечённости."""
    steps = [
        "1. Пользователь видит прогресс",
        "2. Почти разблокировал ачивку (80%)",
        "3. Мотивация завершить",
        "4. Разблокировка → радость",
        "5. Видит следующую ачивку",
        "6. Цикл повторяется"
    ]
    return steps
```

---

## Резюме

### Компоненты системы:
```python
components = {
    "Achievement": "Само достижение",
    "ProgressTracker": "Отслеживание прогресса",
    "AchievementManager": "Управление всем",
    "BadgeSystem": "Уровни и бейджи",
    "Leaderboard": "Таблица лидеров",
    "Notifications": "Уведомления"
}
```

### Типы достижений:
```python
types = {
    "Milestone": "За достижение числа (10, 50, 100 задач)",
    "Streak": "За дни подряд (3, 7, 30 дней)",
    "Challenge": "За особые условия (early bird, night owl)",
    "Hidden": "Секретные (условие скрыто)",
    "Tier": "Уровни (новичок → мастер)"
}
```

### Баланс системы:
- ⚡ **Первые ачивки** — быстро, для onboarding
- 📈 **Средние** — регулярно, для retention
- 🏆 **Сложные** — редко, для престижа
- 👑 **Эпические** — очень редко, легенды

Создай систему достижений и увлеки пользователей! 🎮🚀
