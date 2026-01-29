import json
import os

# Меняем директорию
os.chdir("/Users/dmitrii/Documents/GitHub/pyschool_delete_css/backend")

# Читаем файл
with open("docs/examples/git_github_course_practical.json", encoding="utf-8") as f:
    data = json.load(f)

# Находим урок 1
lesson1 = data["ru"]["lessons"][0]

print(f"До исправления: {len(lesson1['steps'])} шагов")

# Удаляем шаг 20 (Итоги дня 1)
if len(lesson1["steps"]) > 19:
    lesson1["steps"].pop()

# Обновляем шаг 19 (теперь последний) - добавляем self_check_items
step19 = lesson1["steps"][18]
step19["self_check_items"] = [
    "Мой сайт работает по ссылке username.github.io/my-portfolio",
    "На GitHub видны все 6 коммитов",
    "Репозиторий публичный (Public)",
    "Я скопировал ссылку на репозиторий",
    "Готов отправить на проверку",
]
# Убираем старый self_check если есть
if "self_check" in step19:
    del step19["self_check"]

# Обновляем шаг 18 - добавляем self_check_items и упрощаем repair
step18 = lesson1["steps"][17]
step18["self_check_items"] = [
    "Контакты добавлены локально",
    "Коммит создан и отправлен",
    "На сайте появились контакты",
    "Сайт работает на GitHub Pages",
]
step18["repair_description"] = "Подожди 1-2 минуты, очисти кэш Ctrl+Shift+R"
# Убираем старый self_check
if "self_check" in step18:
    del step18["self_check"]

# Добавляем self_check_items во все остальные шаги где есть self_check
for step in lesson1["steps"]:
    if "self_check" in step and "self_check_items" not in step:
        # Разбиваем self_check на список по строкам начинающимся с ✅
        lines = [
            line.strip().lstrip("✅").strip()
            for line in step["self_check"].split("\n")
            if line.strip().startswith("✅")
        ]
        if lines:
            step["self_check_items"] = lines
            del step["self_check"]

print(f"После исправления: {len(lesson1['steps'])} шагов")
print(f"Шаг 18 имеет {len(step18['self_check_items'])} чекбоксов")
print(f"Шаг 19 имеет {len(step19['self_check_items'])} чекбоксов")

# Сохраняем
with open("docs/examples/git_github_course_practical.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Файл сохранён!")
