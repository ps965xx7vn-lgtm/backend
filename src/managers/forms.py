"""
Manager Forms Module - Django формы для административной панели менеджеров.

Этот модуль предоставляет формы для работы с обратной связью
и фильтрации данных в интерфейсе менеджера.

Формы:
    - FeedbackFilterForm: Форма фильтрации списка обращений с расширенными опциями

Особенности:
    - Кастомная валидация дат
    - Поддержка фильтрации по теме обращения
    - Удобные виджеты для дат
    - Type hints для всех методов

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django import forms

from .models import Feedback

# ============================================================================
# FEEDBACK FORM - Форма обратной связи
# ============================================================================


class FeedbackForm(forms.ModelForm):
    """
    Форма для создания и редактирования обратной связи.

    Предоставляет интерфейс для приема и обработки обращений пользователей.
    Включает валидацию всех полей и кастомные виджеты для удобства.

    Поля:
        - name: Имя пользователя (обязательное, мин 2 символа)
        - email: Email адрес (обязательное, валидация формата)
        - phone_number: Телефон (необязательное, должно начинаться с +)
        - subject: Тема обращения (обязательное)
        - message: Текст сообщения (обязательное, мин 10 символов)

    Виджеты:
        - name: TextInput с placeholder
        - email: EmailInput с placeholder
        - phone_number: TextInput с placeholder
        - subject: TextInput с placeholder
        - message: Textarea с rows=5

    Example:
        >>> # В view функции
        >>> if request.method == 'POST':
        >>>     form = FeedbackForm(request.POST)
        >>>     if form.is_valid():
        >>>         feedback = form.save()
        >>>         return redirect('success')
        >>> else:
        >>>     form = FeedbackForm()

        >>> # Валидация
        >>> form = FeedbackForm(data={
        >>>     'name': 'Иван',
        >>>     'email': 'ivan@example.com',
        >>>     'phone_number': '+79001234567',
        >>>     'subject': 'Вопрос',
        >>>     'message': 'Это тестовое сообщение'
        >>> })
        >>> if form.is_valid():
        >>>     feedback = form.save()
    """

    class Meta:
        model = Feedback
        fields = ["first_name", "email", "phone_number", "message", "admin_notes"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше имя"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "email@example.com"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+79001234567"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Ваше сообщение...",
                }
            ),
            "admin_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Заметки администратора...",
                }
            ),
        }

    def clean_phone_number(self) -> str | None:
        """
        Валидирует формат номера телефона.

        Проверяет, что номер начинается с символа '+'.
        Допускается пустое значение (поле необязательное).

        Returns:
            str | None: Валидированный номер телефона или None

        Raises:
            forms.ValidationError: Если номер не начинается с '+'

        Example:
            >>> form = FeedbackForm(data={'phone_number': '79001234567'})
            >>> form.is_valid()  # False - должно начинаться с +
            >>> form = FeedbackForm(data={'phone_number': '+79001234567'})
            >>> form.is_valid()  # True
        """
        phone = self.cleaned_data.get("phone_number")
        if phone and not phone.startswith("+"):
            raise forms.ValidationError("Номер телефона должен начинаться с '+'")
        return phone

    def clean_message(self) -> str:
        """
        Валидирует длину сообщения.

        Проверяет, что сообщение содержит минимум 10 символов.

        Returns:
            str: Валидированное сообщение

        Raises:
            forms.ValidationError: Если сообщение короче 10 символов

        Example:
            >>> form = FeedbackForm(data={'message': 'Привет'})
            >>> form.is_valid()  # False - меньше 10 символов
            >>> form = FeedbackForm(data={'message': 'Здравствуйте, у меня вопрос'})
            >>> form.is_valid()  # True
        """
        message = self.cleaned_data.get("message")
        if message and len(message) < 10:
            raise forms.ValidationError("Сообщение должно содержать минимум 10 символов")
        return message


# ============================================================================
# FILTER FORM - Форма фильтрации обратной связи
# ============================================================================


class FeedbackFilterForm(forms.Form):
    """
    Форма для фильтрации списка обращений обратной связи.

    Позволяет менеджерам фильтровать обращения по тексту, датам,
    статусу обработки и теме обращения.

    Поля:
        - search: Текстовый поиск по имени, email, телефону, сообщению
        - date_from: Дата начала периода (необязательное)
        - date_to: Дата окончания периода (необязательное)
        - is_processed: Статус обработки (необязательное)
        - topic: Тема обращения (необязательное)

    Example:
        >>> filter_form = FeedbackFilterForm(request.GET)
        >>> if filter_form.is_valid():
        >>>     feedbacks = Feedback.objects.all()
        >>>     search = filter_form.cleaned_data.get('search')
        >>>     if search:
        >>>         feedbacks = feedbacks.filter(
        >>>             Q(first_name__icontains=search) |
        >>>             Q(email__icontains=search)
        >>>         )
    """

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по имени, email, телефону, сообщению...",
            }
        ),
    )

    date_from = forms.DateField(
        required=False,
        label="Дата от",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    date_to = forms.DateField(
        required=False,
        label="Дата до",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    is_processed = forms.NullBooleanField(
        required=False,
        label="Статус обработки",
        widget=forms.Select(
            choices=[
                ("", "Все"),
                ("true", "Обработанные"),
                ("false", "Необработанные"),
            ],
            attrs={"class": "form-control"},
        ),
    )

    topic = forms.ChoiceField(
        required=False,
        label="Тема",
        choices=[("", "Все")] + Feedback.TOPIC_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean(self):
        """
        Валидирует корректность диапазона дат.

        Проверяет, что date_from <= date_to, если оба поля заполнены.

        Returns:
            dict: Очищенные данные формы

        Raises:
            forms.ValidationError: Если date_from > date_to
        """
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Дата начала не может быть позже даты окончания")

        return cleaned_data


# ============================================================================
# SYSTEM LOGS FILTER FORM - Форма фильтрации системных логов
# ============================================================================


class SystemLogsFilterForm(forms.Form):
    """
    Форма для фильтрации системных логов.

    Позволяет менеджерам фильтровать логи по уровню, типу действия,
    пользователю, дате и поисковому запросу.

    Поля:
        - search: Текстовый поиск по сообщению и IP адресу
        - level: Уровень лога (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - action_type: Тип действия (USER_LOGIN, FEEDBACK_CREATED и т.д.)
        - date_from: Дата начала периода
        - date_to: Дата окончания периода
    """

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по сообщению или IP адресу...",
            }
        ),
    )

    level = forms.ChoiceField(
        required=False,
        label="Уровень",
        choices=[("", "Все уровни")]
        + [
            ("DEBUG", "Debug"),
            ("INFO", "Info"),
            ("WARNING", "Warning"),
            ("ERROR", "Error"),
            ("CRITICAL", "Critical"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    action_type = forms.ChoiceField(
        required=False,
        label="Тип действия",
        choices=[("", "Все действия")]
        + [
            ("USER_LOGIN", "Вход пользователя"),
            ("USER_LOGOUT", "Выход пользователя"),
            ("USER_REGISTERED", "Регистрация пользователя"),
            ("USER_UPDATED", "Обновление пользователя"),
            ("USER_DELETED", "Удаление пользователя"),
            ("FEEDBACK_CREATED", "Создание обращения"),
            ("FEEDBACK_UPDATED", "Обновление обращения"),
            ("FEEDBACK_DELETED", "Удаление обращения"),
            ("SETTINGS_UPDATED", "Изменение настроек"),
            ("COURSE_CREATED", "Создание курса"),
            ("COURSE_UPDATED", "Обновление курса"),
            ("COURSE_DELETED", "Удаление курса"),
            ("PAYMENT_PROCESSED", "Обработка платежа"),
            ("ERROR_OCCURRED", "Ошибка"),
            ("SECURITY_EVENT", "Событие безопасности"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    date_from = forms.DateField(
        required=False,
        label="Дата от",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    date_to = forms.DateField(
        required=False,
        label="Дата до",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    def clean(self):
        """Валидирует корректность диапазона дат."""
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Дата начала не может быть позже даты окончания")

        return cleaned_data


# ============================================================================
# PAYMENTS FILTER FORM - Форма фильтрации платежей
# ============================================================================


class PaymentsFilterForm(forms.Form):
    """Форма для фильтрации платежных транзакций."""

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ID транзакции, email пользователя, название курса...",
            }
        ),
    )

    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=[
            ("", "Все статусы"),
            ("pending", "Ожидает оплаты"),
            ("processing", "Обрабатывается"),
            ("completed", "Завершён"),
            ("failed", "Ошибка"),
            ("cancelled", "Отменён"),
            ("refunded", "Возвращён"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    payment_method = forms.ChoiceField(
        required=False,
        label="Метод оплаты",
        choices=[
            ("", "Все методы"),
            ("cloudpayments", "CloudPayments"),
            ("tbc_georgia", "TBC Bank"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    currency = forms.ChoiceField(
        required=False,
        label="Валюта",
        choices=[
            ("", "Все валюты"),
            ("USD", "USD"),
            ("GEL", "GEL"),
            ("RUB", "RUB"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    date_from = forms.DateField(
        required=False,
        label="Дата от",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    date_to = forms.DateField(
        required=False,
        label="Дата до",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    amount_min = forms.DecimalField(
        required=False,
        label="Сумма от",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
        ),
    )

    amount_max = forms.DecimalField(
        required=False,
        label="Сумма до",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
        ),
    )

    def clean(self):
        """Валидирует корректность диапазонов дат и сумм."""
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        amount_min = cleaned_data.get("amount_min")
        amount_max = cleaned_data.get("amount_max")

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Дата начала не может быть позже даты окончания")

        if amount_min and amount_max and amount_min > amount_max:
            raise forms.ValidationError("Минимальная сумма не может быть больше максимальной")

        return cleaned_data


# ============================================================================
# PAYMENT REFUND FORM - Форма возврата платежа
# ============================================================================


class PaymentRefundForm(forms.Form):
    """Форма для оформления возврата средств по платежу."""

    refund_amount = forms.DecimalField(
        label="Сумма возврата",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
                "required": True,
            }
        ),
    )

    refund_reason = forms.CharField(
        label="Причина возврата",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Укажите причину возврата средств...",
            }
        ),
    )

    def clean_refund_amount(self):
        """Валидирует сумму возврата."""
        amount = self.cleaned_data.get("refund_amount")
        if amount and amount <= 0:
            raise forms.ValidationError("Сумма возврата должна быть больше нуля")
        return amount

    def clean_refund_reason(self):
        """Валидирует причину возврата."""
        reason = self.cleaned_data.get("refund_reason")
        if reason and len(reason) < 10:
            raise forms.ValidationError("Причина возврата должна содержать минимум 10 символов")
        return reason
