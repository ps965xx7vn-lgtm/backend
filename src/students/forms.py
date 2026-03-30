"""
Students Forms - Django формы для работы студентов.

Этот модуль содержит формы для работы студентов с курсами:
    - LessonSubmissionForm: Отправка ссылки на репозиторий (GitHub или CodeHS) с выполненной работой

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django import forms

from reviewers.models import LessonSubmission


class LessonSubmissionForm(forms.ModelForm):
    """Форма отправки выполненной работы по уроку через ссылку на репозиторий.

    Валидирует URL с поддерживаемых платформ (GitHub, CodeHS) с проверкой
    корректной структуры репозитория и доступности.

    Поддерживаемые платформы:
        - GitHub: https://github.com/username/repository
        - CodeHS (песочница): https://codehs.com/sandbox/username/project

    Правила валидации:
        - URL должен использовать HTTPS протокол
        - Должен быть с поддерживаемой платформы (GitHub или CodeHS)
        - Должен содержать username/owner и имя repository/project
        - Должен следовать специфичной для платформы структуре URL

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
                    "placeholder": "https://codehs.com/share/...",
                    "title": "Введите ссылку на проект с выполненным заданием",
                }
            ),
        }
        labels = {"lesson_url": "Ссылка на репозиторий/песочницу"}
        help_texts = {
            "lesson_url": (
                "Укажите ссылку на ваш репозиторий с выполненным заданием. "
                "Поддерживаются: CodeHS (https://codehs.com/share/...) "
                "и GitHub (https://github.com/user/repo)"
            )
        }

    def clean_lesson_url(self) -> str:
        """Валидирует URL репозитория с поддерживаемых платформ.

        Проверяет URL с GitHub и CodeHS, обеспечивая корректную структуру
        с идентификаторами username/owner и repository/project.

        Returns:
            Валидированный URL репозитория

        Raises:
            ValidationError: Когда URL невалиден:
                - Пустой URL
                - Не HTTPS протокол
                - Не с поддерживаемой платформы
                - Отсутствует username или имя репозитория
                - Некорректная структура URL

        Валидные примеры:
            - https://github.com/user/repo
            - https://github.com/user/repo/tree/main
            - https://codehs.com/sandbox/username/project
            - https://codehs.com/sandbox/username/project?collaborate=xxx

        Невалидные примеры:
            - https://github.com/user (отсутствует репозиторий)
            - http://github.com/user/repo (не HTTPS)
            - https://gitlab.com/user/repo (неподдерживаемая платформа)
        """
        url = self.cleaned_data.get("lesson_url", "").strip()

        if not url:
            raise forms.ValidationError("Необходимо указать ссылку на репозиторий")

        if not url.startswith("https://"):
            raise forms.ValidationError("Ссылка должна использовать HTTPS протокол")

        is_github = url.startswith("https://github.com/")
        is_codehs = url.startswith("https://codehs.com/sandbox/") or url.startswith(
            "https://codehs.com/share/"
        )

        if not (is_github or is_codehs):
            raise forms.ValidationError(
                "Поддерживаются ссылки на GitHub и CodeHS. "
                "Примеры: https://github.com/username/repository или "
                "https://codehs.com/share/project"
            )

        if is_github:
            path = url.replace("https://github.com/", "").split("#")[0].split("?")[0]
            parts = [p for p in path.split("/") if p]
            if len(parts) < 2:
                raise forms.ValidationError(
                    "GitHub ссылка должна содержать имя пользователя и репозиторий. "
                    "Пример: https://github.com/username/repository"
                )

        if is_codehs:
            path = (
                url.replace("https://codehs.com/sandbox/", "")
                .replace("https://codehs.com/share/", "")
                .split("?")[0]
                .split("#")[0]
            )
            parts = [p for p in path.split("/") if p]
            if not parts:
                raise forms.ValidationError(
                    "CodeHS ссылка должна указывать на проект. "
                    "Пример: https://codehs.com/share/project-name"
                )

        return url
