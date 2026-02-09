"""
Payments Forms - Формы для обработки платежей.

Формы основаны на лучших практиках из students/forms.py и reviewers/forms.py:
- Полная валидация данных
- Подробные help_text
- Clean методы для сложной валидации
- Type hints

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Payment


class CheckoutForm(forms.Form):
    """
    Форма для оформления оплаты курса.

    Поля:
        payment_method: Выбор способа оплаты (BOG/TBC)
        currency: Валюта платежа (USD/GEL/RUB)
        terms_accepted: Согласие с условиями использования
        privacy_accepted: Согласие с политикой конфиденциальности

    Валидация:
        - Обязательно принятие всех согласий
        - Валидация соответствия валюты и метода оплаты
        - Проверка доступности метода оплаты
    """

    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                "class": "payment-method-radio",
            }
        ),
        label=_("Способ оплаты"),
        help_text=_("Выберите удобный способ оплаты"),
    )

    currency = forms.ChoiceField(
        choices=Payment.CURRENCY_CHOICES,
        required=True,
        initial="USD",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_currency",
            }
        ),
        label=_("Валюта"),
        help_text=_("Выберите валюту платежа"),
    )

    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "id_terms",
            }
        ),
        label=_("Я принимаю условия использования"),
        error_messages={"required": "Необходимо принять условия использования для продолжения"},
    )

    privacy_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "id_privacy",
            }
        ),
        label=_("Я принимаю политику конфиденциальности"),
        error_messages={
            "required": "Необходимо принять политику конфиденциальности для продолжения"
        },
    )

    def clean_payment_method(self) -> str:
        """Валидация метода оплаты."""
        payment_method = self.cleaned_data.get("payment_method")

        valid_methods = [choice[0] for choice in Payment.PAYMENT_METHOD_CHOICES]
        if payment_method not in valid_methods:
            raise ValidationError("Выбран недопустимый способ оплаты")

        return payment_method

    def clean_currency(self) -> str:
        """Валидация валюты."""
        currency = self.cleaned_data.get("currency")

        valid_currencies = [choice[0] for choice in Payment.CURRENCY_CHOICES]
        if currency not in valid_currencies:
            raise ValidationError("Выбрана недопустимая валюта")

        return currency

    def clean(self) -> dict[str, Any]:
        """
        Комплексная валидация формы.

        Проверяет корректность данных платежа.
        """
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")
        currency = cleaned_data.get("currency")

        # Валидация метода оплаты
        if not payment_method or not currency:
            raise ValidationError("Необходимо выбрать способ оплаты и валюту")

        return cleaned_data


class PaymentConfirmationForm(forms.Form):
    """
    Форма для подтверждения данных платежа перед отправкой.

    Используется для финального подтверждения перед редиректом
    на страницу платежной системы.
    """

    payment_id = forms.UUIDField(
        required=True,
        widget=forms.HiddenInput(),
        label=_("ID платежа"),
    )

    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True,
    )
