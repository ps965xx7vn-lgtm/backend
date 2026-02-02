"""
Auth Views Module - Django views для аутентификации.

Этот модуль содержит все представления для работы с аутентификацией:

Аутентификация:
    - signin_view: Вход пользователя (GET/POST)
    - signup_view: Регистрация нового пользователя (GET/POST)
    - user_logout: Выход из системы
    - verify_email_confirm: Подтверждение email по токену
    - resend_verification_email: Повторная отправка письма верификации

Восстановление пароля:
    - password_reset_view: Запрос сброса пароля (GET/POST)
    - password_reset_confirm: Установка нового пароля по токену (GET/POST)

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .forms import PasswordResetForm, SetPasswordForm, UserLoginForm, UserRegisterForm
from .tasks import send_verification_email, send_verification_email_sync

User = get_user_model()
logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@csrf_protect
@never_cache
def signin_view(request: HttpRequest) -> HttpResponse:
    """
    Вход пользователя в систему через email и пароль.

    Обрабатывает аутентификацию пользователя с проверкой подтверждения email.
    Поддерживает перенаправление на next URL после успешного входа.
    Авторизованные пользователи автоматически перенаправляются на главную.

    Args:
        request: HTTP запрос Django (GET для отображения формы, POST для входа)

    Returns:
        HttpResponse:
            - GET: Рендерит форму входа account/auth/signin.html
            - POST успешно: Redirect на next URL или /
            - POST ошибка: Рендерит форму с сообщением об ошибке

    Template Context:
        form: UserLoginForm instance
        next: URL для перенаправления после входа (из GET/POST параметра)

    Validation:
        - Проверяет email и пароль через UserLoginForm
        - Проверяет user.email_is_verified перед входом
        - Показывает ссылку на повторную отправку email если не подтвержден

    Example:
        GET /account/signin?next=/courses/python
        POST /account/signin
        {
            "email": "user@example.com",
            "password": "SecurePass123",
            "next": "/dashboard"
        }

        → Redirect to /dashboard если email подтвержден
        → Ошибка с ссылкой на resend_verification если не подтвержден
    """
    # Редирект авторизованных пользователей на их dashboard
    if request.user.is_authenticated:
        logger.info(f"Авторизованный пользователь {request.user.email} перенаправлен с signin")
        role_name = request.user.role.name if request.user.role else None

        if role_name == "manager" and hasattr(request.user, "manager"):
            return redirect(
                reverse("managers:dashboard", kwargs={"user_uuid": request.user.manager.id})
            )
        elif role_name == "student" and hasattr(request.user, "student"):
            return redirect(
                reverse("students:dashboard", kwargs={"user_uuid": request.user.student.id})
            )
        elif role_name == "reviewer" and hasattr(request.user, "reviewer"):
            return redirect(
                reverse("reviewers:dashboard", kwargs={"user_uuid": request.user.reviewer.id})
            )
        return redirect("/")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me", False)
            user = authenticate(email=email, password=password)
            if user:
                if user.email_is_verified:
                    login(request, user)
                    logger.info(f"Пользователь успешно вошел: {email}")
                    # Если пользователь не выбрал "Запомнить меня", сессия истечет при закрытии браузера
                    if not remember_me:
                        request.session.set_expiry(0)
                    # Если выбрал "Запомнить меня", сессия будет храниться 2 недели (по умолчанию в settings)

                    # Умный редирект на основе роли пользователя
                    if not next_url or next_url == "/":
                        role_name = user.role.name if user.role else None

                        if role_name == "manager" and hasattr(user, "manager"):
                            # Менеджеры идут на свой dashboard
                            next_url = reverse(
                                "managers:dashboard", kwargs={"user_uuid": user.manager.id}
                            )
                            logger.info(f"Redirecting {email} (manager) to managers dashboard")
                        elif role_name == "student" and hasattr(user, "student"):
                            # Студенты идут на свой dashboard
                            next_url = reverse(
                                "students:dashboard", kwargs={"user_uuid": user.student.id}
                            )
                            logger.info(f"Redirecting {email} (student) to student dashboard")
                        elif role_name == "reviewer" and hasattr(user, "reviewer"):
                            # Ревьюеры идут на свой dashboard
                            next_url = reverse(
                                "reviewers:dashboard", kwargs={"user_uuid": user.reviewer.id}
                            )
                            logger.info(f"Redirecting {email} (reviewer) to reviewer dashboard")
                        else:
                            # По умолчанию на главную
                            next_url = "/"

                    return redirect(next_url)
                else:
                    logger.warning(f"Попытка входа с неподтвержденным email: {email}")
                    resend_url = reverse("authentication:resend_verification_email")
                    messages.error(
                        request,
                        mark_safe(  # nosec B703 B308 - trusted URL from reverse()
                            _(
                                'Ваш email не подтвержден. <a href="{url}">Отправить письмо повторно</a>'
                            ).format(url=resend_url)
                        ),
                    )
            else:
                messages.error(request, _("Email или пароль введен неверно."))
    else:
        form = UserLoginForm()

    return render(request, "auth/auth/signin.html", {"form": form, "next": next_url})


@require_http_methods(["GET", "POST"])
@csrf_protect
@never_cache
@transaction.atomic
def signup_view(request: HttpRequest) -> HttpResponse:
    """
    Регистрация нового пользователя с отправкой письма подтверждения email.

    Создает User с уникальным username (UUID), Profile через сигнал,
    и отправляет письмо с ссылкой активации через Celery или синхронно (fallback).
    Авторизованные пользователи автоматически перенаправляются на главную.

    Args:
        request: HTTP запрос Django (GET для формы, POST для регистрации)

    Returns:
        HttpResponse:
            - GET: Рендерит форму регистрации account/auth/signup.html
            - POST успешно: Redirect на signin с сообщением о письме
            - POST ошибка: Рендерит форму с ошибками валидации

    Template Context:
        form: UserRegisterForm instance

    Process Flow:
        1. Валидация формы (email уникальность, пароль сложность, телефон)
        2. Создание User с username=uuid4() внутри транзакции
        3. Генерация токена подтверждения и activation URL
        4. Попытка отправки email через Celery task
        5. Fallback на синхронную отправку если Celery недоступен
        6. Откат транзакции если отправка email не удалась

    Raises:
        Exception: Откатывает транзакцию если не удалось отправить email

    Example:
        POST /account/signup
        {
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "confirm_password": "SecurePass123",
            "first_name": "Ivan",
            "phone_number": "+79991234567",
            "agree_to_terms": true
        }

        → Создается User и Profile
        → Отправляется email с /account/verify-email-confirm/{uidb64}/{token}/
        → Redirect на signin с сообщением "Подтвердите email"
    """
    # Редирект авторизованных пользователей
    if request.user.is_authenticated:
        logger.info(f"Авторизованный пользователь {request.user.email} перенаправлен с signup")
        return redirect("/")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Создаем пользователя (транзакция управляется декоратором)
                user = form.save(commit=False)
                user.username = str(uuid.uuid4())[:30]
                password = form.cleaned_data.get("password")
                user.set_password(password)
                user.save()

                # Сохраняем номер телефона в профиль Student
                phone_number = form.cleaned_data.get("phone_number")
                if phone_number:
                    user.student.phone = phone_number
                    user.student.save()
                    logger.info(f"Номер телефона сохранен для {user.email}: {phone_number}")

                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                activation_url = request.build_absolute_uri(
                    reverse(
                        "authentication:verify_email_confirm",
                        kwargs={"uidb64": uidb64, "token": token},
                    )
                )

                # Email верификация обязательна для всех пользователей
                # Попытка отправить email через Celery, при ошибке - синхронно
                try:
                    send_verification_email.delay(
                        user.id,
                        activation_url,
                        _("Активируйте ваш аккаунт."),
                        "auth/email/email-verification.html",
                    )
                    logger.info(f"Email верификации добавлен в очередь для {user.email}")
                except Exception as celery_error:
                    logger.warning(
                        f"Celery недоступен, переключаемся на синхронную отправку: {celery_error}"
                    )
                    # Fallback на синхронную отправку email если Celery недоступен
                    try:
                        send_verification_email_sync(
                            user.id,
                            activation_url,
                            _("Активируйте ваш аккаунт."),
                            "auth/email/email-verification.html",
                        )
                        logger.info(f"Email верификации отправлен синхронно для {user.email}")
                    except Exception as sync_error:
                        logger.error(
                            f"Ошибка отправки email при регистрации пользователю {user.email}: {sync_error}"
                        )
                        messages.error(
                            request,
                            _("Ошибка отправки письма подтверждения. Попробуйте позже."),
                        )
                        raise sync_error  # Это откатит транзакцию

                # Успешная регистрация
                success_message = _("Регистрация успешна! Проверьте ваш email для подтверждения.")
                messages.success(request, success_message)
                return redirect("authentication:signin")

            except Exception:
                # Если что-то пошло не так, пользователь не будет создан
                messages.error(request, _("Произошла ошибка при регистрации. Попробуйте еще раз."))
    else:
        form = UserRegisterForm()

    return render(request, "auth/auth/signup.html", {"form": form})


@require_http_methods(["GET"])
@never_cache
@transaction.atomic
def verify_email_confirm(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """
    Подтверждение email адреса пользователя по токену из письма.

    Декодирует uidb64 для получения user ID, проверяет токен,
    и устанавливает email_is_verified=True если токен валидный.

    Args:
        request: HTTP запрос Django
        uidb64: Base64 закодированный user.pk из urlsafe_base64_encode()
        token: Одноразовый токен из default_token_generator.make_token()

    Returns:
        HttpResponse:
            - Успех: Redirect на signin с сообщением "Email подтвержден"
            - Ошибка: Рендер account/auth/email-verification-confirm.html с warning

    Flow:
        1. Декодируем uidb64 → user.pk
        2. Получаем User из БД
        3. Проверяем токен через default_token_generator.check_token()
        4. Если токен валидный: устанавливаем email_is_verified=True
        5. Если токен невалидный/истек: показываем предупреждение

    Example:
        GET /account/verify-email-confirm/MjM=/6c8-abc123def456/

        → Если токен валиден: user.email_is_verified = True, redirect на signin
        → Если токен истек: "Ссылка недействительна", показываем форму повторной отправки
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.warning(f"Невалидная ссылка верификации email: {e}")
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_is_verified = True
        user.save(update_fields=["email_is_verified"])
        logger.info(f"Email успешно подтвержден для пользователя: {user.email}")
        messages.success(request, _("Ваш email успешно подтвержден. Вы можете войти в систему."))
        return redirect("authentication:signin")

    logger.warning(f"Invalid or expired email verification token for uidb64: {uidb64}")
    messages.warning(request, _("Ссылка недействительна."))
    return render(request, "auth/auth/email-verification-confirm.html")


