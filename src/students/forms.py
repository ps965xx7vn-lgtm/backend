"""
Students Forms - Django формы для работы студентов.

Этот модуль содержит формы для работы студентов с курсами:
    - LessonSubmissionForm: Отправка ссылки на GitHub репозиторий с выполненной работой

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django import forms

from reviewers.models import LessonSubmission


class LessonSubmissionForm(forms.ModelForm):
    """
    Форма отправки ссылки на GitHub репозиторий с выполненной работой по уроку.

    Валидирует что ссылка ведет на GitHub репозиторий с корректной структурой URL
    (https://github.com/username/repository).

    Fields:
        lesson_url: URL GitHub репозитория с выполненным заданием

    Validation:
        - URL должен начинаться с https://github.com/
        - URL должен содержать username и repository name
        - Формат: https://github.com/username/repository

    Example:
        >>> form = LessonSubmissionForm({
        ...     'lesson_url': 'https://github.com/user/python-homework'
        ... })
        >>> if form.is_valid():
        ...     submission = form.save(commit=False)
        ...     submission.student = request.user
        ...     submission.save()
    """

    class Meta:
        model = LessonSubmission
        fields = ["lesson_url"]
        widgets = {
            "lesson_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username/repository",
                    "pattern": "https://github\\.com/.*",
                    "title": "Введите ссылку на GitHub репозиторий",
                }
            ),
        }
        labels = {"lesson_url": "Ссылка на GitHub репозиторий"}
        help_texts = {
            "lesson_url": "Укажите ссылку на ваш GitHub репозиторий с выполненным заданием"
        }

    def clean_lesson_url(self) -> str:
        """
        Валидирует что URL является корректной ссылкой на GitHub репозиторий.

        Returns:
            Валидированный URL GitHub репозитория

        Raises:
            ValidationError: Если URL не соответствует формату GitHub репозитория:
                - URL пустой
                - URL не начинается с https://github.com/
                - URL не содержит username и repository name

        Example:
            Валидные:
            - https://github.com/user/repo
            - https://github.com/user/repo/tree/main

            Невалидные:
            - https://github.com/user (нет repository)
            - https://gitlab.com/user/repo (не GitHub)
            - github.com/user/repo (нет https://)
        """
        url = self.cleaned_data.get("lesson_url")

        if not url:
            raise forms.ValidationError("Необходимо указать ссылку на GitHub репозиторий")

        if not url.startswith("https://github.com/"):
            raise forms.ValidationError("Ссылка должна начинаться с https://github.com/")

        # Extract path after github.com/
        path = url.replace("https://github.com/", "")

        # Check that there's at least username and repository
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2:
            raise forms.ValidationError(
                "Ссылка должна содержать имя пользователя и название репозитория. "
                "Пример: https://github.com/username/repository"
            )

        return url
