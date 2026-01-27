"""
Pyland School Platform

Онлайн-платформа для обучения программированию с полным функционалом LMS.

Основные приложения:
    authentication - Система аутентификации и управления пользователями
    core - Основные страницы платформы и контекстные процессоры
    blog - Полнофункциональный блог со статьями и комментариями
    students - Личный кабинет студента
    courses - Управление курсами, уроками и шагами
    reviewers - Система проверки работ студентов
    mentors - Управление менторами
    managers - Административная панель
    payments - Обработка платежей
    certificates - Генерация сертификатов
    notifications - Система уведомлений (email, SMS, Telegram)
    support - Техническая поддержка

Технологический стек:
    - Django 5.2.3
    - Django Ninja 1.4.3 (REST API)
    - Python 3.13+
    - PostgreSQL (основная БД)
    - Redis (кеширование и Celery broker)
    - Celery 5.5.3 (асинхронные задачи)
    - Pydantic 2.11.7 (валидация)
    - Poetry (управление зависимостями)

Дополнительно:
    - JWT аутентификация (ninja-jwt)
    - Social Auth (django-social-auth)
    - Логирование (loguru)
    - Мониторинг (Sentry)

Версия: 1.0.0
Автор: Pyland Team
Дата: 2025
"""

# Celery setup
from .celery import app as celery_app

__all__ = ("celery_app",)
