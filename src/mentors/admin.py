"""
Mentors Admin Module - Административный интерфейс Django для управления менторами.

ВАЖНО: Все регистрации admin для Reviewer (менторов) перемещены
в authentication/admin.py для централизованного управления.

Управление Reviewer (менторами) через Django Admin:
    - URL: /admin/authentication/reviewer/
    - Регистрация: authentication.admin.ReviewerAdmin

Дополнительная информация:
    - /src/authentication/admin.py
    - /src/authentication/decorators.py (управление доступом на основе ролей)

Автор: Pyland Team
Дата: 2025
"""

# Register your models here.
