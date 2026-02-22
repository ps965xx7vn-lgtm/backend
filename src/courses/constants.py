"""
Константы для расчёта времени прохождения курсов.

За основу взято реалистичное время для начинающего:
  - Прочитать описание шага
  - Выполнить практическое задание
  - Сделать самопроверку
"""

from django.utils.translation import gettext as _

# Минут на один шаг для начинающего (чтение + практика + самопроверка)
MINUTES_PER_STEP = 20


def format_duration(minutes: int) -> str:
    """
    Форматирует минуты в читаемый вид с учётом активного языка Django.

    Examples (ru):  15 → '15 мин' | 60 → '~1 ч' | 80 → '~1 ч 20 мин'
    Examples (en):  15 → '15 min' | 60 → '~1 h' | 80 → '~1 h 20 min'
    Examples (ka):  15 → '15 წთ' | 60 → '~1 სთ' | 80 → '~1 სთ 20 წთ'
    """
    min_label = _("мин")
    hour_label = _("ч")

    if minutes <= 0:
        return f"0 {min_label}"
    if minutes < 60:
        return f"{minutes} {min_label}"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"~{hours} {hour_label}"
    return f"~{hours} {hour_label} {mins} {min_label}"
