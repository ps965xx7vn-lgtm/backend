"""
Конфигурация переводов для моделей курсов.

Использует django-modeltranslation для автоматического создания
полей переводов для поддерживаемых языков (ru, en, ka).
"""

from modeltranslation.translator import TranslationOptions, register

from .models import Course, ExtraSource, Lesson, Step, Tip


@register(Course)
class CourseTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Course.

    Структура БД после миграции:
        - name_ru, name_en, name_ka
        - description_ru, description_en, description_ka
        - short_description_ru, short_description_en, short_description_ka
    """

    fields = (
        "name",  # Название курса
        "description",  # Полное описание
        "short_description",  # Краткое описание
    )
    required_languages = {
        "ru": ("name", "short_description"),  # Обязательные для русского
        "en": ("name",),  # Минимум для английского
        "ka": ("name",),  # Минимум для грузинского
    }


@register(Lesson)
class LessonTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Lesson.

    Структура БД после миграции:
        - name_ru, name_en, name_ka
        - short_description_ru, short_description_en, short_description_ka
    """

    fields = (
        "name",  # Название урока
        "short_description",  # Краткое описание
    )
    required_languages = {
        "ru": ("name",),
        "en": ("name",),
        "ka": ("name",),
    }


@register(Step)
class StepTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Step.

    Много контента - все текстовые поля переводятся.

    Структура БД после миграции:
        - name_ru, name_en, name_ka
        - description_ru, description_en, description_ka
        - actions_ru, actions_en, actions_ka
        - self_check_ru, self_check_en, self_check_ka
        - troubleshooting_help_ru, troubleshooting_help_en, troubleshooting_help_ka
        - repair_description_ru, repair_description_en, repair_description_ka
    """

    fields = (
        "name",  # Название шага
        "description",  # Описание шага
        "actions",  # Действия для выполнения
        "self_check",  # Проверка себя
        "troubleshooting_help",  # Помощь при трудностях (для студентов)
        "repair_description",  # Примечания администратора (не для студентов)
    )
    required_languages = {
        "ru": ("name", "description"),
        "en": ("name",),
        "ka": ("name",),
    }


@register(Tip)
class TipTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Tip (подсказки к шагам).

    Структура БД после миграции:
        - title_ru, title_en, title_ka
        - description_ru, description_en, description_ka
    """

    fields = (
        "title",  # Заголовок подсказки
        "description",  # Описание подсказки
    )
    required_languages = {
        "ru": ("title", "description"),
        "en": ("title",),
        "ka": ("title",),
    }


@register(ExtraSource)
class ExtraSourceTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели ExtraSource (дополнительные материалы).

    Структура БД после миграции:
        - name_ru, name_en, name_ka
        - url_ru, url_en, url_ka (URL может быть разным для языков)
    """

    fields = (
        "name",  # Название источника
        "url",  # URL (может различаться для языков)
    )
    required_languages = {
        "ru": ("name",),
        "en": ("name",),
        "ka": ("name",),
    }
