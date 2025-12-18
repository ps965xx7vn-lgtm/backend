"""
Reviewers Forms - Современные формы для работы с рецензиями и профилем ревьюера.

Формы основаны на лучших практиках из students/forms.py:
- Полная валидация
- Подробные help_text
- Clean методы для сложной валидации
- Type hints

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from typing import Any, Dict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from authentication.models import Reviewer
from courses.models import Course

from .models import Review, StudentImprovement


class ReviewForm(forms.ModelForm):
    """
    Форма для создания/редактирования рецензии на работу студента.

    Поля:
        status: Статус проверки (approved/needs_work)
        comments: Подробные комментарии к работе
        time_spent: Время затраченное на проверку (в минутах)

    Валидация:
        - Для needs_work требуются comments
        - time_spent должно быть положительным числом
    """

    class Meta:
        model = Review
        fields = ["status", "comments", "time_spent"]
        widgets = {
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "id_status",
                }
            ),
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Подробные комментарии к работе студента...",
                    "id": "id_comments",
                }
            ),
            "time_spent": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Время в минутах",
                    "id": "id_time_spent",
                }
            ),
        }
        labels = {
            "status": _("Статус проверки"),
            "comments": _("Комментарии"),
            "time_spent": _("Время проверки (мин)"),
        }
        help_texts = {
            "status": _("Выберите статус: принята или требует доработки"),
            "comments": _("Подробный отзыв о работе с рекомендациями"),
            "time_spent": _("Примерное время затраченное на проверку"),
        }

    def clean_comments(self) -> str:
        """Валидация комментариев."""
        comments = self.cleaned_data.get("comments", "").strip()
        status = self.cleaned_data.get("status")

        if status in ["needs_work", "rejected"] and not comments:
            raise ValidationError(
                "Для работ требующих доработки или отклоненных комментарии обязательны"
            )

        if comments and len(comments) < 10:
            raise ValidationError("Комментарии должны содержать минимум 10 символов")

        return comments

    def clean_time_spent(self) -> int:
        """Валидация времени проверки."""
        time_spent = self.cleaned_data.get("time_spent", 0)

        if time_spent < 0:
            raise ValidationError("Время проверки не может быть отрицательным")

        return time_spent


class ReviewerProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля ревьюера.

    Поля:
        bio: Биография и опыт работы
        is_active: Активен ли профиль (принимает новые работы)
        courses: Курсы для проверки (ManyToMany)
        max_reviews_per_day: Максимальное количество проверок в день

    Валидация:
        - bio должна быть не менее 50 символов
        - max_reviews_per_day от 1 до 50
        - Минимум 1 курс для проверки
    """

    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=_("Курсы для проверки"),
        help_text=_("Выберите курсы, работы по которым вы можете проверять"),
    )

    class Meta:
        model = Reviewer
        fields = ["bio", "is_active", "courses", "max_reviews_per_day"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Расскажите о своем опыте и экспертизе...",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "max_reviews_per_day": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "50",
                }
            ),
        }
        labels = {
            "bio": _("О себе"),
            "is_active": _("Активен (принимать новые работы)"),
            "max_reviews_per_day": _("Макс. проверок в день"),
        }
        help_texts = {
            "bio": _("Информация о вашем опыте, образовании и экспертизе (минимум 50 символов)"),
            "is_active": _("Если отключено, вы не будете получать новые работы на проверку"),
            "max_reviews_per_day": _(
                "Максимальное количество работ которые можете проверить за день (1-50)"
            ),
        }

    def clean_bio(self) -> str:
        """Валидация биографии."""
        bio = self.cleaned_data.get("bio", "").strip()

        if bio and len(bio) < 50:
            raise ValidationError("Биография должна содержать минимум 50 символов")

        return bio

    def clean_courses(self) -> Any:
        """Валидация курсов."""
        courses = self.cleaned_data.get("courses")

        if not courses or courses.count() < 1:
            raise ValidationError("Выберите хотя бы один курс для проверки")

        return courses

    def clean_max_reviews_per_day(self) -> int:
        """Валидация лимита проверок."""
        max_reviews = self.cleaned_data.get("max_reviews_per_day")

        if max_reviews and (max_reviews < 1 or max_reviews > 50):
            raise ValidationError("Количество проверок в день должно быть от 1 до 50")

        return max_reviews or 10  # Default value


class SubmissionFilterForm(forms.Form):
    """
    Форма для фильтрации списка работ на проверку.

    Поля:
        status: Статус работы (pending/approved/changes_requested)
        course: Курс
        date_from: Дата от
        date_to: Дата до
        search: Поиск по email студента

    Валидация:
        - date_to должна быть >= date_from
    """

    status = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Все статусы"),
            ("pending", "Ожидает проверки"),
            ("approved", "Принята"),
            ("changes_requested", "Требует доработки"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        label=_("Статус"),
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="Все курсы",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        label=_("Курс"),
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        label=_("Дата от"),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
        label=_("Дата до"),
    )

    search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по email студента...",
            }
        ),
        label=_("Поиск"),
    )

    def clean(self) -> Dict[str, Any]:
        """Валидация всей формы."""
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise ValidationError('Дата "до" не может быть раньше даты "от"')

        return cleaned_data


class StudentImprovementForm(forms.ModelForm):
    """
    Форма для добавления конкретных улучшений к работе студента.

    Поля:
        improvement_text: Описание улучшения
        priority: Приоритет (high/medium/low)
    """

    PRIORITY_CHOICES = [
        ("high", "Высокий"),
        ("medium", "Средний"),
        ("low", "Низкий"),
    ]

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        initial="medium",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        label=_("Приоритет"),
        help_text=_("Важность данного улучшения"),
    )

    class Meta:
        model = StudentImprovement
        fields = ["title", "improvement_text", "priority"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Добавить проверку на пустые значения",
                }
            ),
            "improvement_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Опишите конкретное улучшение...",
                }
            ),
        }
        labels = {
            "title": _("Название шага"),
            "improvement_text": _("Описание улучшения"),
        }
        help_texts = {
            "title": _("Краткое название шага улучшения"),
            "improvement_text": _("Конкретное улучшение которое студент должен внести"),
        }

    def clean_improvement_text(self) -> str:
        """Валидация текста улучшения."""
        text = self.cleaned_data.get("improvement_text", "").strip()

        if not text:
            raise ValidationError("Описание улучшения обязательно")

        if len(text) < 10:
            raise ValidationError("Описание должно содержать минимум 10 символов")

        return text
