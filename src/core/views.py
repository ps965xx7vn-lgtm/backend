"""
Core Views Module - Представления основных страниц платформы Pyland School.

Этот модуль содержит все представления для публичных страниц и основных функций сайта.
Используется стандартный Django request/response цикл с функциональными views.

Представления (Views):
    - home: Главная страница с популярными курсами
    - contacts: Страница контактов с формой обратной связи
    - about: Страница "О нас" с информацией о платформе
    - subscribe: Подписка на email рассылку
    - terms_of_service: Условия использования (юридическая страница)
    - privacy_policy: Политика конфиденциальности (юридическая страница)
    - home_redirect: Умный редирект по ролям пользователей

Особенности:
    - Оптимизированные запросы с annotate/select_related
    - Обработка форм с валидацией (FeedbackForm, SubscriptionForm)
    - Защита от спама и дублирования подписок
    - Flash messages для информирования пользователей
    - Роль-based редиректы для аутентифицированных пользователей

Архитектура:
    - Function-based views (проще и понятнее для базовых страниц)
    - Каждая view имеет полную type-hint аннотацию
    - Логика форм вынесена в forms.py
    - API функционал вынесен в api.py

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging

from django.contrib import messages
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from authentication.decorators import redirect_to_role_dashboard
from courses.models import Course
from managers.models import Feedback
from notifications.models import Subscription

from .cache_utils import cache_about_page, cache_legal_page, cache_page_data
from .forms import FeedbackForm, SubscriptionForm

logger = logging.getLogger(__name__)


# Вспомогательные функции с кешированием данных
@cache_page_data(timeout=300, key_prefix="top_courses")
def get_top_courses():
    """
    Получает топ-4 курса с кешированием (5 минут).

    Returns:
        QuerySet[Course]: Топ-4 курса с наибольшим количеством уроков
    """
    try:
        return list(
            Course.objects.annotate(lessons_count=Count("lessons")).order_by(
                "-lessons_count", "name"
            )[:4]
        )
    except Exception as e:
        logger.error(f"Ошибка при получении топ курсов: {e}")
        return []


@cache_about_page()
def get_about_page_data():
    """
    Получает данные страницы О нас с кешированием (1 час).
    Статическая информация, меняется редко.

    Returns:
        dict: Данные страницы О нас
    """
    return {
        "page_title": "О нас - Pyland",
        "meta_description": "Узнайте больше о Pyland - образовательной платформе для изучения программирования",
        # Можно добавить другие данные если нужно
    }


@cache_legal_page()
def get_terms_page_data():
    """
    Получает данные страницы Terms of Service с кешированием (24 часа).
    Юридические документы меняются очень редко.

    Returns:
        dict: Данные ToS
    """
    return {
        "page_title": "Terms of Service - Pyland",
        "last_updated": "10.11.2025",
    }


@cache_legal_page()
def get_privacy_page_data():
    """
    Получает данные страницы Privacy Policy с кешированием (24 часа).
    Юридические документы меняются очень редко.

    Returns:
        dict: Данные Privacy Policy
    """
    return {
        "page_title": "Privacy Policy - Pyland",
        "last_updated": "10.11.2025",
    }


def home(request: HttpRequest) -> HttpResponse:
    """
    Главная (лендинг) страница сайта - только для неавторизованных пользователей.

    Авторизованные пользователи автоматически перенаправляются на дашборд их роли.

    Отображает:
    - Топ-4 курса с наибольшим количеством уроков
    - Список преимуществ платформы
    - Форму обратной связи (FeedbackForm)

    При POST запросе:
    - Валидирует форму обратной связи
    - Создает запись Feedback в БД
    - Перенаправляет на секцию контактов с сообщением об успехе

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/home.html или редирект на дашборд

    Template context:
        form: FeedbackForm - форма обратной связи
        courses: QuerySet[Course] - топ-4 курса
        features: List[str] - список преимуществ платформы

    Example:
        >>> response = home(request)
        >>> assert 'form' in response.context_data
        >>> assert len(response.context_data['courses']) <= 4
    """
    # Редирект авторизованных пользователей на их дашборд
    if request.user.is_authenticated:
        role_name = getattr(request.user.role, "name", None)
        if role_name == "student":
            return redirect("students:dashboard", user_uuid=request.user.student.id)
        elif role_name == "reviewer":
            return redirect("reviewers:dashboard", user_uuid=request.user.reviewer.id)
        elif role_name in ("mentor", "manager", "admin"):
            # Для ролей без отдельных профилей используем общий редиректор
            return redirect("core:dashboard")
        else:
            # Для пользователей без роли или с неизвестной ролью
            return redirect("students:dashboard", user_uuid=request.user.student.id)

    try:
        if request.method == "POST":
            logger.info(f"POST request received on home page. Data: {request.POST}")
            form = FeedbackForm(request.POST)
            if form.is_valid():
                try:
                    feedback = Feedback.objects.create(
                        first_name=form.cleaned_data["first_name"],
                        phone_number=form.cleaned_data["phone_number"],
                        email=form.cleaned_data["email"],
                        topic=request.POST.get("topic", ""),  # topic может быть пустым на главной
                        message=form.cleaned_data["message"],
                    )
                    logger.info(
                        f"Форма обратной связи отправлена: {form.cleaned_data['email']} "
                        f"(ID: {feedback.id})"
                    )
                    messages.success(
                        request,
                        "Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.",
                    )
                    return redirect("core:home")
                except Exception as e:
                    logger.error(f"Ошибка при создании заявки обратной связи: {e}", exc_info=True)
                    messages.error(
                        request,
                        "Произошла ошибка при отправке сообщения. Попробуйте позже.",
                    )
            else:
                logger.warning(f"Ошибка валидации формы обратной связи: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = FeedbackForm()

        # Получаем реальные курсы из базы данных с кешированием
        courses = get_top_courses()

        features = [
            "Практические проекты",
            "Поддержка менторов",
            "Онлайн-сообщество",
            "Реальные кейсы",
            "Сертификаты",
            "Гибкий график",
        ]
        return render(
            request,
            "core/home.html",
            {"form": form, "courses": courses, "features": features},
        )
    except Exception as e:
        logger.error(f"Критическая ошибка на главной странице: {e}")
        messages.error(request, "Произошла ошибка. Пожалуйста, попробуйте позже.")
        return render(
            request,
            "core/home.html",
            {"form": FeedbackForm(), "courses": [], "features": []},
        )


@redirect_to_role_dashboard
def dashboard_redirect(request: HttpRequest) -> HttpResponse:
    """
    Роутер для /dashboard/ - перенаправляет пользователей в их дашборды по ролям.

    Неавторизованные пользователи → signin
    Student → students:dashboard
    Manager/Admin → managers:dashboard
    Reviewer → reviewers:dashboard
    Mentor → mentors:dashboard

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с редиректом на соответствующий dashboard
    """
    # Декоратор @redirect_to_role_dashboard сделает всю работу
    pass


def contacts(request: HttpRequest) -> HttpResponse:
    """
    Страница контактов с формой обратной связи.

    Отображает контактную информацию компании и форму для отправки сообщений.

    При POST запросе:
    - Валидирует FeedbackForm
    - Сохраняет сообщение в БД
    - Показывает success message
    - Редиректит на ту же страницу

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/contacts.html

    Template context:
        form: FeedbackForm - форма обратной связи

    Example:
        >>> response = contacts(request)
        >>> assert response.status_code == 200
        >>> assert 'form' in response.context_data
    """
    try:
        if request.method == "POST":
            form = FeedbackForm(request.POST)
            if form.is_valid():
                try:
                    Feedback.objects.create(
                        first_name=form.cleaned_data["first_name"],
                        phone_number=form.cleaned_data["phone_number"],
                        email=form.cleaned_data["email"],
                        topic=form.cleaned_data.get("topic", ""),
                        message=form.cleaned_data["message"],
                    )
                    logger.info(f"Контактная форма отправлена: {form.cleaned_data['email']}")
                    messages.success(request, "Ваше сообщение отправлено!")
                    return redirect("core:contacts")
                except Exception as e:
                    logger.error(f"Ошибка при создании контактного сообщения: {e}")
                    messages.error(
                        request,
                        "Произошла ошибка при отправке. Попробуйте позже.",
                    )
            else:
                logger.warning(f"Ошибка валидации контактной формы: {form.errors}")
                # Показываем ошибки валидации пользователю
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = FeedbackForm()
        return render(request, "core/contacts.html", {"form": form})
    except Exception as e:
        logger.error(f"Критическая ошибка на странице контактов: {e}")
        messages.error(request, "Произошла ошибка. Пожалуйста, попробуйте позже.")
        return render(request, "core/contacts.html", {"form": FeedbackForm()})


def about(request: HttpRequest) -> HttpResponse:
    """
    Страница "О нас" с информацией о компании и команде - только для неавторизованных.

    Авторизованные пользователи автоматически перенаправляются на дашборд их роли.

    Отображает:
    - Миссию и видение компании
    - Историю создания
    - Команду преподавателей
    - Достижения и статистику

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/about.html или редирект на дашборд

    Example:
        >>> response = about(request)
        >>> assert response.status_code == 200
    """
    # Редирект авторизованных пользователей на их дашборд
    if request.user.is_authenticated:
        role_name = getattr(request.user.role, "name", None)
        if role_name == "student":
            return redirect("students:dashboard", user_uuid=request.user.student.id)
        elif role_name == "reviewer":
            return redirect("reviewers:dashboard", user_uuid=request.user.reviewer.id)
        elif role_name in ("mentor", "manager", "admin"):
            # Для ролей без отдельных профилей используем общий редиректор
            return redirect("core:dashboard")
        else:
            return redirect("students:dashboard", user_uuid=request.user.student.id)

    return render(request, "core/about.html")


def subscribe(request: HttpRequest) -> HttpResponse:
    """
    Обработчик подписки на email рассылку.

    Принимает POST запрос с email адресом и создает/обновляет подписку.
    Используется для newsletter подписок из футера или других мест сайта.

    При POST запросе:
    - Валидирует SubscriptionForm
    - Создает или получает существующую подписку
    - Показывает соответствующее сообщение (success/info)
    - Редиректит обратно на предыдущую страницу

    Args:
        request: HttpRequest объект Django (ожидается POST)

    Returns:
        HttpResponse редирект на страницу, откуда пришел запрос (HTTP_REFERER)
        или на главную если referer отсутствует

    Example:
        >>> # В шаблоне footer
        >>> <form method="post" action="{% url 'core:subscribe' %}">
        >>>     {% csrf_token %}
        >>>     <input type="email" name="email">
        >>>     <button type="submit">Подписаться</button>
        >>> </form>
    """
    try:
        if request.method == "POST":
            form = SubscriptionForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                try:
                    subscription, created = Subscription.subscribe(
                        email=email, subscription_type="email_notifications"
                    )
                    if created:
                        logger.info(f"Новая подписка на рассылку: {email}")
                        messages.success(request, "Вы успешно подписались!")
                    else:
                        logger.warning(f"Попытка повторной подписки: {email}")
                        messages.info(request, "Вы уже подписаны.")
                except Exception as e:
                    logger.error(f"Ошибка при создании подписки: {e}")
                    messages.error(
                        request,
                        "Произошла ошибка при подписке. Попробуйте позже.",
                    )
            else:
                logger.warning(f"Ошибка валидации формы подписки: {form.errors}")
                messages.error(request, "Введите корректный email.")
        else:
            logger.error("Неверный метод запроса для подписки")
    except Exception as e:
        logger.error(f"Критическая ошибка при обработке подписки: {e}")
        messages.error(request, "Произошла ошибка. Попробуйте позже.")

    return redirect(request.headers.get("referer", "/"))


def terms_of_service(request: HttpRequest) -> HttpResponse:
    """
    Страница с условиями использования сервиса (Terms of Service).

    Отображает юридический документ с правилами и условиями использования
    онлайн-платформы Pyland.

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/legal/terms_of_service.html

    Example:
        >>> response = terms_of_service(request)
        >>> assert response.status_code == 200
        >>> assert 'Terms of Service' in response.content.decode()
    """
    return render(request, "core/legal/terms-of-service.html")


def privacy_policy(request: HttpRequest) -> HttpResponse:
    """
    Страница с политикой конфиденциальности (Privacy Policy).

    Отображает юридический документ о сборе, использовании и защите
    персональных данных пользователей.

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/legal/privacy_policy.html

    Example:
        >>> response = privacy_policy(request)
        >>> assert response.status_code == 200
        >>> assert 'Privacy Policy' in response.content.decode()
    """
    return render(request, "core/legal/privacy-policy.html")


def data_processing(request: HttpRequest) -> HttpResponse:
    """
    Страница с согласием на обработку персональных данных.

    Отображает юридический документ о согласии пользователя на обработку
    персональных данных в соответствии с 152-ФЗ.

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/legal/data_processing.html

    Example:
        >>> response = data_processing(request)
        >>> assert response.status_code == 200
    """
    return render(request, "core/legal/data-processing.html")


def refund_policy(request: HttpRequest) -> HttpResponse:
    """
    Страница с политикой возвратов (Refund Policy).
    """
    return render(request, "core/legal/refund-policy.html")


def cookies_policy(request: HttpRequest) -> HttpResponse:
    """
    Страница с политикой использования cookie (Cookies Policy).
    """
    return render(request, "core/legal/cookies-policy.html")


def public_offer(request: HttpRequest) -> HttpResponse:
    """
    Страница с публичной офертой (Public Offer).

    Отображает юридический документ с официальным предложением заключить
    договор на оказание образовательных услуг в соответствии с законодательством Грузии.

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/legal/public-offer.html
    """
    return render(request, "core/legal/public-offer.html")


def payment_policy(request: HttpRequest) -> HttpResponse:
    """
    Страница с правилами оплаты (Payment Policy).

    Отображает политику оплаты образовательных услуг, включая способы оплаты,
    процесс платежа и безопасность транзакций.

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/legal/payment-policy.html
    """
    return render(request, "core/legal/payment-policy.html")


def platform_rules(request: HttpRequest) -> HttpResponse:
    """
    Страница с правилами использования платформы (Platform Rules).

    Отображает правила поведения на платформе, запрещенные действия,
    санкции за нарушения и процедуру апелляции.

    Args:
        request: HttpRequest объект Django

    Returns:
        HttpResponse с отрендеренным шаблоном core/legal/platform-rules.html
    """
    return render(request, "core/legal/platform-rules.html")
