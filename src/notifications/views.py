"""
Notifications Views Module - Django views для управления подписками.

Этот модуль содержит представления для работы с уведомлениями:

Представления:
    - subscribe_view: Обработка подписки на email рассылку

Особенности:
    - Проверка на дублирование подписок
    - Валидация email через форму
    - Flash messages для информирования
    - Редирект на предыдущую страницу
    - Защита от спама

Автор: Pyland Team
Дата: 2025
"""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .forms import SubscriptionForm
from .models import Subscription


def subscribe_view(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает форму подписки на уведомления.

    Принимает email пользователя, сохраняет его в базе, если он ещё не подписан.
    Показывает сообщение об успехе или ошибке и возвращает пользователя на предыдущую страницу.
    """
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            obj, created = Subscription.objects.get_or_create(email=email)
            if created:
                messages.success(request, "Вы успешно подписались!")
            else:
                messages.info(request, "Вы уже подписаны.")
        else:
            messages.error(request, "Введите корректный email.")
    return redirect(request.headers.get("referer", "/"))
