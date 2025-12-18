"""
Тесты для моделей authentication.

Проверяет:
- Создание пользователей
- Роли и права доступа
- Профили всех типов (Student, Reviewer, Mentor, Manager, Admin, Support)
- Методы моделей
- Связи между моделями
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from authentication.models import ExpertiseArea, Role
from authentication.tests.factories import ExpertiseAreaFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Тесты модели User."""

    def test_create_user_with_email(self):
        """Создание пользователя с email."""
        user = User.objects.create_user(
            email="test@example.com", password="TestPass123!", first_name="Test", last_name="User"
        )

        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("TestPass123!")

    def test_create_superuser(self):
        """Создание суперпользователя."""
        user = User.objects.create_superuser(email="admin@example.com", password="AdminPass123!")

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.email == "admin@example.com"

    def test_user_email_unique(self):
        """Email должен быть уникальным."""
        User.objects.create_user(email="test@example.com", password="TestPass123!")

        with pytest.raises(IntegrityError):
            User.objects.create_user(email="test@example.com", password="AnotherPass123!")

    def test_user_str_method(self):
        """Тест __str__ метода."""
        user = UserFactory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_user_get_full_name(self):
        """Получение полного имени."""
        user = UserFactory(first_name="John", last_name="Doe")
        assert user.get_full_name() == "John Doe"

    def test_user_get_short_name(self):
        """Получение короткого имени."""
        user = UserFactory(first_name="John", last_name="Doe")
        assert user.get_short_name() == "John"

    def test_user_email_verification_defaults_to_false(self):
        """Email не подтвержден по умолчанию."""
        user = UserFactory()
        assert user.email_is_verified is False

    def test_user_factory_creates_valid_user(self):
        """Фабрика создает валидного пользователя."""
        user = UserFactory()
        assert user.pk is not None
        assert "@example.com" in user.email
        assert user.first_name
        assert user.last_name


@pytest.mark.django_db
class TestRoleModel:
    """Тесты модели Role."""

    def test_create_role(self):
        """Создание роли."""
        # autouse fixture уже создает роли, создаем уникальную
        role = Role.objects.create(name="custom_test_role", description="Тестовая роль")

        assert role.name == "custom_test_role"
        assert role.description == "Тестовая роль"

    def test_role_str_method(self, student_role):
        """Тест __str__ метода."""
        assert str(student_role) == "Студент"

    def test_role_name_unique(self, student_role):
        """Имя роли должно быть уникальным."""
        # Роль уже существует из fixture
        with pytest.raises(IntegrityError):
            Role.objects.create(name="student", description="Duplicate")

    def test_default_roles_exist(self, db):
        """Проверка наличия всех ролей (создаются автоматически через autouse fixture)."""
        roles = Role.objects.all()
        role_names = [role.name for role in roles]

        assert "student" in role_names
        assert "mentor" in role_names
        assert "reviewer" in role_names
        assert "manager" in role_names
        assert "admin" in role_names
        assert "support" in role_names


@pytest.mark.django_db
class TestExpertiseAreaModel:
    """Тесты модели ExpertiseArea."""

    def test_create_expertise_area(self):
        """Создание области экспертизы."""
        area = ExpertiseArea.objects.create(
            name="Python", description="Язык программирования Python"
        )

        assert area.name == "Python"
        assert area.description == "Язык программирования Python"

    def test_expertise_area_str_method(self):
        """Тест __str__ метода."""
        area = ExpertiseAreaFactory(name="Python")
        assert str(area) == "Python"


