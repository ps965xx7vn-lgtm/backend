from __future__ import annotations

import logging
import re
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .models import Comment

logger = logging.getLogger(__name__)


class CommentForm(forms.ModelForm):
    """
    Форма для создания и редактирования комментариев к статьям.

    Поддерживает:
    - Создание основных комментариев
    - Создание вложенных ответов (через parent_id)
    - Валидацию длины контента
    - Защиту от спама (запрещены повторяющиеся символы)
    - Базовую HTML-санитизацию (strip_tags)

    Fields:
        content (TextField): Текст комментария (обязательное)
        parent_id (IntegerField): ID родительского комментария для ответов (скрытое, необязательное)

    Validation:
        - Минимальная длина: 3 символа
        - Максимальная длина: 5000 символов
        - Запрещены комментарии из одних повторяющихся символов
        - HTML-теги автоматически удаляются

    Example:
        >>> form = CommentForm(data={'content': 'Отличная статья!'})
        >>> if form.is_valid():
        ...     comment = form.save(commit=False)
        ...     comment.article = article
        ...     comment.author = request.user
        ...     comment.save()
    """

    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "comment-textarea-revolutionary",
                    "placeholder": "Поделитесь вашими мыслями о статье...",
                    "rows": 4,
                    "maxlength": "5000",
                }
            )
        }
        labels = {"content": ""}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Инициализация формы с настройкой обязательных полей.

        Args:
            *args: Позиционные аргументы для ModelForm.__init__()
            **kwargs: Именованные аргументы для ModelForm.__init__()
        """
        super().__init__(*args, **kwargs)
        self.fields["content"].required = True
        self.fields["content"].min_length = 3
        self.fields["content"].max_length = 5000

    def clean_content(self) -> str:
        """
        Валидация и санитизация содержимого комментария.

        Проверки:
        1. Удаление HTML-тегов для безопасности
        2. Проверка минимальной длины после удаления пробелов
        3. Защита от спам-комментариев (повторяющиеся символы)
        4. Удаление лишних пробелов и переносов строк

        Returns:
            str: Очищенный и валидированный текст комментария

        Raises:
            ValidationError: Если контент не прошёл валидацию
        """
        content = self.cleaned_data.get("content", "")

        # Удаляем HTML-теги для безопасности
        content = strip_tags(content)

        # Проверка минимальной длины
        content_stripped = content.strip()
        if len(content_stripped) < 3:
            logger.warning("Попытка отправить слишком короткий комментарий")
            raise ValidationError(
                "Комментарий слишком короткий. Минимум 3 символа.", code="too_short"
            )

        # Проверка максимальной длины
        if len(content_stripped) > 5000:
            logger.warning(
                f"Попытка отправить слишком длинный комментарий ({len(content_stripped)} символов)"
            )
            raise ValidationError(
                "Комментарий слишком длинный. Максимум 5000 символов.", code="too_long"
            )

        # Защита от спама: проверка на повторяющиеся символы
        # Если более 70% символов повторяются - это спам
        if len(content_stripped) > 10:
            char_counts = {}
            for char in content_stripped:
                if char not in (" ", "\n", "\t"):
                    char_counts[char] = char_counts.get(char, 0) + 1

            if char_counts:
                max_char_count = max(char_counts.values())
                total_chars = sum(char_counts.values())
                repetition_ratio = max_char_count / total_chars if total_chars > 0 else 0

                if repetition_ratio > 0.7:
                    logger.warning(
                        f"Обнаружен спам-комментарий (повторение {repetition_ratio:.0%})"
                    )
                    raise ValidationError(
                        "Комментарий выглядит как спам. Пожалуйста, напишите осмысленный текст.",
                        code="spam_detected",
                    )

        # Удаление лишних пробелов и переносов строк
        content = re.sub(r"\n{3,}", "\n\n", content)  # Максимум 2 переноса подряд
        content = re.sub(r" {2,}", " ", content)  # Максимум 1 пробел подряд
        content = content.strip()

        return content

    def clean(self) -> dict[str, Any]:
        """
        Общая валидация формы.

        Проверяет корректность parent_id если указан.

        Returns:
            dict[str, Any]: Очищенные данные формы

        Raises:
            ValidationError: Если parent_id некорректен
        """
        cleaned_data = super().clean()
        parent_id = cleaned_data.get("parent_id")

        # Валидация parent_id если указан
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
                # Проверяем, что родительский комментарий одобрен
                if not parent_comment.is_approved:
                    logger.warning(f"Попытка ответить на неодобренный комментарий {parent_id}")
                    raise ValidationError(
                        "Нельзя отвечать на неодобренные комментарии.", code="invalid_parent"
                    )
            except Comment.DoesNotExist as err:
                logger.error(f"Попытка ответить на несуществующий комментарий {parent_id}")
                raise ValidationError(
                    "Родительский комментарий не найден.", code="parent_not_found"
                ) from err

        return cleaned_data
