"""
Markdown Template Filters

Template tags для работы с Markdown в Django шаблонах:
- markdown: конвертирует Markdown в HTML
- get_item: получает значение из словаря по ключу
- clean_markdown: очищает текст от Markdown символов
- smart_excerpt: создает умный отрывок текста

Использование в шаблонах:
    {% load markdown_filters %}
    {{ article.content|markdown }}
    {{ article.content|clean_markdown }}
    {{ article.content|smart_excerpt:30 }}
"""

import re
from typing import Any, Dict, Optional

import markdown
from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_format(text: Optional[str]) -> SafeString:
    """
    Конвертирует Markdown текст в HTML.

    Args:
        text: Markdown текст для конвертации

    Returns:
        SafeString: HTML разметка

    Example:
        {{ article.content|markdown }}
    """
    if not text:
        return mark_safe("")

    return mark_safe(markdown.markdown(text, extensions=["fenced_code"]))


@register.filter(name="get_item")
def get_item(dictionary: Dict[str, Any], key: str) -> Any:
    """
    Получает значение из словаря по ключу в шаблоне.

    Args:
        dictionary: Словарь для поиска
        key: Ключ для получения значения

    Returns:
        Значение из словаря или None

    Example:
        {{ my_dict|get_item:"some_key" }}
    """
    return dictionary.get(key)


@register.filter
def clean_markdown(text: Optional[str]) -> str:
    """
    Очищает текст от Markdown-символов для отображения в превью карточек.

    Удаляет:
    - Заголовки (# ## ###)
    - Жирный текст (**text** или __text__)
    - Курсив (*text* или _text_)
    - Ссылки [text](url)
    - Инлайн код `code`
    - Блоки кода ```
    - Цитаты (>)
    - Списки (- * +)
    - Нумерованные списки (1. 2.)
    - Горизонтальные линии (---)

    Args:
        text: Markdown текст для очистки

    Returns:
        str: Очищенный текст без Markdown символов

    Example:
        {{ article.content|clean_markdown }}
    """
    if not text:
        return text

    # Удаляем заголовки (# ## ### и т.д.)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Удаляем жирный текст (**text** или __text__)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)

    # Удаляем курсив (*text* или _text_)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    # Удаляем ссылки [text](url)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Удаляем инлайн код `code`
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Удаляем блоки кода ```
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Удаляем цитаты (>)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Удаляем списки (- * +)
    text = re.sub(r"^[\s]*[-\*\+]\s+", "", text, flags=re.MULTILINE)

    # Удаляем нумерованные списки
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

    # Удаляем горизонтальные линии
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)

    # Удаляем лишние пробелы и переносы строк
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


@register.filter
def smart_excerpt(content: Optional[str], words_limit: int = 20) -> str:
    """
    Умное извлечение отрывка из контента с очисткой от Markdown.

    Очищает текст от Markdown символов и обрезает до указанного
    количества слов с добавлением "..." если текст был обрезан.

    Args:
        content: Исходный Markdown контент
        words_limit: Максимальное количество слов (по умолчанию 20)

    Returns:
        str: Отрывок текста с "..." если был обрезан

    Example:
        {{ article.content|smart_excerpt:30 }}
        {{ article.content|smart_excerpt }}  # по умолчанию 20 слов
    """
    if not content:
        return ""

    # Очищаем от Markdown
    clean_text = clean_markdown(content)

    # Разделяем на слова и берем нужное количество
    words = clean_text.split()[:words_limit]

    return " ".join(words) + ("..." if len(content.split()) > words_limit else "")
