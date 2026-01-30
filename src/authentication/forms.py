"""
Auth Forms - Django формы для регистрации и аутентификации.

Этот модуль содержит формы для работы с аутентификацией:
    - UserRegisterForm: Регистрация нового пользователя с валидацией email, пароля, телефона
    - UserLoginForm: Аутентификация через email и пароль
    - PasswordResetForm: Запрос сброса пароля по email
    - SetPasswordForm: Установка нового пароля

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Any

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()
logger = logging.getLogger(__name__)

# ============================================================================
# ФОРМЫ АУТЕНТИФИКАЦИИ
# ============================================================================


class UserRegisterForm(forms.ModelForm):
    """
    Форма регистрации нового пользователя с полной валидацией всех полей.

    Создает нового пользователя с проверкой уникальности email, сложности пароля,
    формата телефона и согласия с условиями использования.

    Fields:
        first_name: Имя пользователя (макс 30 символов)
        phone_number: Номер телефона в международном формате (+7...)
        email: Адрес электронной почты (должен быть уникальным)
        password: Пароль (мин 8 символов, буквы + цифры)
        confirm_password: Подтверждение пароля (должно совпадать)
        agree_to_terms: Согласие с условиями использования (обязательно)

    Validation:
        - email: Проверяется уникальность в базе данных
        - password: Мин 8 символов, буквы + цифры, не содержит email/телефон
        - confirm_password: Должен совпадать с password
        - phone_number: Должен начинаться с +, макс 15 символов
        - agree_to_terms: Должен быть True

    Example:
        >>> form = UserRegisterForm({
        ...     'email': 'user@example.com',
        ...     'password': 'SecurePass123',
        ...     'confirm_password': 'SecurePass123',
        ...     'first_name': 'Ivan',
        ...     'phone_number': '+79991234567',
        ...     'agree_to_terms': True
        ... })
        >>> if form.is_valid():
        ...     user = form.save()
    """

    first_name: forms.CharField = forms.CharField(
        label=_("Имя"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Введите ваше имя")}
        ),
        max_length=30,
        error_messages={
            "required": _("Имя обязательно для заполнения."),
            "max_length": _("Имя не может превышать 30 символов."),
        },
    )
    phone_number = PhoneNumberField(
        label=_("Телефон"),
        region="RU",
        widget=forms.TextInput(
            attrs={
                "class": "phone-number-input",
                "type": "tel",
                "placeholder": _("Введите номер телефона"),
                "autocomplete": "tel",
            }
        ),
        error_messages={
            "required": _("Телефон обязателен для заполнения."),
            "invalid": _("Введите корректный номер телефона в международном формате."),
        },
    )
    email: forms.EmailField = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": _("Введите ваш Email")}
        ),
        error_messages={
            "required": _("Email обязателен для заполнения."),
            "invalid": _("Введите корректный email адрес."),
        },
    )
    password: forms.CharField = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Введите пароль")}
        ),
        error_messages={"required": _("Пароль обязателен для заполнения.")},
    )
    confirm_password: forms.CharField = forms.CharField(
        label=_("Подтвердите пароль"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Подтвердите пароль")}
        ),
        error_messages={"required": _("Подтверждение пароля обязательно.")},
    )

    agree_to_terms: forms.BooleanField = forms.BooleanField(
        label=_("Я согласен с условиями использования и политикой конфиденциальности"),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=True,
        error_messages={
            "required": _(
                "Необходимо согласиться с условиями использования и политикой конфиденциальности."
            )
        },
    )

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "phone_number"]

    def clean_email(self) -> str:
        """
        Проверяет уникальность email в базе данных.

        Returns:
            Валидированный email адрес

        Raises:
            ValidationError: Если email уже используется другим пользователем
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            logger.warning(f"Попытка регистрации с существующим email: {email}")
            raise ValidationError(_("Этот адрес электронной почты уже используется."))
        return email

    def clean_password(self) -> str:
        """
        Проверяет сложность пароля через Django валидаторы.

        Returns:
            Валидированный пароль

        Raises:
            ValidationError: Если пароль не соответствует требованиям Django
        """
        password = self.cleaned_data.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                raise ValidationError(error.messages) from error
        return password

    def clean_confirm_password(self) -> str:
        """
        Проверяет совпадение пароля и подтверждения.

        Returns:
            Подтвержденный пароль

        Raises:
            ValidationError: Если пароли не совпадают
        """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError(_("Пароли не совпадают."))
        return confirm_password

    def clean_agree_to_terms(self) -> bool:
        """
        Проверяет согласие с условиями использования.

        Returns:
            True если пользователь согласился

        Raises:
            ValidationError: Если чекбокс не отмечен
        """
        agree_to_terms = self.cleaned_data.get("agree_to_terms")
        if not agree_to_terms:
            raise ValidationError(
                _(
                    "Необходимо согласиться с условиями использования и политикой конфиденциальности."
                )
            )
        return agree_to_terms

    def clean(self) -> dict[str, Any]:
        """
        Выполняет общую валидацию взаимодействия полей.

        Проверяет что пароль не содержит email или номер телефона пользователя
        для повышения безопасности.

        Returns:
            Dict с валидированными данными формы
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        phone_number = cleaned_data.get("phone_number")
        email = cleaned_data.get("email")

        if password:
            # Конвертируем PhoneNumber в строку для проверки
            if phone_number:
                phone_str = str(phone_number)
                if phone_str in password:
                    self.add_error("password", _("Пароль не должен содержать ваш номер телефона."))
            if email and email in password:
                self.add_error(
                    "password",
                    _("Пароль не должен содержать ваш адрес электронной почты."),
                )
        return cleaned_data


class UserLoginForm(forms.Form):
    """
    Форма аутентификации пользователя через email и пароль.

    Проверяет учетные данные пользователя через Django authenticate().
    Используется на странице входа в систему.

    Fields:
        email: Email адрес пользователя
        password: Пароль пользователя

    Validation:
        - email и password проверяются через authenticate()
        - Если пользователь не найден или пароль неверный - общая ошибка формы

    Example:
        >>> form = UserLoginForm({
        ...     'email': 'user@example.com',
        ...     'password': 'SecurePass123'
        ... })
        >>> if form.is_valid():
        ...     user = authenticate(**form.cleaned_data)
    """

    email: forms.EmailField = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": _("Email")}),
        error_messages={
            "required": _("Пожалуйста, введите ваш email."),
            "invalid": _("Пожалуйста, введите корректный email адрес."),
        },
    )
    password: forms.CharField = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={"class": "password", "placeholder": _("Пароль")}),
        error_messages={"required": _("Пожалуйста, введите ваш пароль.")},
    )
    remember_me: forms.BooleanField = forms.BooleanField(
        label=_("Запомнить меня"),
        required=False,
        initial=False,
    )

    def clean(self) -> dict[str, Any]:
        """
        Проверяет email и пароль через Django authenticate().

        Returns:
            dict с валидированными данными (email, password)

        Raises:
            ValidationError: Если email не найден или пароль неверный
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                logger.warning(f"Неудачная попытка входа с email: {email}")
                self.add_error(None, _("Неверный email или пароль."))
        return cleaned_data


