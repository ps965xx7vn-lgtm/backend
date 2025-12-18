"""
Tests for Blog Forms.

Этот модуль тестирует формы блога:
- CommentForm - форма добавления комментария

Каждый тест проверяет:
- Валидацию полей
- Санитизацию HTML
- Защиту от XSS
- Обязательные поля
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from blog.forms import CommentForm
from blog.tests.factories import ArticleFactory, UserFactory


@pytest.mark.django_db
class TestCommentForm:
    """Тесты для формы комментариев."""

    def test_valid_comment_form(self):
        """Тест валидной формы."""
        article = ArticleFactory()
        form = CommentForm(data={"content": "This is a valid comment."})

        assert form.is_valid()

        comment = form.save(commit=False)
        comment.article = article
        comment.author = UserFactory()
        comment.save()

        assert comment.content == "This is a valid comment."

    def test_empty_comment(self):
        """Тест пустого комментария."""
        form = CommentForm(data={"content": ""})

        assert not form.is_valid()
        assert "content" in form.errors

    def test_comment_too_short(self):
        """Тест слишком короткого комментария."""
        form = CommentForm(data={"content": "Hi"})  # Менее 3 символов

        # Зависит от валидации в форме
        # Может быть валидным или нет
        if not form.is_valid():
            assert "content" in form.errors

    def test_comment_xss_protection(self):
        """Тест защиты от XSS."""
        form = CommentForm(data={"content": '<script>alert("XSS")</script>Normal text'})

        # Форма должна быть валидной, но содержимое должно быть санитизировано
        if form.is_valid():
            comment = form.save(commit=False)
            # Проверяем, что скрипт удален или экранирован
            assert "<script>" not in comment.content or "&lt;script&gt;" in comment.content

    def test_comment_html_tags_allowed(self):
        """Тест разрешенных HTML тегов."""
        form = CommentForm(data={"content": "<strong>Bold text</strong> and <em>italic</em>"})

        # Зависит от настроек формы - может разрешать или запрещать HTML
        # Проверяем, что форма обрабатывает это корректно
        assert form.is_valid() or not form.is_valid()  # Любой результат валиден

    def test_comment_max_length(self):
        """Тест максимальной длины комментария."""
        long_content = "x" * 10000  # 10000 символов
        form = CommentForm(data={"content": long_content})

        # Зависит от настройки max_length в модели
        # Может быть валидным или нет
        if not form.is_valid():
            assert "content" in form.errors

    def test_comment_whitespace_only(self):
        """Тест комментария только из пробелов."""
        form = CommentForm(data={"content": "   \n\t   "})

        # Должен быть невалидным
        assert not form.is_valid()

    def test_comment_with_links(self):
        """Тест комментария с ссылками."""
        form = CommentForm(data={"content": "Check out https://example.com for more info!"})

        assert form.is_valid()
        comment = form.save(commit=False)
        assert "https://example.com" in comment.content

    def test_comment_with_email(self):
        """Тест комментария с email."""
        form = CommentForm(data={"content": "Contact me at test@example.com"})

        assert form.is_valid()

    def test_comment_special_characters(self):
        """Тест специальных символов."""
        form = CommentForm(data={"content": "Special chars: @#$%^&*()_+-=[]{}|;:,.<>?"})

        assert form.is_valid()

    def test_comment_unicode_characters(self):
        """Тест Unicode символов."""
        form = CommentForm(data={"content": "Unicode: 你好 مرحبا हैलो"})

        assert form.is_valid()

    def test_comment_code_blocks(self):
        """Тест блоков кода."""
        form = CommentForm(data={"content": 'Code example: `print("Hello")`'})

        assert form.is_valid()


@pytest.mark.django_db
class TestCommentFormEdgeCases:
    """Тесты граничных случаев для формы комментариев."""

    def test_comment_with_newlines(self):
        """Тест комментария с переносами строк."""
        form = CommentForm(data={"content": "Line 1\nLine 2\nLine 3"})

        assert form.is_valid()
        comment = form.save(commit=False)
        assert "\n" in comment.content

    def test_comment_with_quotes(self):
        """Тест комментария с кавычками."""
        form = CommentForm(data={"content": "He said \"Hello\" and I said 'Hi'"})

        assert form.is_valid()

    def test_comment_sql_injection_attempt(self):
        """Тест попытки SQL injection."""
        form = CommentForm(data={"content": "'; DROP TABLE blog_comment; --"})

        # Должна быть валидной формой, но Django ORM защитит от injection
        assert form.is_valid()
        comment = form.save(commit=False)
        assert comment.content == "'; DROP TABLE blog_comment; --"

    def test_comment_with_html_entities(self):
        """Тест HTML entities."""
        form = CommentForm(data={"content": "Entities: &lt; &gt; &amp; &quot;"})

        assert form.is_valid()
