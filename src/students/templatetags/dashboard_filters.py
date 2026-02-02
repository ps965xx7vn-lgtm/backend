from django import template
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def translate_role(role_name):
    """
    Перевод названия роли пользователя.
    """
    if not role_name:
        return _("Студент")

    # Словарь переводов для ролей
    role_translations = {
        "student": _("Студент"),
        "mentor": _("Ментор"),
        "reviewer": _("Ревьюер"),
        "manager": _("Менеджер"),
    }

    # Нормализуем название роли к lowercase
    role_key = role_name.lower()

    # Возвращаем перевод или оригинальное значение
    return role_translations.get(role_key, role_name)


@register.filter
def pluralize_steps(count):
    """
    Склонение слова "шаг" в зависимости от числа.
    1 шаг, 2 шага, 5 шагов
    """
    count = int(count)
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} шаг"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return f"{count} шага"
    else:
        return f"{count} шагов"
