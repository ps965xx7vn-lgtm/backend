"""
Factory Boy фабрики для создания тестовых объектов.

Используются для быстрого создания тестовых данных.
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from authentication.models import ExpertiseArea, Manager, Mentor, Reviewer, Role, Student

User = get_user_model()


class RoleFactory(DjangoModelFactory):
    """Фабрика для создания ролей."""

    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = "student"
    description = factory.Faker("text", max_nb_chars=200)


class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False
    email_is_verified = False
    role = factory.SubFactory(RoleFactory, name="student")

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Устанавливает пароль для пользователя."""
        if create:
            if extracted:
                obj.set_password(extracted)
            else:
                obj.set_password("TestPass123!")
            obj.save()


class StaffUserFactory(UserFactory):
    """Фабрика для создания staff пользователей."""

    is_staff = True
    role = factory.SubFactory(RoleFactory, name="manager")


class SuperUserFactory(UserFactory):
    """Фабрика для создания superuser."""

    is_staff = True
    is_superuser = True
    role = factory.SubFactory(RoleFactory, name="manager")


class ExpertiseAreaFactory(DjangoModelFactory):
    """Фабрика для создания областей экспертизы."""

    class Meta:
        model = ExpertiseArea

    name = factory.Sequence(lambda n: f"Expertise {n}")
    description = factory.Faker("text", max_nb_chars=200)


class StudentFactory(DjangoModelFactory):
    """Фабрика для создания студентов."""

    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory, role__name="student")
    phone = factory.Faker("phone_number")
    country = "RU"
    city = factory.Faker("city")
    bio = factory.Faker("text", max_nb_chars=500)
    gender = factory.Iterator(["male", "female", "other"])
    is_active = True


class ReviewerFactory(DjangoModelFactory):
    """Фабрика для создания ревьюеров."""

    class Meta:
        model = Reviewer

    user = factory.SubFactory(UserFactory, role__name="reviewer")
    bio = factory.Faker("text", max_nb_chars=500)
    is_active = True
    total_reviews = factory.Faker("random_int", min=0, max=100)
    average_review_time = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)


class MentorFactory(DjangoModelFactory):
    """Фабрика для создания менторов."""

    class Meta:
        model = Mentor

    user = factory.SubFactory(UserFactory, role__name="mentor")
    bio = factory.Faker("text", max_nb_chars=500)
    is_active = True


class ManagerFactory(DjangoModelFactory):
    """Фабрика для создания менеджеров."""

    class Meta:
        model = Manager

    user = factory.SubFactory(UserFactory, role__name="manager")
    bio = factory.Faker("text", max_nb_chars=500)
    is_active = True
