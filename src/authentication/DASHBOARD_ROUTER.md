# Dashboard Router - Автоматический роутинг по ролям

## Описание

Система автоматического перенаправления пользователей на соответствующие dashboard'ы в зависимости от их роли.

## Архитектура

### 1. Декоратор `@redirect_to_role_dashboard`

**Расположение:** `authentication/decorators.py`

**Логика роутинга:**

```python
@redirect_to_role_dashboard
def my_view(request):

    # Код не выполнится, произойдет автоматический редирект

    pass
```text
**Маршрутизация:**

- `admin` → `managers:dashboard` (полный доступ к админке)
- `manager` → `managers:dashboard` (управление платформой)
- `mentor` → `reviewers:dashboard` (проверка работ + менторство)
- `reviewer` → `reviewers:dashboard` (проверка работ студентов)
- `student` → `students:account_dashboard` (личный кабинет с ID)
- `support` → `managers:dashboard` (поддержка пользователей)
- `is_staff=True` (без роли) → `managers:dashboard` (персонал)
- Не аутентифицирован → `authentication:login`
- Неизвестная роль или без роли → `core:home`

### 2. View для общего роутинга

**Расположение:** `core/views.py`

```python
@redirect_to_role_dashboard
def home_redirect(request: HttpRequest) -> HttpResponse:
    """Роутер dashboard по ролям пользователей"""
    return redirect("core:home")  # Fallback, не выполнится
```text
### 3. URL endpoints

**Расположение:** `core/urls.py`

```python
urlpatterns = [
    path("dashboard/", views.home_redirect, name="dashboard"),

    #

]
```text
## Использование

### В шаблонах

Вместо проверки роли в шаблоне:

```django
❌ ПЛОХО:
{% if user.role.name == 'reviewer' %}
    <a href="{% url 'reviewers:dashboard' %}">Dashboard</a>
{% elif user.role.name == 'student' %}
    <a href="{% url 'students:account_dashboard' user.student.id %}">Dashboard</a>
{% endif %}

✅ ХОРОШО:
<a href="{% url 'core:dashboard' %}">Dashboard</a>
```text
### В views

```python
from authentication.decorators import redirect_to_role_dashboard

@redirect_to_role_dashboard
def my_router_view(request):
    """Автоматически перенаправит на нужный dashboard"""
    pass
```text
### Прямой редирект

```python
def some_view(request):

    # Перенаправить на dashboard пользователя

    return redirect('core:dashboard')
```text
## Примеры

### 1. Ссылка "Дашборд" в header

```django
<!-- В _header.html -->
<a href="{% url 'core:dashboard' %}">Дашборд</a>
```text
### 2. После успешного логина

```python
def login_view(request):

    #

    login(request, user)
    return redirect('core:dashboard')  # Автоматически на нужный dashboard
```text
### 3. Кнопка на главной странице

```django
<!-- В home.html -->
{% if user.is_authenticated %}
    <a href="{% url 'core:dashboard' %}" class="btn">Перейти в кабинет</a>
{% endif %}
```text
## Преимущества

1. ✅ **Чистые шаблоны** - никаких проверок ролей
2. ✅ **Централизованная логика** - один декоратор управляет всем
3. ✅ **Легко расширять** - добавил роль → обновил декоратор
4. ✅ **Логирование** - все редиректы записываются в лог
5. ✅ **Безопасность** - проверка аутентификации встроена

## Логирование

Декоратор автоматически логирует все редиректы:

```text
INFO: Redirecting a@mail.ru (reviewer) to reviewers dashboard
INFO: Redirecting b@mail.ru (student) to student dashboard
WARNING: Unknown role 'None' for user c@mail.ru, redirecting to home
```text
## Тестирование

```python
def test_dashboard_router_reviewer(client, reviewer_user):
    client.force_login(reviewer_user)
    response = client.get(reverse('core:dashboard'))
    assert response.status_code == 302
    assert response.url == reverse('reviewers:dashboard')

def test_dashboard_router_student(client, student_user):
    client.force_login(student_user)
    response = client.get(reverse('core:dashboard'))
    assert response.status_code == 302
    assert 'students/account/' in response.url
```text
## Миграция существующего кода

### Шаг 1: Обновить шаблоны

Заменить все условные ссылки на `{% url 'core:dashboard' %}`

### Шаг 2: Обновить views

```python

# Было

if user.role.name == 'reviewer':
    return redirect('reviewers:dashboard')
elif user.role.name == 'student':
    return redirect('students:account_dashboard', user.student.id)

# Стало

return redirect('core:dashboard')
```text
### Шаг 3: Протестировать

Проверить редиректы для всех ролей

## Troubleshooting

**Проблема:** Редирект на home вместо dashboard

- Проверить наличие роли: `user.role.name`
- Проверить логи: `grep "Redirecting" logs/django.log`

**Проблема:** Для студента нет ID

- Проверить наличие профиля: `user.student`
- Проверить сигналы создания Student

**Проблема:** Циклический редирект

- Не использовать декоратор на самих dashboard views
- Декоратор только для роутеров
