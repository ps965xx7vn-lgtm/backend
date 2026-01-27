"""
Certificates API Module - REST API для работы с сертификатами.

Этот модуль будет содержать эндпоинты для сертификатов:

Планируемые Endpoints:
    GET    /api/certificates/                   - Список сертификатов пользователя
    GET    /api/certificates/{id}               - Детали сертификата
    GET    /api/certificates/{id}/download      - Скачать PDF
    GET    /api/certificates/verify/{number}    - Публичная проверка
    POST   /api/certificates/generate           - Генерация сертификата

Особенности:
    - Автоматическая генерация PDF
    - Уникальные номера сертификатов
    - Публичная верификация без авторизации
    - Цифровая подпись для защиты
    - Кеширование PDF файлов

Автор: Pyland Team
Дата: 2025
"""

from ninja import Router

router = Router()


# Пример эндпоинта для теста
@router.get("/ping")
def ping(request):
    return {"ping": "pong"}
