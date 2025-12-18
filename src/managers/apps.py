"""
Manager Application Configuration - Конфигурация административного приложения.

Этот модуль определяет конфигурацию Django приложения для административной панели.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django.apps import AppConfig


class ManagerConfig(AppConfig):
    """
    Конфигурация приложения Manager.

    Настройки:
        - default_auto_field: BigAutoField для первичных ключей
        - name: Имя приложения 'managers'
        - verbose_name: Человекочитаемое имя для admin
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "managers"
    verbose_name = "Административная панель"
