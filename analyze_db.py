#!/usr/bin/env python
"""
Скрипт для анализа размера базы данных и прогнозирования роста.
"""

import os
import sys

import django
from django.apps import apps

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyland.settings")
django.setup()


def analyze_database():
    """Анализ текущего состояния базы данных."""
    print("=" * 100)
    print("АНАЛИЗ БАЗЫ ДАННЫХ PYLAND")
    print("=" * 100)
    print()

    # Получаем все модели
    models_data = []
    total_records = 0

    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        # Пропускаем служебные модели Django
        if app_label in ["admin", "auth", "contenttypes", "sessions", "socialaccount", "account"]:
            continue

        try:
            count = model.objects.count()
            table_name = model._meta.db_table

            models_data.append(
                {"app": app_label, "model": model_name, "count": count, "table": table_name}
            )
            total_records += count
        except Exception as e:
            # Пропускаем модели, к которым нет доступа
            print(f"Skipping {app_label}.{model_name}: {e}", file=sys.stderr)

    # Сортируем по количеству записей
    models_data.sort(key=lambda x: x["count"], reverse=True)

    print(f"{'Модель':<40} | {'Записей':>8} | {'Таблица':<40}")
    print("-" * 100)

    for m in models_data:
        model_full = f"{m['app']}.{m['model']}"
        print(f"{model_full:<40} | {m['count']:>8} | {m['table']:<40}")

    print("-" * 100)
    print(f"{'ИТОГО ЗАПИСЕЙ':<40} | {total_records:>8}")
    print()

    return models_data, total_records


