"""
Скрипт миграции данных: blog.Newsletter → notifications.Subscription

Переносит все подписки из blog.Newsletter в централизованную
notifications.Subscription с type='blog'.
"""

import os
import sys

import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyland.settings")
django.setup()

from blog.models import Newsletter
from notifications.models import Subscription


def migrate_newsletter_to_subscriptions():
    """Миграция данных из Newsletter в Subscription."""

    print("=" * 70)
    print("🔄 МИГРАЦИЯ: blog.Newsletter → notifications.Subscription")
    print("=" * 70)

    # Статистика ДО миграции
    newsletter_count = Newsletter.objects.count()
    subscription_count = Subscription.objects.filter(subscription_type="blog").count()

    print("\n📊 Статистика ДО миграции:")
    print(f"   - blog.Newsletter: {newsletter_count} записей")
    print(f"   - notifications.Subscription (type='blog'): {subscription_count} записей")

    if newsletter_count == 0:
        print("\n✅ В blog.Newsletter нет данных для миграции.")
        return

    print(f"\n🚀 Начинаем миграцию {newsletter_count} подписок...")

    migrated = 0
    skipped = 0
    errors = 0

    for newsletter in Newsletter.objects.all():
        try:
            # Проверяем, есть ли уже такая подписка
            existing = Subscription.objects.filter(
                email=newsletter.email, subscription_type="blog"
            ).first()

            if existing:
                print(f"   ⏭️  Пропущено (уже существует): {newsletter.email}")
                skipped += 1
                continue

            # Создаем подписку
            Subscription.objects.create(
                user=newsletter.user,
                email=newsletter.email,
                subscription_type="blog",
                is_active=newsletter.is_active,
                preferences={"name": newsletter.name} if newsletter.name else {},
                created_at=newsletter.created_at,
            )

            migrated += 1
            print(f"   ✅ Мигрировано: {newsletter.email}")

        except Exception as e:
            errors += 1
            print(f"   ❌ Ошибка для {newsletter.email}: {e}")

    # Статистика ПОСЛЕ миграции
    subscription_count_after = Subscription.objects.filter(subscription_type="blog").count()

    print("\n" + "=" * 70)
    print("📊 Результаты миграции:")
    print("=" * 70)
    print(f"   ✅ Успешно мигрировано: {migrated}")
    print(f"   ⏭️  Пропущено (дубликаты): {skipped}")
    print(f"   ❌ Ошибок: {errors}")
    print(f"\n   📈 Subscription (type='blog') сейчас: {subscription_count_after} записей")

    if errors == 0 and migrated > 0:
        print("\n🎉 Миграция завершена успешно!")
        print("\n⚠️  ВАЖНО: Теперь можно удалить модель blog.Newsletter:")
        print("   1. Удалить Newsletter из blog/models.py")
        print("   2. Удалить NewsletterAdmin из blog/admin.py")
        print("   3. Создать миграцию: python manage.py makemigrations blog")
        print("   4. Применить: python manage.py migrate blog")
    elif errors > 0:
        print("\n⚠️  Миграция завершена с ошибками. Проверьте логи выше.")
    else:
        print("\n✅ Нечего мигрировать.")

    print("=" * 70)


if __name__ == "__main__":
    migrate_newsletter_to_subscriptions()