@require_http_methods(["GET", "POST"])
@csrf_protect
@never_cache
def password_reset_view(request: HttpRequest) -> HttpResponse:
    """
    Представление для запроса сброса пароля по email.

    POST:
        - Отправляет email с инструкциями по сбросу пароля.
    GET:
        - Отображает форму запроса сброса пароля.
    """
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)

            if users.exists():
                for user in users:
                    token = default_token_generator.make_token(user)
                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    reset_url = request.build_absolute_uri(
                        reverse(
                            "authentication:password_reset_confirm",
                            kwargs={"uidb64": uidb64, "token": token},
                        )
                    )

                    # Попытка отправить email через Celery, при ошибке - синхронно
                    email_sent = False
                    try:
                        send_verification_email.delay(
                            user.id,
                            reset_url,
                            _("Инструкция по сбросу пароля"),
                            "auth/email/password-reset.html",
                        )
                        email_sent = True
                    except Exception as celery_error:
                        logger.warning(
                            f"Celery недоступен, переключаемся на синхронную отправку при сбросе пароля: {celery_error}"
                        )

                        try:
                            send_verification_email_sync(
                                user.id,
                                reset_url,
                                _("Инструкция по сбросу пароля"),
                                "auth/email/password-reset.html",
                            )
                            email_sent = True
                        except Exception as sync_error:
                            logger.error(
                                f"Ошибка отправки email для сброса пароля пользователю {user.email}: {sync_error}"
                            )
                            messages.error(
                                request,
                                _("Произошла ошибка при отправке письма. Попробуйте позже."),
                            )
                            return redirect("authentication:password_reset")

                    if not email_sent:
                        messages.error(
                            request, _("Произошла ошибка при отправке письма. Попробуйте позже.")
                        )
                        return redirect("authentication:password_reset")

                messages.success(request, _("Инструкции по сбросу пароля отправлены на ваш email."))
            else:
                messages.warning(request, _("Пользователь с таким email не найден."))
            return redirect("authentication:password_reset")
    else:
        form = PasswordResetForm()

    return render(request, "auth/password-reset/form.html", {"form": form})


