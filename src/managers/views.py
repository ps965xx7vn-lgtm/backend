"""
Manager Views Module - Django views для административной панели.

Этот модуль предоставляет веб-интерфейс для управления платформой.
Все views требуют прав администратора (@staff_member_required).

Views:
    - manager_dashboard: Главная страница dashboard со статистикой
    - feedback_list: Список всех обращений
    - feedback_detail: Детальный просмотр обращения
    - feedback_delete: Удаление обращения
    - system_logs: Просмотр системных логов
    - system_settings: Управление настройками системы

Особенности:
    - Все views защищены @staff_member_required
    - Кеширование статистики для быстрой загрузки
    - Пагинация списков
    - Фильтрация данных через формы
    - Breadcrumbs для навигации
    - Responsive дизайн

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .cache_utils import get_cached_feedback_stats
from .forms import FeedbackFilterForm
from .models import Feedback, SystemLog, SystemSettings

User = get_user_model()
logger = logging.getLogger(__name__)

# ============================================================================
# DASHBOARD - Главная страница административной панели
# ============================================================================


@staff_member_required
def manager_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Главная страница административной панели (Dashboard).

    Отображает общую статистику платформы:
        - Статистика по обратной связи (всего, необработанных, за сегодня)
        - Последние 5 обращений
        - Статистика по пользователям (всего, активных, новых)
        - Статистика по контенту (статьи, курсы, комментарии)
        - Последние 10 системных логов
        - Быстрые ссылки на основные разделы

    Args:
        request: HTTP запрос от пользователя

    Returns:
        HttpResponse с отрендеренным шаблоном dashboard

    Template:
        managers/dashboard.html

    Context:
        - stats: Словарь со всей статистикой
        - recent_feedback: QuerySet последних обращений
        - recent_logs: QuerySet последних логов
        - user_stats: Статистика по пользователям
        - content_stats: Статистика по контенту

    Примечание:
        Использует кеширование для статистики (TTL 5 минут)
    """
    # Получаем кешированную статистику по feedback
    feedback_stats = get_cached_feedback_stats()

    # Последние 5 обращений
    recent_feedback = Feedback.objects.select_related("processed_by").order_by("-registered_at")[:5]

    # Последние 10 системных логов
    recent_logs = SystemLog.objects.select_related("user").order_by("-created_at")[:10]

    # Статистика по пользователям (если есть доступ к модели User)
    try:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        user_stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "new_users_week": User.objects.filter(date_joined__gte=week_ago).count(),
            "staff_users": User.objects.filter(is_staff=True).count(),
        }
    except Exception as e:
        logger.warning(f"Ошибка получения статистики пользователей: {e}")
        user_stats = {
            "total_users": 0,
            "active_users": 0,
            "new_users_week": 0,
            "staff_users": 0,
        }

    # Статистика по контенту (blog, courses если есть)
    content_stats = {}
    try:
        from blog.models import Article, Comment

        content_stats["articles"] = Article.objects.count()
        content_stats["published_articles"] = Article.objects.filter(status="published").count()
        content_stats["comments"] = Comment.objects.count()
    except ImportError:
        pass

    try:
        from courses.models import Course

        content_stats["courses"] = Course.objects.count()
    except ImportError:
        pass

    # Системные настройки
    try:
        settings_count = SystemSettings.objects.count()
        public_settings = SystemSettings.objects.filter(is_public=True).count()
    except Exception as e:
        logger.warning(f"Ошибка получения настроек: {e}")
        settings_count = 0
        public_settings = 0

    context = {
        "feedback_stats": feedback_stats,
        "recent_feedback": recent_feedback,
        "recent_logs": recent_logs,
        "user_stats": user_stats,
        "content_stats": content_stats,
        "settings_count": settings_count,
        "public_settings": public_settings,
        "page_title": "Dashboard",
    }

    return render(request, "managers/dashboard.html", context)


# ============================================================================
# FEEDBACK MANAGEMENT - Управление обратной связью
# ============================================================================


