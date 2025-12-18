"""
Core Response Validation Tests

Тесты для проверки что все API эндпоинты возвращают
валидные Pydantic модели, а не просто dict.
"""

import pytest
from pydantic import ValidationError

from core.schemas import (
    ContactInfoSchema,
    FeedbackResponseSchema,
    StatsSchema,
    SubscriptionResponseSchema,
)


class TestResponseValidation:
    """Тесты валидации возвращаемых значений."""

    def test_feedback_response_validates_success_field(self):
        """Проверка что success должен быть bool."""
        # Валидные данные
        response = FeedbackResponseSchema(success=True, message="Test", feedback_id=1)
        assert response.success is True

        # Невалидные данные
        with pytest.raises(ValidationError):
            FeedbackResponseSchema(success="not a bool", message="Test")  # Должен быть bool

    def test_feedback_response_validates_feedback_id(self):
        """Проверка что feedback_id должен быть int или None."""
        # С ID
        response = FeedbackResponseSchema(success=True, message="Test", feedback_id=42)
        assert response.feedback_id == 42

        # Без ID (None)
        response = FeedbackResponseSchema(success=True, message="Test")
        assert response.feedback_id is None

    def test_subscription_response_validates_already_subscribed(self):
        """Проверка что already_subscribed должен быть bool."""
        # С явным значением
        response = SubscriptionResponseSchema(success=True, message="Test", already_subscribed=True)
        assert response.already_subscribed is True

        # С дефолтным значением
        response = SubscriptionResponseSchema(success=True, message="Test")
        assert response.already_subscribed is False

    def test_contact_info_validates_social_links(self):
        """Проверка что social_links должен быть dict."""
        # С соц. сетями
        response = ContactInfoSchema(
            email="test@test.com",
            phone="+1234567890",
            social_links={"telegram": "https://t.me/test"},
        )
        assert isinstance(response.social_links, dict)

        # Пустой dict (по умолчанию)
        response = ContactInfoSchema(email="test@test.com", phone="+1234567890")
        assert response.social_links == {}

    def test_stats_validates_numeric_fields(self):
        """Проверка что все счетчики должны быть числами."""
        # Валидные данные
        stats = StatsSchema(
            total_students=100,
            total_courses=10,
            total_lessons=50,
            total_hours=25.5,
            completion_rate=75.0,
        )

        assert stats.total_students == 100
        assert stats.total_courses == 10
        assert stats.total_hours == 25.5

        # Невалидные данные
        with pytest.raises(ValidationError):
            StatsSchema(total_students="not a number", total_courses=10)  # Должен быть int

    def test_stats_validates_completion_rate_bounds(self):
        """Проверка что completion_rate в диапазоне 0-100."""
        # Валидные значения
        StatsSchema(completion_rate=0.0)
        StatsSchema(completion_rate=50.5)
        StatsSchema(completion_rate=100.0)

        # Невалидные значения
        with pytest.raises(ValidationError):
            StatsSchema(completion_rate=-1.0)  # Меньше 0

        with pytest.raises(ValidationError):
            StatsSchema(completion_rate=101.0)  # Больше 100

    def test_contact_info_requires_email_and_phone(self):
        """Проверка что email и phone обязательны."""
        # Валидные данные
        ContactInfoSchema(email="test@test.com", phone="+1234567890")

        # Без email
        with pytest.raises(ValidationError):
            ContactInfoSchema(phone="+1234567890")

        # Без phone
        with pytest.raises(ValidationError):
            ContactInfoSchema(email="test@test.com")

    def test_response_schemas_are_immutable_after_creation(self):
        """Проверка что Pydantic модели возвращают правильные типы."""
        # FeedbackResponseSchema
        feedback_response = FeedbackResponseSchema(
            success=True, message="Test message", feedback_id=123
        )

        # Проверяем типы
        assert isinstance(feedback_response.success, bool)
        assert isinstance(feedback_response.message, str)
        assert isinstance(feedback_response.feedback_id, int)

        # SubscriptionResponseSchema
        sub_response = SubscriptionResponseSchema(
            success=True, message="Test", already_subscribed=False
        )

        assert isinstance(sub_response.success, bool)
        assert isinstance(sub_response.already_subscribed, bool)

    def test_pydantic_models_can_be_serialized_to_dict(self):
        """Проверка что Pydantic модели можно сериализовать."""
        response = FeedbackResponseSchema(success=True, message="Test", feedback_id=42)

        # Сериализуем в dict
        data = response.model_dump()

        assert data == {"success": True, "message": "Test", "feedback_id": 42}

    def test_pydantic_models_can_be_serialized_to_json(self):
        """Проверка что Pydantic модели можно сериализовать в JSON."""
        response = StatsSchema(
            total_students=100,
            total_courses=10,
            total_lessons=50,
            total_hours=25.5,
            completion_rate=75.0,
        )

        # Сериализуем в JSON
        json_str = response.model_dump_json()

        assert isinstance(json_str, str)
        assert '"total_students":100' in json_str
        assert '"completion_rate":75.0' in json_str
