"""
Management Command - Обновление курсов валют.

Команда для ручного обновления и отображения актуальных курсов валют.
Использует CurrencyService для получения свежих данных из API.

Usage:
    python manage.py update_currency_rates
    python manage.py update_currency_rates --show
    python manage.py update_currency_rates --force

Автор: Pyland Team
Дата: 2026
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from payments.currency_service import get_currency_service


class Command(BaseCommand):
    """
    Django management команда для обновления курсов валют.

    Позволяет:
    - Показать текущие курсы
    - Принудительно обновить курсы
    - Очистить кэш и получить свежие данные
    """

    help = "Обновить и показать актуальные курсы валют для платежей"

    def add_arguments(self, parser):
        """
        Добавить аргументы командной строки.

        Args:
            parser: Парсер аргументов
        """
        parser.add_argument(
            "--show",
            action="store_true",
            help="Только показать текущие курсы без обновления",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Принудительно обновить курсы (очистить кэш)",
        )

    def handle(self, *args, **options):
        """
        Основная логика команды.

        Args:
            *args: Позиционные аргументы
            **options: Опции команды
        """
        currency_service = get_currency_service()

        show_only = options["show"]
        force_update = options["force"]

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("  CURRENCY RATES MANAGER - Менеджер курсов валют"))
        self.stdout.write(self.style.SUCCESS("=" * 60 + "\n"))

        if force_update and not show_only:
            self.stdout.write("🔄 Принудительное обновление курсов...")
            currency_service.invalidate_cache()
            self.stdout.write(self.style.WARNING("   Кэш очищен\n"))

        try:
            rates = currency_service.get_exchange_rates(base_currency="USD")

            self.stdout.write(
                self.style.SUCCESS("✅ Актуальные курсы валют (базовая валюта: USD):\n")
            )

            self._display_rates(rates)

            self.stdout.write("\n📊 Примеры конвертации (100 USD):\n")
            self._show_conversion_examples(currency_service)

            self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
            self.stdout.write(f"⏰ Время: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.stdout.write("💾 Курсы кэшируются на 1 час")
            self.stdout.write(self.style.SUCCESS("=" * 60 + "\n"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Ошибка при получении курсов: {e}\n"))
            return

    def _display_rates(self, rates: dict[str, Decimal]) -> None:
        """
        Отобразить курсы валют в таблице.

        Args:
            rates: Словарь с курсами валют
        """
        currencies = {
            "USD": ("💵", "Доллар США"),
            "EUR": ("💶", "Евро"),
            "RUB": ("₽", "Российский рубль"),
            "GEL": ("₾", "Грузинский лари"),
        }

        self.stdout.write("   " + "-" * 50)
        self.stdout.write("   | Валюта           | Курс к USD        | Символ |")
        self.stdout.write("   " + "-" * 50)

        for currency_code, rate in sorted(rates.items()):
            if currency_code in currencies:
                symbol, name = currencies[currency_code]
                rate_str = f"{rate:.4f}" if rate != Decimal("1.00") else "1.0000 (база)"
                formatted_line = f"   | {name:16} | {rate_str:17} | {symbol:6} |"

                if currency_code == "USD":
                    self.stdout.write(self.style.SUCCESS(formatted_line))
                else:
                    self.stdout.write(formatted_line)

        self.stdout.write("   " + "-" * 50)

    def _show_conversion_examples(self, currency_service) -> None:
        """
        Показать примеры конвертации валют.

        Args:
            currency_service: Экземпляр CurrencyService
        """
        base_amount = Decimal("100.00")
        conversions = [
            ("USD", "EUR"),
            ("USD", "RUB"),
            ("USD", "GEL"),
        ]

        for from_curr, to_curr in conversions:
            try:
                converted = currency_service.convert_currency(base_amount, from_curr, to_curr)
                self.stdout.write(f"   • {base_amount} {from_curr} = {converted:.2f} {to_curr}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️  Ошибка конвертации {from_curr}→{to_curr}: {e}")
                )