@staff_member_required
def feedback_list(request: HttpRequest) -> HttpResponse:
    """
    Список всех обращений обратной связи с фильтрацией.

    Поддерживает фильтрацию по:
        - Поиск по имени, email, телефону, сообщению
        - Дата от/до
        - Статус обработки
        - Обработавший администратор

    Args:
        request: HTTP запрос (GET параметры для фильтрации)

    Returns:
        HttpResponse с отрендеренным списком

    Template:
        managers/feedback_list.html

    Context:
        - feedback_list: Paginator page с обращениями
        - filter_form: Форма фильтрации
        - total_count: Общее количество записей

    Query Parameters:
        - search: Текст для поиска
        - date_from: Дата начала (YYYY-MM-DD)
        - date_to: Дата окончания (YYYY-MM-DD)
        - is_processed: Статус обработки (true/false)
        - page: Номер страницы для пагинации
    """
    # Получаем все обращения
    feedback_qs = Feedback.objects.select_related("processed_by").order_by("-registered_at")

    # Применяем фильтры из формы
    filter_form = FeedbackFilterForm(request.GET or None)

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        is_processed = filter_form.cleaned_data.get("is_processed")

        if search:
            feedback_qs = feedback_qs.filter(
                Q(first_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(message__icontains=search)
            )

        if date_from:
            feedback_qs = feedback_qs.filter(registered_at__gte=date_from)

        if date_to:
            # Добавляем 1 день для включения записей до конца дня
            date_to_end = datetime.combine(date_to, datetime.max.time())
            feedback_qs = feedback_qs.filter(registered_at__lte=date_to_end)

        if is_processed is not None:
            feedback_qs = feedback_qs.filter(is_processed=is_processed)

    # Пагинация
    paginator = Paginator(feedback_qs, 25)  # 25 записей на страницу
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "feedback_list": page_obj,
        "filter_form": filter_form,
        "total_count": paginator.count,
        "page_title": "Обратная связь",
    }

    return render(request, "managers/feedback_list.html", context)


@staff_member_required
def feedback_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Детальный просмотр и обработка обращения.

    Позволяет:
        - Просмотреть полную информацию об обращении
        - Отметить как обработанное/необработанное
        - Добавить заметки администратора
        - Просмотреть историю обработки

    Args:
        request: HTTP запрос
        pk: ID обращения

    Returns:
        HttpResponse с детальной информацией
        GET: Отображение формы
        POST: Обработка обновления статуса и заметок

    Template:
        managers/feedback_detail.html

    Context:
        - feedback: Объект Feedback
        - form: Форма для редактирования заметок

    POST Parameters:
        - action: 'mark_processed' или 'mark_unprocessed'
        - admin_notes: Текст заметок администратора
    """
    feedback = get_object_or_404(Feedback.objects.select_related("processed_by"), pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "mark_processed":
            feedback.is_processed = True
            feedback.processed_by = request.user
            feedback.processed_at = timezone.now()
            messages.success(request, "Обращение отмечено как обработанное.")

        elif action == "mark_unprocessed":
            feedback.is_processed = False
            feedback.processed_by = None
            feedback.processed_at = None
            messages.info(request, "Обращение отмечено как необработанное.")

        # Сохраняем заметки администратора
        admin_notes = request.POST.get("admin_notes", "").strip()
        if admin_notes:
            feedback.admin_notes = admin_notes

        feedback.save()

        # Логируем действие
        SystemLog.objects.create(
            level="INFO",
            action_type="FEEDBACK_PROCESSED" if action == "mark_processed" else "FEEDBACK_UPDATED",
            user=request.user,
            message=f"Обращение #{feedback.id} обработано пользователем {request.user.username}",
            details={
                "feedback_id": feedback.id,
                "action": action,
                "has_notes": bool(admin_notes),
            },
        )

        return redirect("manager:feedback_detail", pk=pk)

    context = {
        "feedback": feedback,
        "page_title": f"Обращение #{feedback.id}",
    }

    return render(request, "managers/feedback_detail.html", context)


@staff_member_required
def feedback_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаление обращения обратной связи.

    Args:
        request: HTTP запрос (только POST)
        pk: ID обращения для удаления

    Returns:
        HttpResponse: Редирект на список после удаления

    Security:
        - Только POST метод
        - Требует подтверждения
        - Логирует удаление в SystemLog

    Примечание:
        Перед удалением создается запись в SystemLog для аудита.
    """
    feedback = get_object_or_404(Feedback, pk=pk)

    if request.method == "POST":
        # Логируем удаление
        SystemLog.objects.create(
            level="WARNING",
            action_type="FEEDBACK_DELETED",
            user=request.user,
            message=f"Обращение #{feedback.id} от {feedback.email} удалено",
            details={
                "feedback_id": feedback.id,
                "email": feedback.email,
                "name": feedback.first_name,
                "deleted_by": request.user.username,
            },
        )

        feedback.delete()
        messages.success(request, f"Обращение #{pk} успешно удалено.")
        return redirect("manager:feedback_list")

    context = {
        "feedback": feedback,
        "page_title": "Подтверждение удаления",
    }

    return render(request, "managers/feedback_confirm_delete.html", context)


