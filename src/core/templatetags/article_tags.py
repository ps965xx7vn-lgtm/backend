"""
Article Template Tags

Template tags для работы со статьями блога:
- pluralize_articles: правильное склонение слова "статья"

Использование в шаблонах:
    {% load article_tags %}
    {{ articles.count|pluralize_articles }}
"""

from django import template

register = template.Library()


@register.filter
def pluralize_articles(count: int) -> str:
    """
    Склонение слова "статья" в зависимости от количества.

    Правила русского языка:
    - 1 статья (1, 21, 31, ...)
    - 2-4 статьи (2, 3, 4, 22, 23, 24, ...)
    - 5+ статей (5, 6, ..., 11-19, 25, ...)

    Args:
        count: Количество статей

    Returns:
        str: Склоненное слово с числом, например "5 статей"

    Example:
        {{ articles.count|pluralize_articles }}
        Output: "1 статья", "2 статьи", "5 статей"
    """
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} статья"
    elif 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
        return f"{count} статьи"
    else:
        return f"{count} статей"
