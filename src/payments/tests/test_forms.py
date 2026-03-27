"""
Тесты форм payments.

Проверяет:
    - Валидацию CheckoutForm
    - Валидацию выбора валюты
    - Обязательное принятие условий
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from payments.forms import CheckoutForm
from payments.models import Payment


@pytest.mark.django_db
class TestCheckoutForm:
    """Тесты формы CheckoutForm."""

    def test_valid_form(self):
        """Тест валидной формы."""
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["payment_method"] == "paddle"
        assert form.cleaned_data["currency"] == "USD"

    def test_missing_payment_method(self):
        """Тест без выбора метода оплаты."""
        form_data = {
            "currency": "USD",
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()
        assert "payment_method" in form.errors

    def test_missing_currency(self):
        """Тест без выбора валюты."""
        form_data = {
            "payment_method": "paddle",
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()
        assert "currency" in form.errors

    def test_invalid_payment_method(self):
        """Тест с недопустимым методом оплаты."""
        form_data = {
            "payment_method": "invalid_method",
            "currency": "USD",
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()

    def test_invalid_currency(self):
        """Тест с недопустимой валютой."""
        form_data = {
            "payment_method": "paddle",
            "currency": "INVALID",
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()

    def test_terms_not_accepted(self):
        """Тест без принятия условий."""
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_all": False,
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()
        assert "accept_all" in form.errors

    def test_privacy_not_accepted(self):
        """Тест без принятия политики приватности."""
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            # Не принимаем условия
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()
        assert "accept_all" in form.errors

    def test_all_supported_currencies(self):
        """Тест всех поддерживаемых валют."""
        currencies = ["USD", "EUR", "RUB", "GEL"]

        for currency in currencies:
            form_data = {
                "payment_method": "paddle",
                "currency": currency,
                "accept_all": True,
            }

            form = CheckoutForm(data=form_data)

            assert form.is_valid(), f"Currency {currency} should be valid"
            assert form.cleaned_data["currency"] == currency

    def test_clean_method_validation(self):
        """Тест комплексной валидации через clean()."""
        # Test with missing payment_method and currency
        form_data = {
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert not form.is_valid()
        # Should have errors for required fields
        assert "payment_method" in form.errors or "currency" in form.errors

        # Test with all valid data
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_all": True,
        }

        form = CheckoutForm(data=form_data)

        assert form.is_valid()

        cleaned = form.clean()
        assert "payment_method" in cleaned
        assert "currency" in cleaned
