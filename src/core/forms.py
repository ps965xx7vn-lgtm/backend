"""
Core Forms Module

Формы для основных функций приложения core:
- FeedbackForm: форма обратной связи с валидацией
- SubscriptionForm: форма подписки на email рассылку

Все формы используют Django forms с кастомными валидаторами
и i18n поддержкой через gettext_lazy.
"""

import logging
import re

import phonenumbers
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumbers import NumberParseException

logger = logging.getLogger(__name__)


class FeedbackForm(forms.Form):
    """
    Форма обратной связи для страниц контактов и главной.

    Поля:
        first_name: Имя отправителя (макс 100 символов, без цифр)
        phone_number: Номер телефона в международном формате (+1234567890)
        email: Email адрес с валидацией формата
        message: Текст сообщения (обязательное, textarea)
        agree_terms: Согласие с условиями использования (checkbox)

    Валидация:
        - Имя не должно содержать цифры
        - Телефон должен начинаться с + и содержать 9-15 цифр
        - Email должен соответствовать стандартному формату
        - Обязательно согласие с условиями

    Example:
        >>> form = FeedbackForm(request.POST)
        >>> if form.is_valid():
        >>>     name = form.cleaned_data['first_name']
        >>>     Feedback.objects.create(**form.cleaned_data)
    """

    first_name = forms.CharField(
        label=_("Имя"),
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Имя")}),
        error_messages={
            "required": _("Имя обязательно для заполнения."),
            "max_length": _("Имя не может превышать 100 символов."),
        },
    )

    phone_number = forms.CharField(
        label=_("Номер телефона"),
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Номер телефона")}),
        error_messages={
            "required": _("Номер телефона обязателен для заполнения."),
            "max_length": _("Номер телефона не может превышать 20 символов."),
        },
    )

    email = forms.EmailField(
        label=_("Email адрес"),
        max_length=100,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Email адрес")}),
        error_messages={
            "required": _("Email обязателен для заполнения."),
            "invalid": _("Введите корректный email адрес."),
        },
    )

    topic = forms.ChoiceField(
        label=_("Тема обращения"),
        choices=[
            ("", _("Выберите тему")),
            ("courses", _("Вопросы о курсах")),
            ("career", _("Карьерная консультация")),
            ("technical", _("Техническая поддержка")),
            ("partnership", _("Сотрудничество")),
            ("other", _("Другое")),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    message = forms.CharField(
        label=_("Напишите свое сообщение"),
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": _("Напишите свое сообщение"), "rows": 10}
        ),
        error_messages={"required": _("Сообщение обязательно для заполнения.")},
    )

    agree_terms = forms.BooleanField(
        label=_("Я согласен с Условиями обслуживания и Политикой конфиденциальности"),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        error_messages={
            "required": _(
                "Вы должны согласиться с Условиями обслуживания и Политикой конфиденциальности."
            )
        },
    )

    def clean_phone_number(self) -> str:
        """
        Валидация номера телефона с использованием библиотеки phonenumbers.

        Проверяет что номер телефона является валидным для любой страны.
        Поддерживает различные форматы: +7 (999) 123-45-67, +79991234567, и т.д.

        Returns:
            str: Валидный номер телефона в международном формате

        Raises:
            ValidationError: Если номер не прошел валидацию

        Example:
            >>> form.cleaned_data['phone_number'] = '+7 (999) 123-45-67'  # valid
            >>> form.cleaned_data['phone_number'] = '+79991234567'  # valid
            >>> form.cleaned_data['phone_number'] = '+1 (555) 123-4567'  # valid
        """
        phone_number = self.cleaned_data.get("phone_number")

        try:
            # Парсим номер телефона
            parsed_number = phonenumbers.parse(phone_number, None)

            # Проверяем что номер валидный
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(_("Введите корректный номер телефона."))

            # Проверяем что это возможный номер для данного региона
            if not phonenumbers.is_possible_number(parsed_number):
                raise ValidationError(
                    _("Номер телефона не соответствует формату выбранной страны.")
                )

            # Возвращаем номер в международном формате E164
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        except NumberParseException:
            raise ValidationError(
                _(
                    "Неверный формат номера телефона. Используйте международный формат, например: +7 999 123 45 67"
                )
            )

    def clean_email(self) -> str:
        """
        Дополнительная валидация email адреса.

        Проверяет email на соответствие стандартному формату
        с использованием регулярного выражения.

        Returns:
            str: Валидный email адрес

        Raises:
            ValidationError: Если email некорректный
        """
        email = self.cleaned_data.get("email")
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            raise ValidationError(_("Введите корректный email адрес."))
        return email

    def clean_first_name(self) -> str:
        """
        Валидация имени.

        Проверяет что имя не содержит цифр.

        Returns:
            str: Валидированное имя

        Raises:
            ValidationError: Если имя содержит цифры
        """
        name = self.cleaned_data.get("first_name")
        if any(char.isdigit() for char in name):
            logger.warning(f"Имя содержит цифры в форме обратной связи: {name}")
            raise ValidationError(_("Имя не должно содержать цифры."))
        return name


class SubscriptionForm(forms.Form):
    """
    Форма подписки на email рассылку.

    Простая форма с одним полем email для подписки на новости
    и обновления платформы. Используется в футере и других местах сайта.

    Поля:
        email: Email адрес для подписки

    Example:
        >>> form = SubscriptionForm(request.POST)
        >>> if form.is_valid():
        >>>     Subscription.objects.get_or_create(email=form.cleaned_data['email'])
    """

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите Email"}),
        error_messages={"required": "Введите Email"},
    )
