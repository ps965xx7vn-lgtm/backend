"""
Тесты для Django signals authentication.

Проверяет автоматическое создание профилей при создании пользователей.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from authentication.models import Mentor, Reviewer, Student
from authentication.signals import create_user_student, save_user_student

User = get_user_model()


@pytest.mark.django_db
class TestUserProfileCreationSignals:
    """Тесты автоматического создания профилей."""

    def test_student_profile_created_on_user_creation(self, student_role):
        """При создании пользователя с ролью student создается профиль Student."""
        user = User.objects.create_user(
            email="student@example.com", password="TestPass123!", role=student_role
        )

        assert hasattr(user, "student")
        assert user.student is not None
        assert user.student.user == user
        assert user.student.is_active is True

    def test_mentor_profile_created_on_user_creation(self, mentor_role):
        """При создании пользователя с ролью mentor создается профиль Mentor."""
        user = User.objects.create_user(
            email="mentor@example.com", password="TestPass123!", role=mentor_role
        )

        assert hasattr(user, "mentor")
        assert user.mentor is not None
        assert user.mentor.user == user

    def test_reviewer_profile_created_on_user_creation(self, reviewer_role):
        """При создании пользователя с ролью reviewer создается профиль Reviewer."""
        user = User.objects.create_user(
            email="reviewer@example.com", password="TestPass123!", role=reviewer_role
        )

        assert hasattr(user, "reviewer")
        assert user.reviewer is not None
        assert user.reviewer.user == user

    def test_manager_profile_created_on_user_creation(self, manager_role):
        """При создании пользователя с ролью manager создается профиль Manager."""
        user = User.objects.create_user(
            email="manager@example.com", password="TestPass123!", role=manager_role
        )

        assert hasattr(user, "manager")
        assert user.manager is not None
        assert user.manager.user == user

    def test_no_profile_created_without_role(self):
        """Без роли создается student профиль по умолчанию."""
        user = User.objects.create_user(email="norole@example.com", password="TestPass123!")

        # Проверяем, что создан student профиль по умолчанию
        assert hasattr(user, "student")
        assert user.student is not None
        # Проверяем, что других профилей нет
        from authentication.models import Mentor, Reviewer

        assert not Mentor.objects.filter(user=user).exists()
        assert not Reviewer.objects.filter(user=user).exists()

    def test_profile_not_duplicated_on_save(self, student_role):
        """Профиль не дублируется при повторном сохранении пользователя."""
        user = User.objects.create_user(
            email="student@example.com", password="TestPass123!", role=student_role
        )

        # Получаем ID первого профиля
        first_profile_id = user.student.id

        # Сохраняем пользователя снова
        user.first_name = "Updated"
        user.save()

        # Проверяем, что профиль тот же
        user.refresh_from_db()
        assert user.student.id == first_profile_id
        assert Student.objects.filter(user=user).count() == 1

    def test_signal_handles_legacy_users(self, student_role):
        """Signal корректно обрабатывает существующих пользователей без профиля."""
        # Отключаем signals временно
        post_save.disconnect(create_user_student, sender=User)
        post_save.disconnect(save_user_student, sender=User)

        try:
            # Создаем пользователя без профиля
            user = User.objects.create_user(
                email="legacy@example.com", password="TestPass123!", role=student_role
            )

            # Включаем signals обратно
            post_save.connect(create_user_student, sender=User)
            post_save.connect(save_user_student, sender=User)

            # Триггерим save
            user.save()

            # Проверяем, что профиль создан
            user.refresh_from_db()
            assert hasattr(user, "student")
            assert user.student is not None

        finally:
            # Восстанавливаем signals
            post_save.connect(create_user_student, sender=User)
            post_save.connect(save_user_student, sender=User)


@pytest.mark.django_db
class TestMultiRoleSupport:
    """Тесты поддержки изменения роли."""

    def test_user_can_change_role(self, student_role, mentor_role):
        """Пользователь может сменить роль (User имеет одну роль через FK)."""
        user = User.objects.create_user(
            email="multi@example.com", password="TestPass123!", role=student_role
        )

        # Проверяем начальную роль
        assert user.role == student_role

        # Меняем роль
        user.role = mentor_role
        user.save()

        # Проверяем новую роль
        user.refresh_from_db()
        assert user.role == mentor_role

    def test_profile_creation_for_primary_role_only(self, student_role):
        """При создании пользователя профиль создается только для основной роли."""
        user = User.objects.create_user(
            email="primary@example.com", password="TestPass123!", role=student_role
        )

        # Проверяем, что создан только student профиль
        assert hasattr(user, "student")
        assert user.student is not None

        # Проверяем, что других профилей нет
        assert not hasattr(user, "mentor") or not Mentor.objects.filter(user=user).exists()
        assert not hasattr(user, "reviewer") or not Reviewer.objects.filter(user=user).exists()
