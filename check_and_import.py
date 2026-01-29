#!/usr/bin/env python
"""Скрипт для проверки и импорта курса с чекбоксами"""

import os
import sys

import django

# Настройка Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyland.settings")
django.setup()

from django.core.management import call_command

from courses.models import Course

print("=" * 60)
print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ")
print("=" * 60)

# Проверяем текущие курсы
courses = Course.objects.all()
print(f"\n📚 Курсов в базе: {courses.count()}")
for course in courses:
    print(f"  - {course.slug}: {course.name}")

# Удаляем git-github курсы
git_courses = Course.objects.filter(slug__icontains="git")
if git_courses.exists():
    print(f"\n🗑️  Удаление {git_courses.count()} курсов Git...")
    git_courses.delete()
    print("✅ Удалено")

print("\n" + "=" * 60)
print("📥 ИМПОРТ КУРСА")
print("=" * 60)

# Импортируем курс
course_path = os.path.join(
    os.path.dirname(__file__), "docs/examples/git_github_course_practical.json"
)

print(f"\n📁 Путь к файлу: {course_path}")
print(f"📄 Файл существует: {os.path.exists(course_path)}")

if os.path.exists(course_path):
    print("\n⏳ Импорт...")
    call_command("import_course", course_path)

    print("\n" + "=" * 60)
    print("✅ ПРОВЕРКА РЕЗУЛЬТАТА")
    print("=" * 60)

    # Проверяем импортированный курс
    course = Course.objects.filter(slug="git-github").first()
    if course:
        print(f"\n✅ Курс найден: {course.name}")
        print(f"   ID: {course.id}")
        print(f"   Уроков: {course.lessons.count()}")

        # Проверяем первый урок
        lesson1 = course.lessons.first()
        if lesson1:
            print(f"\n📚 Урок 1: {lesson1.name}")
            print(f"   Шагов: {lesson1.steps.count()}")

            # Проверяем шаг 2 (должны быть чекбоксы)
            step2 = lesson1.steps.filter(step_number=2).first()
            if step2:
                print(f"\n🔹 Шаг 2: {step2.name}")
                print(f"   self_check_items: {step2.self_check_items}")

                if step2.self_check_items:
                    print(f"   ✅ Чекбоксов: {len(step2.self_check_items)}")
                    for i, item in enumerate(step2.self_check_items, 1):
                        print(f"      {i}. {item}")
                else:
                    print("   ⚠️  self_check_items пустой или None")

                # Проверяем troubleshooting_help
                if step2.troubleshooting_help:
                    print("\n💡 troubleshooting_help:")
                    print(f"   {step2.troubleshooting_help[:100]}...")
                else:
                    print("\n   ℹ️  troubleshooting_help пустой")
    else:
        print("❌ Курс не найден после импорта!")
else:
    print(f"❌ Файл не найден: {course_path}")

print("\n" + "=" * 60)
print("✅ ГОТОВО")
print("=" * 60)