def estimate_growth():
    """Оценка роста базы данных после рекламы."""
    print()
    print("=" * 100)
    print("ПРОГНОЗ РОСТА ПОСЛЕ ПЕРВОЙ РЕКЛАМНОЙ КАМПАНИИ")
    print("=" * 100)
    print()

    # Средние размеры записей (в байтах, реальные оценки с учетом индексов)
    record_sizes = {
        "User": 500,  # Пользователь с email, паролем (хэш), профилем
        "Student": 1000,  # Расширенный профиль студента с аватаром (путь), телефоном, настройками
        "Course": 3000,  # Курс с описанием, изображением (путь), метаданными
        "Lesson": 2000,  # Урок с контентом, описанием
        "Step": 1500,  # Шаг урока с контентом
        "LessonSubmission": 5000,  # Отправка задания с кодом, файлами (пути), комментариями
        "Article": 8000,  # Статья блога с контентом, изображениями (пути)
        "Comment": 500,  # Комментарий
        "Reaction": 100,  # Реакция (like, love)
        "Payment": 800,  # Платеж с данными транзакции
        "Certificate": 2000,  # Сертификат с данными
        "Review": 1000,  # Отзыв ревьюера
        "Notification": 300,  # Уведомление
        "SystemLog": 400,  # Системный лог
    }

    # Сценарии после первой рекламы
    scenarios = {
        "Консервативный (500 регистраций)": {
            "new_users": 500,
            "conversion_to_paid": 0.05,  # 5% купят курс
            "avg_submissions_per_student": 10,
            "avg_comments_per_user": 5,
            "avg_reactions_per_user": 20,
        },
        "Средний (2000 регистраций)": {
            "new_users": 2000,
            "conversion_to_paid": 0.08,  # 8% купят курс
            "avg_submissions_per_student": 15,
            "avg_comments_per_user": 8,
            "avg_reactions_per_user": 30,
        },
        "Оптимистичный (5000 регистраций)": {
            "new_users": 5000,
            "conversion_to_paid": 0.10,  # 10% купят курс
            "avg_submissions_per_student": 20,
            "avg_comments_per_user": 12,
            "avg_reactions_per_user": 40,
        },
    }

    for scenario_name, params in scenarios.items():
        print(f"\n📊 {scenario_name}")
        print("-" * 100)

        new_users = params["new_users"]
        paid_students = int(new_users * params["conversion_to_paid"])

        # Расчет новых записей
        new_records = {
            "Users": new_users,
            "Students": new_users,
            "Payments": paid_students,
            "Certificates": paid_students,
            "LessonSubmissions": paid_students * params["avg_submissions_per_student"],
            "Comments": new_users * params["avg_comments_per_user"],
            "Reactions": new_users * params["avg_reactions_per_user"],
            "Notifications": new_users * 50,  # В среднем 50 уведомлений на пользователя
            "SystemLogs": new_users * 100,  # Логи действий
        }

        # Расчет размера
        total_size_bytes = 0
        total_size_bytes += new_records["Users"] * record_sizes["User"]
        total_size_bytes += new_records["Students"] * record_sizes["Student"]
        total_size_bytes += new_records["Payments"] * record_sizes["Payment"]
        total_size_bytes += new_records["Certificates"] * record_sizes["Certificate"]
        total_size_bytes += new_records["LessonSubmissions"] * record_sizes["LessonSubmission"]
        total_size_bytes += new_records["Comments"] * record_sizes["Comment"]
        total_size_bytes += new_records["Reactions"] * record_sizes["Reaction"]
        total_size_bytes += new_records["Notifications"] * record_sizes["Notification"]
        total_size_bytes += new_records["SystemLogs"] * record_sizes["SystemLog"]

        # Добавляем накладные расходы (индексы, foreign keys, версии PostgreSQL)
        overhead = 1.5  # 50% накладных расходов
        total_size_bytes *= overhead

        # Конвертируем в читаемый формат
        size_mb = total_size_bytes / (1024 * 1024)
        size_gb = size_mb / 1024

        print(f"  👥 Новых пользователей: {new_users:,}")
        print(
            f"  💰 Платящих студентов: {paid_students:,} ({params['conversion_to_paid'] * 100:.0f}%)"
        )
        print(f"  📝 Отправок заданий: {new_records['LessonSubmissions']:,}")
        print(f"  💬 Комментариев: {new_records['Comments']:,}")
        print(f"  ❤️  Реакций: {new_records['Reactions']:,}")
        print(f"  🔔 Уведомлений: {new_records['Notifications']:,}")
        print()
        print(f"  📦 Ожидаемый размер БД: {size_mb:.1f} MB ({size_gb:.2f} GB)")
        print(f"  💾 С учетом роста контента (x2): {size_gb * 2:.2f} GB")

    print()
    print("=" * 100)
    print("РЕКОМЕНДАЦИИ ПО ХРАНЕНИЮ")
    print("=" * 100)
    print()
    print("📌 Базовая оценка для 30 GB:")
    print()
    print("  ✅ Консервативный сценарий (500 юзеров): ~0.5-1 GB")
    print("     → 30 GB хватит на ~15,000-30,000 пользователей")
    print()
    print("  ✅ Средний сценарий (2000 юзеров): ~2-4 GB")
    print("     → 30 GB хватит на ~15,000-30,000 пользователей")
    print()
    print("  ⚠️  Оптимистичный сценарий (5000 юзеров): ~5-10 GB")
    print("     → 30 GB хватит на ~15,000-30,000 пользователей")
    print()
    print("🎯 ВЫВОД:")
    print("  • 30 GB вполне достаточно для старта и первых месяцев работы")
    print("  • При активном росте (5000+ юзеров/месяц) можно выйти за 30 GB через 6-12 месяцев")
    print("  • Критичные факторы роста:")
    print("    - Отправки заданий с кодом (5-50 KB каждая)")
    print("    - Загружаемые файлы студентов (хранятся отдельно в media)")
    print("    - Логи системы (можно чистить старые)")
    print()
    print("💡 РЕКОМЕНДАЦИИ:")
    print("  1. Настройте автоочистку старых логов (старше 3-6 месяцев)")
    print("  2. Архивируйте неактивных пользователей (>1 года без активности)")
    print("  3. Мониторьте размер БД через pgAdmin или встроенные метрики PostgreSQL")
    print("  4. Держите media-файлы отдельно (S3, MinIO)")
    print("  5. При достижении 20 GB начинайте планировать масштабирование")
    print()


if __name__ == "__main__":
    try:
        models_data, total = analyze_database()
        estimate_growth()
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback

        traceback.print_exc()