@require_http_methods(["GET", "POST"])
@csrf_protect
@never_cache
@transaction.atomic
def password_reset_confirm(request, uidb64: str, token: str) -> Any:
    """
    Подтверждение сброса пароля.

    :param uidb64: base64 закодированный pk пользователя
    :param token: токен сброса пароля
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.warning(f"Невалидная ссылка сброса пароля: {e}")
        user = None

    validlink = False
    if user and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                logger.info(f"Пароль успешно сброшен для пользователя: {user.email}")
                messages.success(
                    request, _("Пароль успешно изменен. Теперь вы можете войти с новым паролем.")
                )
                return redirect("authentication:signin")
        else:
            form = SetPasswordForm(user)

        return render(
            request,
            "auth/password-reset/confirm.html",
            {"form": form, "validlink": validlink},
        )

    # Если ссылка недействительна
    logger.warning(f"Невалидный или истекший токен сброса пароля для uidb64: {uidb64}")
    return render(
        request,
        "auth/password-reset/confirm.html",
        {"validlink": validlink},
    )


@require_http_methods(["GET", "POST"])
@csrf_protect
@never_cache
def resend_verification_email(request: HttpRequest) -> HttpResponse:
    """
    Повторная отправка письма с подтверждением email адреса.

    Генерирует новый токен и отправляет письмо если email не подтвержден.
    Защищает от спама проверкой существования пользователя и статуса верификации.

    Args:
        request: HTTP запрос Django (GET для формы, POST для отправки)

    Returns:
        HttpResponse:
            - GET: Рендер формы account/auth/email-verification-resend.html
            - POST: Redirect на signin с сообщением о результате

    Flow:
        1. Проверяет существование User с данным email
        2. Если email_is_verified=False: генерирует новый токен и отправляет письмо
        3. Если email_is_verified=True: показывает "Email уже подтвержден"
        4. Если User не найден: показывает ошибку

    Example:
        POST /account/resend-verification
        {
            "email": "user@example.com"
        }

        → Отправляет новое письмо с /account/verify-email-confirm/{uidb64}/{token}/
        → Redirect на signin с "Письмо отправлено"
    """
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if not user.email_is_verified:
                logger.info(f"Повторная отправка письма верификации для пользователя: {email}")
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                activation_url = request.build_absolute_uri(
                    reverse(
                        "authentication:verify_email_confirm",
                        kwargs={"uidb64": uidb64, "token": token},
                    )
                )

                # Попытка отправить email через Celery, при ошибке - синхронно
                try:
                    send_verification_email.delay(
                        user.id,
                        activation_url,
                        _("Активируйте ваш аккаунт."),
                        "auth/email/email-verification.html",
                    )
                except Exception as celery_error:
                    logger.warning(
                        f"Celery недоступен при повторной отправке, используем синхронную: {celery_error}"
                    )
                    send_verification_email_sync(
                        user.id,
                        activation_url,
                        _("Активируйте ваш аккаунт."),
                        "auth/email/email-verification.html",
                    )

                messages.success(
                    request,
                    _("Мы отправили повторное письмо для подтверждения вашего email."),
                )
            else:
                logger.info(f"Попытка повторной отправки для уже подтвержденного email: {email}")
                messages.info(request, _("Ваш email уже подтвержден."))
        except User.DoesNotExist:
            logger.warning(f"Попытка повторной отправки на несуществующий email: {email}")
            messages.error(request, _("Пользователь с таким email не найден."))
        return redirect("authentication:signin")

    return render(request, "auth/auth/email-verification-resend.html")


@require_http_methods(["GET", "POST"])
@login_required
@never_cache
def user_logout(request: HttpRequest) -> HttpResponse:
    """
    Выход пользователя из системы.

    Завершает сессию пользователя через Django logout() и перенаправляет на главную.

    Args:
        request: HTTP запрос Django

    Returns:
        HttpResponse: Redirect на домашнюю страницу "/"

    Example:
        GET /account/logout
        → Вызывает logout(request)
        → Redirect на "/"
    """
    logout(request)
    return redirect("/")