# ============================================================================
# SYSTEM LOGS - Просмотр системных логов
# ============================================================================


@staff_member_required
def system_logs(request: HttpRequest) -> HttpResponse:
    """
    Просмотр системных логов с фильтрацией.

    Позволяет просматривать и фильтровать системные события:
        - По уровню (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - По типу действия (LOGIN, LOGOUT, CREATE, UPDATE, DELETE и т.д.)
        - По пользователю
        - По дате
        - По поисковому запросу

    Args:
        request: HTTP запрос (GET параметры для фильтрации)

    Returns:
        HttpResponse с отрендеренным списком логов

    Template:
        managers/system_logs.html

    Context:
        - logs: Paginator page с логами
        - level_choices: Доступные уровни логирования
        - action_choices: Доступные типы действий
        - total_count: Общее количество записей

    Query Parameters:
        - level: Уровень лога (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        - action_type: Тип действия
        - user_id: ID пользователя
        - date_from: Дата начала
        - date_to: Дата окончания
        - search: Поиск по сообщению
        - page: Номер страницы
    """
    logs_qs = SystemLog.objects.select_related("user").order_by("-created_at")

    # Фильтрация
    level = request.GET.get("level")
    action_type = request.GET.get("action_type")
    user_id = request.GET.get("user_id")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    search = request.GET.get("search")

    if level:
        logs_qs = logs_qs.filter(level=level)

    if action_type:
        logs_qs = logs_qs.filter(action_type=action_type)

    if user_id:
        logs_qs = logs_qs.filter(user_id=user_id)

    if date_from:
        logs_qs = logs_qs.filter(created_at__gte=date_from)

    if date_to:
        logs_qs = logs_qs.filter(created_at__lte=date_to)

    if search:
        logs_qs = logs_qs.filter(Q(message__icontains=search) | Q(ip_address__icontains=search))

    # Пагинация
    paginator = Paginator(logs_qs, 50)  # 50 записей на страницу
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "logs": page_obj,
        "level_choices": SystemLog.LOG_LEVELS,
        "action_choices": SystemLog.ACTION_TYPES,
        "total_count": paginator.count,
        "page_title": "Системные логи",
    }

    return render(request, "managers/system_logs.html", context)


# ============================================================================
# SYSTEM SETTINGS - Управление настройками системы
# ============================================================================


@staff_member_required
def system_settings(request: HttpRequest) -> HttpResponse:
    """
    Управление настройками системы.

    Позволяет просматривать и редактировать настройки платформы:
        - Общие настройки (название сайта, email и т.д.)
        - Настройки безопасности
        - Настройки интеграций (email, соц. сети)
        - Feature flags
        - API ключи

    Args:
        request: HTTP запрос
        GET: Отображение списка настроек
        POST: Обновление значений настроек

    Returns:
        HttpResponse с формой настроек

    Template:
        managers/system_settings.html

    Context:
        - settings_list: QuerySet всех настроек
        - grouped_settings: Настройки сгруппированные по категориям

    POST Parameters:
        - setting_{id}: Новое значение для настройки с ID={id}

    Примечание:
        Изменения логируются в SystemLog для аудита.
    """
    settings_qs = SystemSettings.objects.all().order_by("key")

    if request.method == "POST":
        # Обработка обновления настроек
        updated_count = 0

        for setting in settings_qs:
            new_value = request.POST.get(f"setting_{setting.id}")

            if new_value is not None and new_value != setting.value:
                old_value = setting.value
                setting.value = new_value
                setting.updated_by = request.user
                setting.save()

                updated_count += 1

                # Логируем изменение
                SystemLog.objects.create(
                    level="INFO",
                    action_type="SETTING_UPDATE",
                    user=request.user,
                    message=f"Настройка {setting.key} изменена",
                    details={
                        "setting_key": setting.key,
                        "old_value": old_value,
                        "new_value": new_value,
                    },
                )

        if updated_count > 0:
            messages.success(request, f"Обновлено настроек: {updated_count}")
        else:
            messages.info(request, "Нет изменений для сохранения.")

        return redirect("manager:system_settings")

    # Группируем настройки по префиксу ключа
    grouped_settings = {}
    for setting in settings_qs:
        prefix = setting.key.split("_")[0] if "_" in setting.key else "general"
        if prefix not in grouped_settings:
            grouped_settings[prefix] = []
        grouped_settings[prefix].append(setting)

    context = {
        "settings_list": settings_qs,
        "grouped_settings": grouped_settings,
        "page_title": "Настройки системы",
    }

    return render(request, "managers/system_settings.html", context)