class PasswordResetForm(forms.Form):
    """
    Форма запроса сброса пароля по email адресу.

    Проверяет существование пользователя с указанным email и отправляет
    письмо со ссылкой для сброса пароля.

    Fields:
        email: Email адрес пользователя для сброса пароля

    Validation:
        - Проверяется существование пользователя с данным email в БД

    Example:
        >>> form = PasswordResetForm({'email': 'user@example.com'})
        >>> if form.is_valid():
        ...     user = User.objects.get(email=form.cleaned_data['email'])
        ...     # Отправка письма со ссылкой сброса пароля
    """

    email: forms.EmailField = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": _("Введите ваш email")}
        ),
        error_messages={
            "required": _("Пожалуйста, введите ваш email."),
            "invalid": _("Пожалуйста, введите корректный email адрес."),
        },
    )

    def clean_email(self) -> str:
        """
        Проверяет существование пользователя с данным email.

        Returns:
            Валидированный email адрес

        Raises:
            ValidationError: Если пользователь с таким email не найден
        """
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_("Пользователь с таким email не найден."))
        return email


class SetPasswordForm(DjangoSetPasswordForm):
    """
    Кастомная форма установки нового пароля с переведенными сообщениями об ошибках.

    Переопределяет стандартную Django форму SetPasswordForm для корректного
    отображения ошибок валидации пароля на русском языке.

    Fields:
        new_password1: Новый пароль
        new_password2: Подтверждение нового пароля
    """

    new_password1 = forms.CharField(
        label=_("Новый пароль"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Введите новый пароль"),
                "autocomplete": "new-password",
            }
        ),
        strip=False,
        help_text=_(
            "Пароль должен содержать минимум 8 символов и не может состоять только из цифр."
        ),
    )
    new_password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Подтвердите новый пароль"),
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_new_password2(self):
        """
        Валидирует совпадение паролей и применяет все валидаторы паролей Django.

        Returns:
            Валидированный пароль

        Raises:
            ValidationError: Если пароли не совпадают или не проходят валидацию
        """
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    _("Два введённых пароля не совпадают."),
                    code="password_mismatch",
                )

        # Применяем стандартные валидаторы Django с переводом ошибок
        if password2:
            try:
                validate_password(password2, self.user)
            except ValidationError as error:
                # Переводим все ошибки валидации на русский
                translated_errors = []
                for err in error.error_list:
                    error_message = str(err.message)

                    # Переводим стандартные сообщения Django
                    if "too short" in error_message.lower() or "at least" in error_message.lower():
                        translated_errors.append(
                            ValidationError(
                                _(
                                    "Пароль слишком короткий. Он должен содержать минимум 8 символов."
                                )
                            )
                        )
                    elif "too common" in error_message.lower():
                        translated_errors.append(
                            ValidationError(_("Введённый пароль слишком широко распространён."))
                        )
                    elif "entirely numeric" in error_message.lower():
                        translated_errors.append(
                            ValidationError(_("Введённый пароль состоит только из цифр."))
                        )
                    elif "too similar" in error_message.lower():
                        translated_errors.append(
                            ValidationError(
                                _(
                                    "Введённый пароль слишком похож на другую вашу личную информацию."
                                )
                            )
                        )
                    else:
                        # Если ошибка уже переведена или неизвестна, оставляем как есть
                        translated_errors.append(err)

                raise ValidationError(translated_errors) from err

        return password2
