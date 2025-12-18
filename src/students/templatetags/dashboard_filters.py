from django import template

register = template.Library()


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
