"""
Account Signals Module - Сигналы для автоматизации работы со студентами (Student модель).

Этот модуль содержит сигналы Django для автоматического управления студентами:
    - create_user_student: Создает студента при регистрации нового пользователя
    - save_user_student: Сохраняет студента при обновлении модели User

Сигналы обеспечивают целостность данных между User и Student моделями.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import Student

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_student(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    """
    Автоматически создает профиль для нового пользователя в зависимости от его роли.

    При создании нового пользователя:
    - Создается профиль в зависимости от роли (Student, Reviewer, Mentor, Manager, Admin, Support)
    - Если роль не указана, создается Student профиль по умолчанию

    Срабатывает после сохранения объекта User с флагом created=True.
    Создает связанный объект профиля с настройками по умолчанию.

    Args:
        sender: Класс модели User (отправитель сигнала)
        instance: Экземпляр созданного пользователя
        created: True если пользователь только что создан, False при обновлении
        **kwargs: Дополнительные аргументы сигнала Django

    Returns:
        None

    Example:
        >>> user = User.objects.create_user(email='user@example.com', password='pass123')
        # Автоматически создастся Student профиль
        >>> user = User.objects.create_user(email='mentor@example.com', password='pass123', role=mentor_role)
        # Автоматически создастся Mentor профиль

    Note:
        Профиль создается в зависимости от роли пользователя.
        По умолчанию - Student профиль.
    """
    if created:
        try:
            from authentication.models import Admin, Manager, Mentor, Reviewer, Support

            role_name = instance.role.name if instance.role else "student"
            role_display = instance.role.get_name_display() if instance.role else "Студент"

            # Создаем профиль в зависимости от роли
            if role_name == "student":
                Student.objects.create(user=instance)
                logger.info(f"Создан профиль Student для {instance.email} с ролью '{role_display}'")
            elif role_name == "reviewer":
                Reviewer.objects.create(user=instance)
                logger.info(
                    f"Создан профиль Reviewer для {instance.email} с ролью '{role_display}'"
                )
            elif role_name == "mentor":
                Mentor.objects.create(user=instance)
                logger.info(f"Создан профиль Mentor для {instance.email} с ролью '{role_display}'")
            elif role_name == "manager":
                Manager.objects.create(user=instance)
                logger.info(f"Создан профиль Manager для {instance.email} с ролью '{role_display}'")
            elif role_name == "admin":
                Admin.objects.create(user=instance)
                # Установить флаги для доступа в Django Admin
                if not instance.is_staff:
                    instance.is_staff = True
                    # Используем update для избежания рекурсии сигнала
                    User.objects.filter(pk=instance.pk).update(is_staff=True)
                logger.info(f"Создан профиль Admin для {instance.email} с ролью '{role_display}'")
            elif role_name == "support":
                Support.objects.create(user=instance)
                logger.info(f"Создан профиль Support для {instance.email} с ролью '{role_display}'")
            else:
                # По умолчанию создаем Student профиль
                Student.objects.create(user=instance)
                logger.warning(
                    f"Неизвестная роль '{role_name}', создан Student профиль для {instance.email}"
                )

            # Автоматическая подписка на все типы уведомлений
            subscribe_user_to_notifications(instance)

        except Exception as e:
            logger.error(f"Ошибка создания профиля для {instance.email}: {e}")


@receiver(post_save, sender=User)
def save_user_student(sender: Any, instance: Any, created: bool, **kwargs: Any) -> None:
    """
    Создает отсутствующий профиль для существующих пользователей (legacy поддержка).

    Срабатывает после сохранения объекта User.
    Если профиль отсутствует - создает его в зависимости от роли.
    НЕ сохраняет существующие профили для избежания рекурсии.

    Args:
        sender: Класс модели User (отправитель сигнала)
        instance: Экземпляр обновленного пользователя
        created: True если пользователь только что создан
        **kwargs: Дополнительные аргументы сигнала Django

    Returns:
        None

    Note:
        Этот сигнал ТОЛЬКО создает отсутствующие профили для миграции.
        НЕ пытается сохранить существующие профили (избегаем рекурсии).
    """
    # Пропускаем только что созданных пользователей - для них профиль уже создан
    if created:
        return

    from authentication.models import Admin, Manager, Mentor, Reviewer, Support

    try:
        role_name = instance.role.name if instance.role else "student"

        # ТОЛЬКО создаем отсутствующие профили (для миграции старых данных)
        if role_name == "student" and not hasattr(instance, "student"):
            Student.objects.create(user=instance)
            logger.warning(f"Создан отсутствующий профиль Student для {instance.email}")
        elif role_name == "reviewer" and not hasattr(instance, "reviewer"):
            Reviewer.objects.create(user=instance)
            logger.warning(f"Создан отсутствующий профиль Reviewer для {instance.email}")
        elif role_name == "mentor" and not hasattr(instance, "mentor"):
            Mentor.objects.create(user=instance)
            logger.warning(f"Создан отсутствующий профиль Mentor для {instance.email}")
        elif role_name == "manager" and not hasattr(instance, "manager"):
            Manager.objects.create(user=instance)
            logger.warning(f"Создан отсутствующий профиль Manager для {instance.email}")
        elif role_name == "admin" and not hasattr(instance, "admin"):
            Admin.objects.create(user=instance)
            logger.warning(f"Создан отсутствующий профиль Admin для {instance.email}")
        elif role_name == "support" and not hasattr(instance, "support"):
            Support.objects.create(user=instance)
            logger.warning(f"Создан отсутствующий профиль Support для {instance.email}")
    except Exception as e:
        logger.error(f"Ошибка создания отсутствующего профиля для {instance.email}: {e}")


def subscribe_user_to_notifications(user: Any) -> None:
    """
    Автоматически подписывает пользователя на все типы уведомлений при регистрации.

    Создает подписки для всех типов уведомлений из настроек Student модели:
    - email_notifications (Все email уведомления) - включено
    - course_updates (Обновления курсов) - включено
    - lesson_reminders (Напоминания о уроках) - включено
    - achievement_alerts (Уведомления о достижениях) - включено
    - weekly_summary (Еженедельная сводка) - включено
    - marketing_emails (Маркетинговые письма) - выключено

    Args:
        user: Экземпляр пользователя User

    Returns:
        None

    Example:
        >>> user = User.objects.create_user(email='user@example.com', password='pass')
        >>> subscribe_user_to_notifications(user)
        # Создано 6 подписок (5 активных, 1 неактивная)

    Note:
        Подписки соответствуют полям Student модели для единообразия.
        Пользователь может управлять подписками в настройках дашборда.
    """
    try:
        from notifications.models import Subscription

        # Все типы подписок с дефолтными значениями (как в Student модели)
        subscription_types = [
            ("email_notifications", True),  # По умолчанию включено
            ("course_updates", True),  # По умолчанию включено
            ("lesson_reminders", True),  # По умолчанию включено
            ("achievement_alerts", True),  # По умолчанию включено
            ("weekly_summary", True),  # По умолчанию включено
            ("marketing_emails", False),  # По умолчанию выключено
        ]

        created_count = 0
        for subscription_type, is_active in subscription_types:
            _, created = Subscription.objects.get_or_create(
                email=user.email,
                subscription_type=subscription_type,
                defaults={
                    "is_active": is_active,
                    "preferences": {"source": "auto_registration", "user_id": user.id},
                },
            )
            if created:
                created_count += 1

        logger.info(
            f"Пользователь {user.email} подписан на {created_count} типов уведомлений "
            f"({sum(1 for _, active in subscription_types if active)} активных)"
        )
    except Exception as e:
        logger.error(f"Ошибка подписки пользователя {user.email} на уведомления: {e}")