@pytest.mark.django_db
class TestStudentModel:
    """Тесты модели Student."""

    def test_create_student(self, student_role):
        """Создание студента."""
        # Создаем пользователя с ролью student - signal создаст профиль
        user = User.objects.create_user(
            email="newstudent@example.com", password="TestPass123!", role=student_role
        )

        # Получаем автоматически созданный профиль
        student = user.student

        # Обновляем поля
        student.phone = "+79991234567"
        student.country = "RU"
        student.city = "Moscow"
        student.bio = "Test bio"
        student.save()

        assert student.user == user
        assert student.phone == "+79991234567"
        assert student.country == "RU"
        assert student.city == "Moscow"
        assert student.bio == "Test bio"
        assert student.is_active is True

    def test_student_str_method(self, student_role):
        """Тест __str__ метода."""
        user = User.objects.create_user(
            email="student@example.com", password="TestPass123!", role=student_role
        )
        student = user.student
        assert str(student) == "Студент student@example.com"

    def test_student_one_to_one_with_user(self, student_role):
        """Студент имеет связь One-to-One с User."""
        user = User.objects.create_user(
            email="oneto one@example.com", password="TestPass123!", role=student_role
        )
        student = user.student

        assert user.student == student
        assert student.user == user

    def test_student_gender_choices(self, student_role):
        """Проверка допустимых значений пола."""
        # Валидные значения
        for idx, gender in enumerate(["male", "female", "other"]):
            user = User.objects.create_user(
                email=f"gender{idx}@example.com", password="TestPass123!", role=student_role
            )
            student = user.student
            student.gender = gender
            student.save()
            assert student.gender == gender


@pytest.mark.django_db
class TestReviewerModel:
    """Тесты модели Reviewer."""

    def test_create_reviewer(self, reviewer_role):
        """Создание ревьюера через signals."""
        user = User.objects.create_user(
            email="newreviewer@example.com", password="TestPass123!", role=reviewer_role
        )
        reviewer = user.reviewer

        # Обновляем bio
        reviewer.bio = "Experienced reviewer"
        reviewer.save()

        assert reviewer.user == user
        assert reviewer.bio == "Experienced reviewer"
        assert reviewer.is_active is True
        assert reviewer.total_reviews == 0
        assert reviewer.average_review_time == 0.0

    def test_reviewer_str_method(self, reviewer_role):
        """Тест __str__ метода."""
        user = User.objects.create_user(
            email="reviewer@example.com", password="TestPass123!", role=reviewer_role
        )
        reviewer = user.reviewer
        assert str(reviewer) == "reviewer@example.com — Проверок: 0"

    def test_reviewer_expertise_areas_many_to_many(self, reviewer_role):
        """Ревьюер может иметь несколько областей экспертизы."""
        user = User.objects.create_user(
            email="reviewer2@example.com", password="TestPass123!", role=reviewer_role
        )
        reviewer = user.reviewer
        area1 = ExpertiseAreaFactory(name="Python")
        area2 = ExpertiseAreaFactory(name="JavaScript")

        reviewer.expertise_areas.add(area1, area2)

        assert reviewer.expertise_areas.count() == 2
        assert area1 in reviewer.expertise_areas.all()
        assert area2 in reviewer.expertise_areas.all()

    def test_reviewer_average_review_time_default(self, reviewer_role):
        """Среднее время проверки по умолчанию."""
        user = User.objects.create_user(
            email="reviewer4@example.com", password="TestPass123!", role=reviewer_role
        )
        reviewer = user.reviewer
        assert reviewer.average_review_time == 0.0


@pytest.mark.django_db
class TestMentorModel:
    """Тесты модели Mentor."""

    def test_create_mentor(self, mentor_role):
        """Создание ментора через signals."""
        user = User.objects.create_user(
            email="newmentor@example.com", password="TestPass123!", role=mentor_role
        )
        mentor = user.mentor

        # Обновляем bio
        mentor.bio = "Experienced mentor"
        mentor.save()

        assert mentor.user == user
        assert mentor.bio == "Experienced mentor"
        assert mentor.is_active is True

    def test_mentor_str_method(self, mentor_role):
        """Тест __str__ метода."""
        user = User.objects.create_user(
            email="mentor@example.com", password="TestPass123!", role=mentor_role
        )
        mentor = user.mentor
        assert str(mentor) == "Ментор: mentor@example.com"

    def test_mentor_expertise_areas(self, mentor_role):
        """Ментор может иметь области экспертизы."""
        user = User.objects.create_user(
            email="mentor2@example.com", password="TestPass123!", role=mentor_role
        )
        mentor = user.mentor
        area = ExpertiseAreaFactory(name="Django")

        mentor.expertise_areas.add(area)

        assert mentor.expertise_areas.count() == 1
        assert area in mentor.expertise_areas.all()


