"""
Core Schemas Tests

Тесты для Pydantic схем core приложения:
- FeedbackSchema - валидация обратной связи
- SubscriptionSchema - валидация подписки
- ContactInfoSchema - контактная информация
- StatsSchema - статистика платформы
- Response схемы

Проверяем валидаторы, ограничения полей и обработку ошибок.
"""

import pytest
from pydantic import ValidationError

from core.schemas import (
    ContactInfoSchema,
    FeedbackResponseSchema,
    FeedbackSchema,
    StatsSchema,
    SubscriptionResponseSchema,
    SubscriptionSchema,
)


class TestFeedbackSchema:
    """Тесты для FeedbackSchema."""

    def test_valid_feedback(self):
        """Тест валидных данных feedback."""
        data = {
            "first_name": "Иван",
            "phone_number": "+79991234567",
            "email": "ivan@test.com",
            "message": "Хочу узнать больше о курсах",
            "agree_terms": True,
        }

        feedback = FeedbackSchema(**data)

        assert feedback.first_name == "Иван"
        assert feedback.phone_number == "+79991234567"
        assert feedback.email == "ivan@test.com"
        assert feedback.agree_terms is True

    def test_phone_without_plus(self):
        """Тест телефона без плюса в начале."""
        data = {
            "first_name": "Петр",
            "phone_number": "79991234567",  # Без +
            "email": "petr@test.com",
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            FeedbackSchema(**data)

        errors = exc_info.value.errors()
        assert any("phone_number" in str(e) for e in errors)

    def test_phone_invalid_format(self):
        """Тест невалидного формата телефона."""
        data = {
            "first_name": "Анна",
            "phone_number": "+7-999-123-45-67",  # С дефисами
            "email": "anna@test.com",
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            FeedbackSchema(**data)

        errors = exc_info.value.errors()
        assert any("phone_number" in str(e) for e in errors)

    def test_phone_too_short(self):
        """Тест слишком короткого телефона."""
        data = {
            "first_name": "Мария",
            "phone_number": "+712345",  # Меньше 9 цифр
            "email": "maria@test.com",
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError):
            FeedbackSchema(**data)

    def test_phone_too_long(self):
        """Тест слишком длинного телефона."""
        data = {
            "first_name": "Олег",
            "phone_number": "+71234567890123456",  # Больше 15 цифр
            "email": "oleg@test.com",
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError):
            FeedbackSchema(**data)

    def test_name_with_digits(self):
        """Тест имени с цифрами."""
        data = {
            "first_name": "Иван123",  # Цифры в имени
            "phone_number": "+79991234567",
            "email": "ivan@test.com",
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            FeedbackSchema(**data)

        errors = exc_info.value.errors()
        assert any("first_name" in str(e) for e in errors)

    def test_message_too_short(self):
        """Тест слишком короткого сообщения."""
        data = {
            "first_name": "Сергей",
            "phone_number": "+79991234567",
            "email": "sergey@test.com",
            "message": "Привет",  # Меньше 10 символов
            "agree_terms": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            FeedbackSchema(**data)

        errors = exc_info.value.errors()
        assert any("message" in str(e) for e in errors)

    def test_disagree_terms(self):
        """Тест отказа от условий."""
        data = {
            "first_name": "Елена",
            "phone_number": "+79991234567",
            "email": "elena@test.com",
            "message": "Длинное тестовое сообщение",
            "agree_terms": False,  # Не согласен
        }

        with pytest.raises(ValidationError) as exc_info:
            FeedbackSchema(**data)

        errors = exc_info.value.errors()
        assert any("agree_terms" in str(e) for e in errors)

    def test_invalid_email(self):
        """Тест невалидного email."""
        data = {
            "first_name": "Дмитрий",
            "phone_number": "+79991234567",
            "email": "not-an-email",
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError):
            FeedbackSchema(**data)

    def test_missing_required_field(self):
        """Тест отсутствия обязательного поля."""
        data = {
            "first_name": "Алексей",
            "phone_number": "+79991234567",
            # Нет email
            "message": "Тестовое сообщение для проверки",
            "agree_terms": True,
        }

        with pytest.raises(ValidationError):
            FeedbackSchema(**data)


class TestSubscriptionSchema:
    """Тесты для SubscriptionSchema."""

    def test_valid_subscription(self):
        """Тест валидной подписки."""
        data = {"email": "user@test.com"}

        subscription = SubscriptionSchema(**data)

        assert subscription.email == "user@test.com"

    def test_invalid_email(self):
        """Тест невалидного email."""
        data = {"email": "invalid-email"}

        with pytest.raises(ValidationError):
            SubscriptionSchema(**data)

    def test_missing_email(self):
        """Тест отсутствия email."""
        data = {}

        with pytest.raises(ValidationError):
            SubscriptionSchema(**data)


class TestContactInfoSchema:
    """Тесты для ContactInfoSchema."""

    def test_full_contact_info(self):
        """Тест полной контактной информации."""
        data = {
            "email": "info@pylandschool.com",
            "phone": "+7 (999) 123-45-67",
            "address": "Москва, ул. Примерная, д. 1",
            "social_links": {
                "telegram": "https://t.me/pyland",
                "youtube": "https://youtube.com/@pyland",
            },
            "working_hours": "Пн-Пт: 10:00-18:00 МСК",
        }

        contact = ContactInfoSchema(**data)

        assert contact.email == "info@pylandschool.com"
        assert contact.phone == "+7 (999) 123-45-67"
        assert "telegram" in contact.social_links

    def test_minimal_contact_info(self):
        """Тест минимальной контактной информации."""
        data = {
            "email": "info@pylandschool.com",
            "phone": "+7 (999) 123-45-67",
        }

        contact = ContactInfoSchema(**data)

        assert contact.email == "info@pylandschool.com"
        assert contact.address is None
        assert contact.social_links == {}

    def test_empty_social_links(self):
        """Тест с пустыми социальными сетями."""
        data = {
            "email": "info@pylandschool.com",
            "phone": "+7 (999) 123-45-67",
            "social_links": {},
        }

        contact = ContactInfoSchema(**data)
        assert contact.social_links == {}


class TestStatsSchema:
    """Тесты для StatsSchema."""

    def test_valid_stats(self):
        """Тест валидной статистики."""
        data = {
            "total_students": 0,  # Not publicly displayed
            "total_courses": 15,
            "total_lessons": 230,
            "total_hours": 145.5,
            "completion_rate": 0.0,  # Not publicly displayed
        }

        stats = StatsSchema(**data)

        assert stats.total_students == 0
        assert stats.total_courses == 15
        assert stats.completion_rate == 0.0

    def test_default_values(self):
        """Тест значений по умолчанию."""
        data = {}

        stats = StatsSchema(**data)

        assert stats.total_students == 0
        assert stats.total_courses == 0
        assert stats.total_lessons == 0
        assert stats.total_hours == 0.0
        assert stats.completion_rate == 0.0

    def test_completion_rate_boundaries(self):
        """Тест границ completion_rate (0-100)."""
        # Валидные значения
        StatsSchema(completion_rate=0.0)
        StatsSchema(completion_rate=50.5)
        StatsSchema(completion_rate=100.0)

        # Невалидные значения
        with pytest.raises(ValidationError):
            StatsSchema(completion_rate=-1.0)

        with pytest.raises(ValidationError):
            StatsSchema(completion_rate=101.0)

    def test_negative_values(self):
        """Тест что нельзя задать отрицательные значения для счетчиков."""
        # В текущей схеме нет ограничений на отрицательные значения
        # Но логически они должны быть >= 0
        # Это можно добавить через Field(ge=0)
        pass


class TestResponseSchemas:
    """Тесты для Response схем."""

    def test_feedback_response(self):
        """Тест FeedbackResponseSchema."""
        data = {
            "success": True,
            "message": "Спасибо за обращение!",
            "feedback_id": 42,
        }

        response = FeedbackResponseSchema(**data)

        assert response.success is True
        assert response.feedback_id == 42

    def test_feedback_response_without_id(self):
        """Тест FeedbackResponseSchema без ID."""
        data = {
            "success": False,
            "message": "Ошибка создания",
        }

        response = FeedbackResponseSchema(**data)

        assert response.success is False
        assert response.feedback_id is None

    def test_subscription_response(self):
        """Тест SubscriptionResponseSchema."""
        data = {
            "success": True,
            "message": "Вы подписаны!",
            "already_subscribed": False,
        }

        response = SubscriptionResponseSchema(**data)

        assert response.success is True
        assert response.already_subscribed is False

    def test_subscription_response_defaults(self):
        """Тест значений по умолчанию."""
        data = {
            "success": True,
            "message": "OK",
        }

        response = SubscriptionResponseSchema(**data)

        assert response.already_subscribed is False


class TestSchemaExamples:
    """Тесты что примеры в схемах валидны."""

    def test_feedback_example(self):
        """Тест что example из FeedbackSchema валиден."""
        example = FeedbackSchema.model_config["json_schema_extra"]["example"]

        # Должен создаться без ошибок
        feedback = FeedbackSchema(**example)

        assert feedback.first_name is not None
        assert feedback.email is not None

    def test_subscription_example(self):
        """Тест что example из SubscriptionSchema валиден."""
        example = SubscriptionSchema.model_config["json_schema_extra"]["example"]

        subscription = SubscriptionSchema(**example)

        assert "@" in subscription.email

    def test_contact_info_example(self):
        """Тест что example из ContactInfoSchema валиден."""
        example = ContactInfoSchema.model_config["json_schema_extra"]["example"]

        contact = ContactInfoSchema(**example)

        assert contact.email is not None
        assert contact.phone is not None

    def test_stats_example(self):
        """Тест что example из StatsSchema валиден."""
        example = StatsSchema.model_config["json_schema_extra"]["example"]

        stats = StatsSchema(**example)

        assert stats.total_students > 0
        assert 0 <= stats.completion_rate <= 100
