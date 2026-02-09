# Generated manually on 2026-02-09 06:30
"""
Миграция для обновления существующих payment_method значений
из старых (cloudpayments, tbc_georgia) в новые (bog, tbc).
"""

from django.db import migrations


def update_payment_methods(apps, schema_editor):
    """
    Обновление существующих платежей:
    - cloudpayments -> bog
    - tbc_georgia -> tbc
    """
    Payment = apps.get_model("payments", "Payment")

    # Обновляем cloudpayments на bog
    cloudpayments_count = Payment.objects.filter(payment_method="cloudpayments").update(
        payment_method="bog"
    )

    # Обновляем tbc_georgia на tbc
    tbc_georgia_count = Payment.objects.filter(payment_method="tbc_georgia").update(
        payment_method="tbc"
    )

    print(f"Обновлено платежей:")
    print(f"  cloudpayments -> bog: {cloudpayments_count}")
    print(f"  tbc_georgia -> tbc: {tbc_georgia_count}")


def reverse_payment_methods(apps, schema_editor):
    """
    Откат изменений (на случай rollback миграции).
    """
    Payment = apps.get_model("payments", "Payment")

    # Откатываем bog на cloudpayments
    Payment.objects.filter(payment_method="bog").update(payment_method="cloudpayments")

    # Откатываем tbc на tbc_georgia
    Payment.objects.filter(payment_method="tbc").update(payment_method="tbc_georgia")


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_alter_payment_payment_method"),
    ]

    operations = [
        migrations.RunPython(update_payment_methods, reverse_payment_methods),
    ]