@pytest.mark.django_db
class TestManagerModel:
    """Тесты модели Manager."""

    def test_create_manager(self, manager_role):
        """Создание менеджера через signals."""
        user = User.objects.create_user(
            email="newmanager@example.com", password="TestPass123!", role=manager_role
        )
        manager = user.manager

        # Обновляем bio
        manager.bio = "Platform manager"
        manager.save()

        assert manager.user == user
        assert manager.bio == "Platform manager"
        assert manager.is_active is True

    def test_manager_str_method(self, manager_role):
        """Тест __str__ метода."""
        user = User.objects.create_user(
            email="manager@example.com", password="TestPass123!", role=manager_role
        )
        manager = user.manager
        assert str(manager) == "Менеджер: manager@example.com"


@pytest.mark.django_db
class TestAdminModel:
    """Тесты модели Admin."""

    def test_create_admin(self, admin_role):
        """Создание администратора через signals."""
        user = User.objects.create_user(
            email="newadmin@example.com", password="TestPass123!", role=admin_role
        )
        admin = user.admin

        # Обновляем bio
        admin.bio = "System admin"
        admin.save()

        assert admin.user == user
        assert admin.bio == "System admin"
        assert admin.is_active is True

    def test_admin_str_method(self, admin_role):
        """Тест __str__ метода."""
        user = User.objects.create_user(
            email="admin@example.com", password="TestPass123!", role=admin_role
        )
        admin = user.admin
        assert str(admin) == "Админ: admin@example.com"

    def test_admin_user_is_staff(self, admin_role):
        """Админ должен иметь is_staff=True."""
        user = User.objects.create_user(
            email="admin2@example.com", password="TestPass123!", role=admin_role
        )
        admin = user.admin
        assert admin.user.is_staff is True


@pytest.mark.django_db
class TestSupportModel:
    """Тесты модели Support."""

    def test_create_support(self, support_role):
        """Создание поддержки через signals."""
        user = User.objects.create_user(
            email="newsupport@example.com", password="TestPass123!", role=support_role
        )
        support = user.support

        # Обновляем bio
        support.bio = "Support specialist"
        support.save()

        assert support.user == user
        assert support.bio == "Support specialist"
        assert support.is_active is True

    def test_support_str_method(self, support_role):
        """Тест __str__ метода."""
        user = User.objects.create_user(
            email="support@example.com", password="TestPass123!", role=support_role
        )
        support = user.support
        assert str(support) == "Поддержка: support@example.com"


@pytest.mark.django_db
class TestModelRelationships:
    """Тесты связей между моделями."""

    def test_user_has_single_role(self, student_role):
        """Пользователь имеет одну роль."""
        user = UserFactory(role=student_role)

        assert user.role == student_role
        assert user.role.name == "student"

    def test_role_can_have_multiple_users(self, student_role):
        """Роль может быть у нескольких пользователей."""
        user1 = UserFactory(role=student_role)
        user2 = UserFactory(role=student_role)

        assert student_role.users.count() >= 2
        assert user1 in student_role.users.all()
        assert user2 in student_role.users.all()

    def test_expertise_area_shared_by_reviewers_and_mentors(self, reviewer_role, mentor_role):
        """Область экспертизы может быть у ревьюера и ментора."""
        area = ExpertiseAreaFactory(name="Python")

        # Создаем ревьюера через signals
        user1 = User.objects.create_user(
            email="reviewer_shared@example.com", password="TestPass123!", role=reviewer_role
        )
        reviewer = user1.reviewer

        # Создаем ментора через signals
        user2 = User.objects.create_user(
            email="mentor_shared@example.com", password="TestPass123!", role=mentor_role
        )
        mentor = user2.mentor

        reviewer.expertise_areas.add(area)
        mentor.expertise_areas.add(area)

        assert area in reviewer.expertise_areas.all()
        assert area in mentor.expertise_areas.all()
