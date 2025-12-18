import re

from django import template

register = template.Library()


@register.filter
def clean_markdown(text):
    """
    Очищает текст от Markdown-символов для отображения в превью карточек.
    Удаляет заголовки (#), жирный текст (**), курсив (*), ссылки и другие символы.
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
def smart_excerpt(content, words_limit=20):
    """
    Умное извлечение отрывка из контента с очисткой от Markdown.
    """
    if not content:
        return ""

    # Очищаем от Markdown
    clean_text = clean_markdown(content)

    # Разделяем на слова и берем нужное количество
    words = clean_text.split()[:words_limit]

    return " ".join(words) + ("..." if len(content.split()) > words_limit else "")


@register.filter
def split(value, sep=","):
    """Split a string by `sep` and return a list. If value is falsy, return empty list."""
    if value is None:
        return []
    try:
        return [part for part in str(value).split(sep)]
    except Exception:
        return []


@register.filter
def strip(value):
    """Strip whitespace from a string (wrapper around str.strip)."""
    if value is None:
        return ""
    try:
        return str(value).strip()
    except Exception:
        return value


@register.filter
def safe_first(value):
    """Безопасно получает первый символ строки. Возвращает '?' если значение None или пустое."""
    if value is None or value == "":
        return "?"
    try:
        return str(value)[0]
    except (IndexError, TypeError):
        return "?"
