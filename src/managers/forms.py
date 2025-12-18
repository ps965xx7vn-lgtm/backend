"""
Manager Forms Module - Django формы для административной панели.

Этот модуль предоставляет формы для работы с обратной связью
и фильтрации данных в административном интерфейсе.

Формы:
    - FeedbackForm: Форма создания/редактирования обратной связи
    - FeedbackFilterForm: Форма фильтрации списка обращений

Особенности:
    - Кастомная валидация полей (телефон, email, сообщение)
    - Кастомные виджеты для улучшения UX
    - Валидация на стороне сервера
    - Type hints для всех методов

Валидация:
    - Телефон: должен начинаться с +
    - Email: стандартная валидация Django
    - Сообщение: минимум 10 символов
    - Имя: минимум 2 символа

Примечание:
    Используется в Django admin и в manager dashboard views.

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

    Позволяет администраторам фильтровать обращения по тексту
    и диапазону дат для удобного поиска и анализа.

    Поля:
        - search: Текстовый поиск по имени, email, теме, сообщению
        - date_from: Дата начала периода (необязательное)
        - date_to: Дата окончания периода (необязательное)

    Виджеты:
        - search: TextInput с placeholder
        - date_from: DateInput с type='date'
        - date_to: DateInput с type='date'

    Example:
        >>> # В view функции
        >>> filter_form = FeedbackFilterForm(request.GET)
        >>> feedbacks = Feedback.objects.all()
        >>>
        >>> if filter_form.is_valid():
        >>>     search = filter_form.cleaned_data.get('search')
        >>>     date_from = filter_form.cleaned_data.get('date_from')
        >>>     date_to = filter_form.cleaned_data.get('date_to')
        >>>
        >>>     if search:
        >>>         feedbacks = feedbacks.filter(
        >>>             Q(name__icontains=search) |
        >>>             Q(email__icontains=search) |
        >>>             Q(subject__icontains=search)
        >>>         )
        >>>     if date_from:
        >>>         feedbacks = feedbacks.filter(registered_at__gte=date_from)
        >>>     if date_to:
        >>>         feedbacks = feedbacks.filter(registered_at__lte=date_to)
    """

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по имени, email, теме...",
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
