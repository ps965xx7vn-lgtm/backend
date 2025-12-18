"""
Core API Tests

Тесты для API эндпоинтов core приложения:
- POST /api/core/feedback/ - отправка обратной связи
- POST /api/core/subscribe/ - подписка на рассылку
- GET /api/core/contact-info/ - получение контактной информации
- GET /api/core/stats/ - получение статистики платформы

Все эндпоинты публичные (auth=None), не требуют авторизации.
"""

import pytest

from authentication.models import Role, Student
from courses.models import Course, Lesson
from managers.models import Feedback
from notifications.models import Subscription


@pytest.mark.django_db
class TestFeedbackAPI:
    """Тесты для эндпоинта создания обратной связи."""

    def test_create_feedback_success(self, api_client):
        """Тест успешного создания feedback."""
        data = {
            "first_name": "Иван",
            "phone_number": "+79991234567",
            "email": "ivan@test.com",
            "message": "Хочу узнать больше о курсах Python",
            "agree_terms": True,
        }

        response = api_client.post("/feedback/", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "feedback_id" in result
        assert "Спасибо" in result["message"]

        # Проверяем что запись создана в БД
        feedback = Feedback.objects.get(id=result["feedback_id"])
        assert feedback.first_name == "Иван"
        assert feedback.email == "ivan@test.com"
        assert feedback.phone_number == "+79991234567"

    def test_create_feedback_invalid_phone(self, api_client):
        """Тест с невалидным форматом телефона."""
        data = {
            "first_name": "Петр",
            "phone_number": "89991234567",  # Без плюса
            "email": "petr@test.com",
            "message": "Тестовое сообщение",
            "agree_terms": True,
        }

        response = api_client.post("/feedback/", json=data)
        assert response.status_code == 422  # Validation error

    def test_create_feedback_invalid_email(self, api_client):
        """Тест с невалидным email."""
        data = {
            "first_name": "Анна",
            "phone_number": "+79991234567",
            "email": "invalid-email",  # Невалидный email
            "message": "Тестовое сообщение",
            "agree_terms": True,
        }

        response = api_client.post("/core/feedback/", json=data)
        assert response.status_code == 422

    def test_create_feedback_short_message(self, api_client):
        """Тест с коротким сообщением (< 10 символов)."""
        data = {
            "first_name": "Мария",
            "phone_number": "+79991234567",
            "email": "maria@test.com",
            "message": "Привет",  # Меньше 10 символов
            "agree_terms": True,
        }

        response = api_client.post("/feedback/", json=data)
        assert response.status_code == 422

    def test_create_feedback_without_consent(self, api_client):
        """Тест без согласия с условиями."""
        data = {
            "first_name": "Олег",
            "phone_number": "+79991234567",
            "email": "oleg@test.com",
            "message": "Длинное тестовое сообщение для проверки",
            "agree_terms": False,  # Не согласен
        }

        response = api_client.post("/feedback/", json=data)
        assert response.status_code == 422

    def test_create_feedback_name_with_digits(self, api_client):
        """Тест с цифрами в имени (должно быть запрещено)."""
        data = {
            "first_name": "Иван123",  # Цифры в имени
            "phone_number": "+79991234567",
            "email": "ivan@test.com",
            "message": "Тестовое сообщение для проверки валидации",
            "agree_terms": True,
        }

        response = api_client.post("/core/feedback/", json=data)
        assert response.status_code == 422


@pytest.mark.django_db
class TestSubscriptionAPI:
    """Тесты для эндпоинта подписки на рассылку."""

    def test_create_subscription_new(self, api_client):
        """Тест создания новой подписки."""
        data = {"email": "newuser@test.com"}

        response = api_client.post("/core/subscribe/", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["already_subscribed"] is False
        assert "успешно подписаны" in result["message"]

        # Проверяем создание в БД
        subscription = Subscription.objects.get(email="newuser@test.com")
        assert subscription.is_active is True

    def test_create_subscription_already_exists(self, api_client):
        """Тест подписки с уже существующим email."""
        # Создаем существующую подписку
        Subscription.objects.create(email="existing@test.com", is_active=True)

        data = {"email": "existing@test.com"}
        response = api_client.post("/core/subscribe/", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["already_subscribed"] is True
        assert "уже подписан" in result["message"]

    def test_reactivate_inactive_subscription(self, api_client):
        """Тест реактивации неактивной подписки."""
        # Создаем неактивную подписку
        Subscription.objects.create(email="inactive@test.com", is_active=False)

        data = {"email": "inactive@test.com"}
        response = api_client.post("/core/subscribe/", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["already_subscribed"] is False
        assert "снова активна" in result["message"]

        # Проверяем что подписка активирована
        subscription = Subscription.objects.get(email="inactive@test.com")
        assert subscription.is_active is True

    def test_subscription_invalid_email(self, api_client):
        """Тест с невалидным email."""
        data = {"email": "not-an-email"}

        response = api_client.post("/core/subscribe/", json=data)
        assert response.status_code == 422


@pytest.mark.django_db
class TestContactInfoAPI:
    """Тесты для эндпоинта получения контактной информации."""

    def test_get_contact_info(self, api_client):
        """Тест получения контактной информации."""
        response = api_client.get("/core/contact-info/")

        assert response.status_code == 200
        data = response.json()

        # Проверяем наличие всех полей
        assert "email" in data
        assert "phone" in data
        assert "address" in data
        assert "social_links" in data
        assert "working_hours" in data

        # Проверяем формат данных
        assert "@" in data["email"]
        assert "+" in data["phone"]
        assert isinstance(data["social_links"], dict)

        # Проверяем социальные сети
        assert "telegram" in data["social_links"]
        assert "youtube" in data["social_links"]


@pytest.mark.django_db
class TestPlatformStatsAPI:
    """Тесты для эндпоинта статистики платформы."""

    def test_get_stats_empty_db(self, api_client):
        """Тест получения статистики при пустой БД."""
        response = api_client.get("/core/stats/")

        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа
        assert "total_students" in data
        assert "total_courses" in data
        assert "total_lessons" in data
        assert "total_hours" in data
        assert "completion_rate" in data

        # При пустой БД все должно быть 0
        assert data["total_students"] == 0
        assert data["total_courses"] == 0
        assert data["total_lessons"] == 0
        assert data["total_hours"] == 0.0
        assert data["completion_rate"] == 0.0

    def test_get_stats_with_data(self, api_client, django_user_model):
        """Тест получения статистики с данными в БД."""
        # Создаем роль студента
        student_role = Role.objects.create(name="student")

        # Создаем 3 студентов
        for i in range(3):
            user = django_user_model.objects.create_user(
                username=f"student{i}", email=f"student{i}@test.com", password="testpass123"
            )
            user.role = student_role
            user.save()

        # Создаем 2 курса
        Course.objects.create(name="Python Basics", slug="python-basics")
        Course.objects.create(name="Django Advanced", slug="django-advanced")

        response = api_client.get("/core/stats/")

        assert response.status_code == 200
        data = response.json()

        # Проверяем что статистика соответствует созданным данным
        assert data["total_students"] == 3
        assert data["total_courses"] == 2
        # Не создаем уроки из-за сложной логики lesson_number
        assert isinstance(data["total_lessons"], int)
        assert isinstance(data["total_hours"], float)
        assert isinstance(data["completion_rate"], float)

    def test_stats_counts_all_courses(self, api_client):
        """Тест что статистика учитывает все курсы."""
        # Создаем 2 курса
        course1 = Course.objects.create(name="Course 1", slug="course-1")
        course2 = Course.objects.create(name="Course 2", slug="course-2")

        # Добавляем уроки в оба курса
        Lesson.objects.create(course=course1, name="Lesson 1", slug="course-1-lesson-1")
        Lesson.objects.create(course=course2, name="Lesson 2", slug="course-2-lesson-2")

        response = api_client.get("/core/stats/")
        data = response.json()

        # Должны учитываться оба курса
        assert data["total_courses"] == 2
        assert data["total_lessons"] == 2
        assert data["total_hours"] == 0.0  # Нет duration в модели


@pytest.mark.django_db
class TestAPIIntegration:
    """Интеграционные тесты API."""

    def test_full_user_journey(self, api_client):
        """Тест полного пути пользователя через API."""
        # 1. Получаем контактную информацию
        contact_response = api_client.get("/contact-info/")
        assert contact_response.status_code == 200

        # 2. Получаем статистику платформы
        stats_response = api_client.get("/stats/")
        assert stats_response.status_code == 200

        # 3. Подписываемся на рассылку
        subscribe_response = api_client.post("/subscribe/", json={"email": "journey@test.com"})
        assert subscribe_response.status_code == 200
        assert subscribe_response.json()["success"] is True

        # 4. Отправляем feedback
        feedback_response = api_client.post(
            "/feedback/",
            json={
                "first_name": "Тест",
                "phone_number": "+79991234567",
                "email": "journey@test.com",
                "message": "Мне понравился ваш сайт!",
                "agree_terms": True,
            },
        )
        assert feedback_response.status_code == 200
        assert feedback_response.json()["success"] is True

        # Проверяем что все записи созданы
        assert Subscription.objects.filter(email="journey@test.com").exists()
        assert Feedback.objects.filter(email="journey@test.com").exists()
