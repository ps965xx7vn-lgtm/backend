"""Фильтры Django шаблонов для обработки Markdown.

Предоставляет кастомные фильтры для конвертации Markdown в HTML:
- Безопасная обработка ссылок (target="_blank", rel="noopener noreferrer")
- Очистка Markdown синтаксиса для превью
- Умные выдержки из контента

Фильтры:
    markdownify: Расширенный конвертер markdown → HTML с безопасными ссылками
    markdown: Базовый конвертер markdown → HTML
    clean_markdown: Удаление markdown синтаксиса для plain text
    smart_excerpt: Генерация умных выдержек из текста
    get_item: Доступ к значениям словаря в шаблонах
"""

import re
from typing import Any

import markdown
from django import template
from django.utils.safestring import SafeString, mark_safe
from markdownify.templatetags.markdownify import markdownify as original_markdownify

register = template.Library()


@register.filter(name="markdownify")
def markdownify_with_blank_links(text: str | None) -> SafeString:
    """Конвертирует Markdown в HTML с безопасной обработкой ссылок.

    Оборачивает django-markdownify и добавляет атрибуты безопасности
    ко всем якорным тегам для защищенной навигации.

    Args:
        text: Текст в формате Markdown

    Returns:
        HTML разметка с target="_blank" и rel="noopener noreferrer" на всех ссылках

    Note:
        Переопределяет стандартное поведение markdownify при загрузке после
        библиотеки markdownify в шаблонах.

    Example:
        >>> markdownify_with_blank_links("[Ссылка](/url/)")
        '<a href="/url/" target="_blank" rel="noopener noreferrer">Ссылка</a>'
    """
    if not text:
        return mark_safe("")  # nosec B308 B703

    html = original_markdownify(text)

    def add_blank_target(match):
        tag = match.group(0)
        if "target=" in tag:
            return tag
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'

    html = re.sub(r"<a\s[^>]*>", add_blank_target, str(html))
    return mark_safe(html)  # nosec B308 B703


@register.filter(name="markdown")
def markdown_format(text: str | None) -> SafeString:
    """Конвертирует Markdown текст в HTML с поддержкой подсветки кода.

    Args:
        text: Текст в формате Markdown

    Returns:
        HTML разметка с поддержкой fenced code блоков

    Example:
        >>> markdown_format("**жирный** текст")
        '<strong>жирный</strong> текст'
    """
    if not text:
        return mark_safe("")  # nosec B308 B703
    return mark_safe(markdown.markdown(text, extensions=["fenced_code"]))  # nosec B308 B703


@register.filter(name="get_item")
def get_item(dictionary: dict[str, Any], key: str) -> Any:
    """Получает значение из словаря по ключу в Django шаблонах.

    Args:
        dictionary: Словарь для запроса
        key: Ключ для получения значения

    Returns:
        Значение для указанного ключа или None если ключ не существует

    Example:
        >>> get_item({"name": "Иван"}, "name")
        'Иван'
    """
    return dictionary.get(key)


@register.filter
def clean_markdown(text: str | None) -> str:
    """Удаляет Markdown синтаксис из текста для plain text превью.

    Убирает всё Markdown форматирование включая заголовки, выделение,
    ссылки, блоки кода, списки и другие синтаксические элементы.

    Args:
        text: Текст в формате Markdown для очистки

    Returns:
        Простой текст с удаленным Markdown синтаксисом и нормализованными пробелами

    Example:
        >>> clean_markdown("**Жирный** и [ссылка](/url/)")
        'Жирный и ссылка'
    """
    if not text:
        return text

    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*[-\*\+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


@register.filter
def smart_excerpt(content: str | None, words_limit: int = 20) -> str:
    """Генерирует умную выдержку из Markdown контента.

    Удаляет Markdown синтаксис и обрезает до указанного количества слов,
    добавляя многоточие при усечении контента.

    Args:
        content: Контент в формате Markdown
        words_limit: Максимальное количество слов (по умолчанию: 20)

    Returns:
        Выдержка в виде простого текста с суффиксом "..." если обрезан

    Example:
        >>> smart_excerpt("Раз два три четыре", 2)
        'Раз два...'
    """
    if not content:
        return ""

    clean_text = clean_markdown(content)
    words = clean_text.split()[:words_limit]

    return " ".join(words) + ("..." if len(content.split()) > words_limit else "")
