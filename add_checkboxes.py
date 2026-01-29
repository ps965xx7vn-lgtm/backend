#!/usr/bin/env python
"""Скрипт для добавления self_check_items во все шаги, где их нет"""

import json
import os

# Стандартные чекбоксы для разных типов шагов
default_checkboxes = {
    "knowledge": ["Я понял материал этого шага"],
    "git_config": ["Команда выполнена без ошибок"],
    "file_creation": ["Файл создан", "Изменения сохранены"],
    "git_commit": ["Коммит создан успешно"],
    "visual_check": ["Вижу изменения на странице"],
    "github_action": ["Действие выполнено на GitHub"],
}


def get_checkboxes_for_step(step_name, existing_items):
    """Определяет какие чекбоксы нужны для шага"""
    if existing_items:
        return existing_items

    name_lower = step_name.lower()

    # Определяем тип шага по ключевым словам
    if "коммит" in name_lower:
        return default_checkboxes["git_commit"]
    elif "добав" in name_lower or "созда" in name_lower:
        if "html" in name_lower or "стил" in name_lower or "css" in name_lower:
            return default_checkboxes["visual_check"]
        return default_checkboxes["file_creation"]
    elif "настро" in name_lower or "config" in name_lower:
        return default_checkboxes["git_config"]
    elif "github" in name_lower or "репозитор" in name_lower:
        return default_checkboxes["github_action"]
    elif "истор" in name_lower or "знаком" in name_lower:
        return default_checkboxes["knowledge"]
    else:
        # Универсальный чекбокс
        return ["Шаг выполнен"]


def add_checkboxes_to_course():
    file_path = "docs/examples/git_github_course_practical.json"

    print(f"📂 Загружаю: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        course = json.load(f)

    added_count = 0
    updated_count = 0

    # Обрабатываем русскую версию
    if "ru" in course and "lessons" in course["ru"]:
        for lesson_idx, lesson in enumerate(course["ru"]["lessons"], 1):
            print(f"\n📚 Урок {lesson_idx}: {lesson['name']}")
            for step_idx, step in enumerate(lesson["steps"], 1):
                step_name = step.get("name", "")
                existing = step.get("self_check_items")

                if not existing or len(existing) == 0:
                    # Добавляем новые чекбоксы
                    checkboxes = get_checkboxes_for_step(step_name, None)
                    step["self_check_items"] = checkboxes
                    added_count += 1
                    print(f"   ✅ Шаг {step_idx}: {step_name}")
                    print(f"      Добавлено {len(checkboxes)} чекбокс(ов)")
                elif len(existing) < 2 and "Шаг выполнен" not in existing[0]:
                    # Оставляем существующие, но добавляем общий если нужно
                    print(
                        f"   ✓ Шаг {step_idx}: {step_name} - уже есть {len(existing)} чекбокс(ов)"
                    )
                    updated_count += 1

    print("\n💾 Сохраняю изменения...")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(course, f, ensure_ascii=False, indent=2)

    print("\n✅ Готово!")
    print(f"   Добавлено чекбоксов: {added_count} шагов")
    print(f"   Уже было: {updated_count} шагов")
    return added_count


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    add_checkboxes_to_course()
