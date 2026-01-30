"""
Auth Models Module - Модели данных для системы аутентификации и ролей пользователей.

Этот модуль определяет базовые модели для управления пользователями:
    - User: Кастомная модель пользователя с аутентификацией по email
    - CustomUserManager: Менеджер для создания пользователей и суперпользователей
    - Role: Роли пользователей (student, mentor, reviewer, manager, admin, support)
    - Student: Расширенный профиль студента
    - Reviewer: Расширенный профиль проверяющего

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


def get_default_student_role() -> int | None:
    """
    Получить ID дефолтной роли 'student' для новых пользователей.

    При регистрации пользователь сразу получает роль студента,
    что позволяет ему начать обучение без модерации.

    Returns:
        int: ID роли или None если роль не существует
    """
    try:
        from django.apps import apps

        Role = apps.get_model("authentication", "Role")
        role = Role.objects.get(name="student")
        return role.id
    except Exception:
        return None


class CustomUserManager(BaseUserManager):
    """
    Менеджер пользователей для кастомной модели User.

    Отвечает за создание обычных пользователей и суперпользователей
    с использованием email как основного идентификатора.
    """

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        """
        Создаёт и сохраняет пользователя с указанным email и паролем.

        Args:
            email: Email пользователя (обязательный)
            password: Пароль пользователя (если None — создаётся unusable password)
            extra_fields: Дополнительные поля модели

        Returns:
            User: Созданный объект пользователя

        Raises:
            ValueError: Если email не указан
        """
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user: User = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> User:
        """
        Создаёт суперпользователя с правами администратора.

        Args:
            email: Email суперпользователя
            password: Пароль суперпользователя
            extra_fields: Дополнительные поля модели

        Returns:
            User: Созданный суперпользователь
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя с аутентификацией по email и role-based системой.

    Расширяет стандартную модель Django AbstractUser, используя email
    как основной идентификатор вместо username. Система доступа основана
    на ролях, хранящихся прямо на User модели.

    Attributes:
        username: Опциональное имя пользователя (может быть null)
        email: Уникальный email адрес (основной идентификатор)
        email_is_verified: Флаг подтверждения email адреса
        role: Роль пользователя (ForeignKey на Role)
        courses: Курсы, на которые зарегистрирован пользователь
        is_staff: Флаг для доступа в Django Admin (используется только для админов)
        is_superuser: Флаг суперпользователя

    Roles:
        Доступные роли: student, mentor, reviewer, manager, admin, support
        Каждый пользователь имеет одну роль, определяемую через FK Role.
    """

    username: str | None = models.CharField(max_length=150, blank=True, null=True)
    email: str = models.EmailField(unique=True)
    email_is_verified: bool = models.BooleanField(default=False)
    role: Role | None = models.ForeignKey(
        "Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        default=get_default_student_role,
        related_name="users",
        verbose_name="Роль",
        help_text="Роль пользователя в системе (по умолчанию: student)",
    )
    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS: list[str] = []

    objects: CustomUserManager = CustomUserManager()

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        return self.email

    @property
    def role_name(self) -> str | None:
        """
        Получить название роли пользователя.

        Returns:
            Optional[str]: Название роли (student, mentor, reviewer и т.д.) или None

        Example:
            >>> if user.role_name == 'admin':
            ...     show_admin_panel()
        """
        return self.role.name if self.role else None

    def has_role(self, role_name: str) -> bool:
        """
        Проверить есть ли у пользователя указанная роль.

        Args:
            role_name: Название роли для проверки

        Returns:
            bool: True если роль совпадает, иначе False

        Example:
            >>> if user.has_role('reviewer'):
            ...     allow_review_action()
        """
        return self.role_name == role_name

    def has_active_newsletter_subscription(self) -> bool:
        """
        Проверить есть ли у пользователя активная подписка на email уведомления.

        Note:
            Использует централизованную систему notifications.Subscription
            с типом 'email_notifications'

        Returns:
            bool: True если есть активная подписка, иначе False

        Example:
            >>> if not user.has_active_newsletter_subscription():
            ...     show_newsletter_signup()
        """
        try:
            from notifications.models import Subscription

            return Subscription.objects.filter(
                email=self.email, subscription_type="email_notifications", is_active=True
            ).exists()
        except Exception:
            return False

    def has_perm(self, perm: str, obj: Any = None) -> bool:
        """
        Проверка прав доступа для Django admin.

        Суперпользователи имеют все права.
        is_staff пользователи получают базовые права для admin панели.

        Args:
            perm: Название разрешения
            obj: Необязательный объект для проверки прав

        Returns:
            bool: True если пользователь имеет право
        """
        if self.is_active and self.is_superuser:
            return True
        return False

    def has_module_perms(self, app_label: str) -> bool:
        """
        Проверка прав доступа к модулю Django admin.

        Args:
            app_label: Название приложения Django

        Returns:
            bool: True если пользователь имеет право на модуль
        """
        if self.is_active and self.is_superuser:
            return True
        return False

    class Meta:
        verbose_name: str = "Пользователь"
        verbose_name_plural: str = "Пользователи"
        ordering: list[str] = ["-date_joined"]
        permissions: list = [
            ("view_user_details", "Может просматривать детали пользователей"),
            ("manage_user_roles", "Может управлять ролями пользователей"),
            ("verify_user_email", "Может верифицировать email пользователей"),
        ]
        indexes: list = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["-date_joined"]),
        ]


class Role(models.Model):
    """
    Модель роли пользователя в системе.

    Определяет различные роли пользователей с соответствующими правами доступа.
    Используется для управления доступом студентов к функциям.

    Attributes:
        name: Уникальное название роли (choice field)
        description: Подробное описание роли и её полномочий
    """

    # Константы для ролей
    STUDENT: str = "student"
    MENTOR: str = "mentor"
    REVIEWER: str = "reviewer"
    MANAGER: str = "manager"
    ADMIN: str = "admin"
    SUPPORT: str = "support"

    ROLE_CHOICES: list[tuple[str, str]] = [
        (STUDENT, "Студент"),
        (MENTOR, "Ментор"),
        (REVIEWER, "Ревьюер"),
        (MANAGER, "Менеджер"),
        (ADMIN, "Администратор"),
        (SUPPORT, "Поддержка"),
    ]

    name: str = models.CharField(
        max_length=50, unique=True, choices=ROLE_CHOICES, help_text="Название роли"
    )
    description: str = models.TextField(blank=True, help_text="Описание роли")

    def __str__(self) -> str:
        """Строковое представление роли."""
        return self.get_name_display()

    @classmethod
    def get_default_roles(cls) -> dict[str, str]:
        """
        Возвращает словарь с дефолтными ролями и их описаниями.

        Returns:
            dict: Словарь {название_роли: описание}
        """
        return {
            cls.STUDENT: "Студент - проходит курсы, изучает материалы, выполняет задания, отслеживает прогресс",
            cls.MENTOR: "Ментор - ведет курсы, консультирует студентов, проверяет задания, дает обратную связь",
            cls.REVIEWER: "Ревьюер - специализируется на проверке работ студентов, оставляет детальные комментарии и рекомендации",
            cls.MANAGER: "Менеджер - управляет платформой через dashboard: курсы, пользователи, статистика, настройки",
            cls.ADMIN: "Администратор - полный доступ к системе через Django Admin, управление всеми данными и пользователями",
            cls.SUPPORT: "Поддержка - обрабатывает обращения пользователей, решает технические вопросы, управляет тикетами",
        }

    class Meta:
        verbose_name: str = "Роль"
        verbose_name_plural: str = "Роли"
        ordering: list[str] = ["name"]
        permissions: list = [
            ("assign_roles", "Может назначать роли пользователям"),
            ("manage_roles", "Может создавать и изменять роли"),
        ]
        indexes: list = [
            models.Index(fields=["name"]),
        ]


class ExpertiseArea(models.Model):
    """
    Область экспертизы для менторов и ревьюеров.

    Определяет области знаний, в которых специализируются менторы и ревьюеры.
    Используется для назначения правильных специалистов на проверку работ.

    Attributes:
        name: Название области экспертизы (Python, Django, JavaScript и т.д.)
        description: Подробное описание области
        created_at: Дата создания
    """

    name: str = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название",
        help_text="Python, Django, JavaScript, React и т.д.",
    )
    description: str = models.TextField(
        blank=True, verbose_name="Описание", help_text="Подробное описание области экспертизы"
    )
    created_at: Any = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name: str = "Область экспертизы"
        verbose_name_plural: str = "Области экспертизы"
        ordering: list[str] = ["name"]
        permissions: list = [
            ("manage_expertise", "Может управлять областями экспертизы"),
        ]
        indexes: list = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        """Строковое представление области экспертизы."""
        return self.name


# Модель Student перенесена из приложения students
class Student(models.Model):
    """
    Расширенный профиль студента с персональной информацией.

    Связан с моделью User отношением One-to-One. Содержит дополнительные
    данные о студенте: персональную информацию, настройки уведомлений и приватности.
    Роль студента теперь хранится прямо на User модели.

    Attributes:
        id: UUID первичный ключ
        user: Связь с пользователем (OneToOne)

        Персональные данные:
            phone: Номер телефона
            birthday: Дата рождения
            gender: Пол пользователя (мужской/женский/другой)
            country: Страна проживания
            city: Город
            address: Адрес
            bio: Биография/описание студента
            avatar: Аватар пользователя

        Уведомления:
            email_notifications: Общие email уведомления
            course_updates: Уведомления об обновлениях курсов
            lesson_reminders: Напоминания о новых уроках
            achievement_alerts: Уведомления о достижениях
            weekly_summary: Еженедельная сводка прогресса
            marketing_emails: Маркетинговые рассылки

        Приватность:
            profile_visibility: Уровень видимости профиля
            show_progress: Показывать прогресс обучения
            show_achievements: Показывать достижения
            allow_messages: Разрешить личные сообщения
    """

    id: Any = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student", help_text="Пользователь"
    )

    # Персональные данные
    phone: str | None = PhoneNumberField(blank=True, null=True, help_text="Основной телефон")
    birthday: Any | None = models.DateField(null=True, blank=True, help_text="Дата рождения")
    gender: str = models.CharField(
        max_length=10,
        choices=[("male", "Мужской"), ("female", "Женский"), ("other", "Другой")],
        blank=True,
        help_text="Пол пользователя",
    )
    country: str = CountryField(blank=True, help_text="Страна")
    city: str = models.CharField(max_length=100, blank=True, help_text="Город")
    address: str = models.TextField(blank=True, help_text="Адрес")
    bio: str | None = models.TextField(blank=True, null=True, help_text="О себе")
    avatar: Any | None = models.ImageField(
        upload_to="avatars/", blank=True, null=True, help_text="Аватар"
    )

    # Настройки уведомлений
    email_notifications: bool = models.BooleanField(default=True, help_text="Уведомления по email")
    course_updates: bool = models.BooleanField(default=True, help_text="Обновления курсов")
    lesson_reminders: bool = models.BooleanField(default=True, help_text="Напоминания о уроках")
    achievement_alerts: bool = models.BooleanField(
        default=True, help_text="Уведомления о достижениях"
    )
    weekly_summary: bool = models.BooleanField(default=True, help_text="Еженедельная сводка")
    marketing_emails: bool = models.BooleanField(default=False, help_text="Маркетинговые письма")

    # Настройки приватности
    profile_visibility: str = models.CharField(
        max_length=20,
        choices=[
            ("public", "Публичный"),
            ("students", "Только студенты"),
            ("private", "Приватный"),
        ],
        default="students",
        help_text="Видимость профиля",
    )
    show_progress: bool = models.BooleanField(default=True, help_text="Показывать прогресс")
    show_achievements: bool = models.BooleanField(default=True, help_text="Показывать достижения")
    allow_messages: bool = models.BooleanField(default=True, help_text="Разрешить сообщения")

    # Статус активности
    is_active: bool = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Может ли студент получать доступ к курсам и отправлять задания",
    )

    courses: Any = models.ManyToManyField(
        "courses.Course",
        blank=True,
        related_name="student_enrollments",
        help_text="Курсы пользователя",
    )

    # Метаданные
    created_at: Any = models.DateTimeField(auto_now_add=True, help_text="Дата создания профиля")
    updated_at: Any = models.DateTimeField(auto_now=True, help_text="Дата последнего обновления")

    def __str__(self) -> str:
        """Строковое представление студента."""
        return f"Студент {self.user.email}"

    class Meta:
        verbose_name: str = "Студент"
        verbose_name_plural: str = "Студенты"
        ordering: list[str] = ["-created_at"]
        permissions: list = [
            ("view_own_progress", "Может просматривать свой прогресс обучения"),
            ("submit_assignments", "Может отправлять задания на проверку"),
            ("view_course_materials", "Может просматривать материалы курсов"),
            ("manage_own_profile", "Может управлять своим профилем"),
        ]
        indexes: list = [
            models.Index(fields=["user"]),
            models.Index(fields=["country"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["-created_at"]),
        ]


# Модель Reviewer перенесена из приложения reviewers (переименована из ReviewerProfile)
class Reviewer(models.Model):
    """
    Расширенный профиль ревьюера для проверки работ студентов.

    Содержит информацию об экспертизе и статистике проверок.
    Ревьюер проверяет работы студентов и оставляет подробные комментарии.

    Attributes:
        id: UUID первичный ключ
        user: Связь с пользователем (OneToOne)
        bio: Биография ревьюера и опыт работы
        expertise_areas: ManyToMany связь с областями экспертизы
        courses: Курсы, работы по которым может проверять
        is_active: Активен ли и может ли брать новые работы
        total_reviews: Общее количество проверенных работ
        average_review_time: Среднее время проверки в часах
        registered_at: Дата регистрации как ревьюер
        updated_at: Дата последнего обновления профиля
    """

    id: Any = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.OneToOneField(User, on_delete=models.CASCADE, related_name="reviewer")
    bio: str = models.TextField(
        blank=True, verbose_name="Биография", help_text="Информация о проверяющем, опыт работы"
    )
    expertise_areas: Any = models.ManyToManyField(
        "ExpertiseArea",
        related_name="reviewers",
        blank=True,
        verbose_name="Области экспертизы",
        help_text="Python, Django, JavaScript и т.д.",
    )
    courses: Any = models.ManyToManyField(
        "courses.Course",
        related_name="reviewers",
        blank=True,
        verbose_name="Курсы для проверки",
        help_text="Курсы, работы по которым может проверять этот ревьюер",
    )

    # Статистика
    is_active: bool = models.BooleanField(
        default=True, verbose_name="Активен", help_text="Может ли проверяющий брать новые работы"
    )
    total_reviews: int = models.PositiveIntegerField(default=0, verbose_name="Всего проверок")
    average_review_time: Any = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        verbose_name="Среднее время проверки (часы)",
        help_text="Среднее время от получения работы до проверки",
    )
    max_reviews_per_day: int = models.PositiveIntegerField(
        default=10,
        verbose_name="Макс. проверок в день",
        help_text="Максимальное количество работ которые можно проверить за день",
    )

    # Настройки уведомлений
    notify_new_submissions: bool = models.BooleanField(
        default=True,
        verbose_name="Уведомления о новых работах",
        help_text="Получать email когда студент отправляет работу на проверку",
    )

    # Метаданные
    registered_at: Any = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at: Any = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name: str = "Проверяющий"
        verbose_name_plural: str = "Проверяющие"
        ordering: list[str] = ["-registered_at"]
        permissions: list = [
            ("review_submissions", "Может проверять работы студентов"),
            ("approve_submissions", "Может одобрять работы"),
            ("reject_submissions", "Может отклонять работы с замечаниями"),
            ("view_all_submissions", "Может просматривать все работы на проверку"),
            ("manage_review_queue", "Может управлять очередью проверок"),
        ]
        indexes: list = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["-total_reviews"]),
            models.Index(fields=["-average_review_time"]),
        ]

    def __str__(self) -> str:
        """Строковое представление ревьюера с его статистикой."""
        return f"{self.user.email} — Проверок: {self.total_reviews}"

    def get_role_display(self) -> str:
        """
        Получить отображаемое название роли.

        Returns:
            str: 'Ревьюер', 'Ментор' или 'Проверяющий' по умолчанию
        """
        if self.user and self.user.role:
            role_name = self.user.role.name
            if role_name == "reviewer":
                return "Ревьюер"
            elif role_name == "mentor":
                return "Ментор"
        return "Проверяющий"

    def can_review_course(self, course: Any) -> bool:
        """
        Проверить, может ли ревьюер проверять работы по этому курсу.

        Args:
            course: Объект Course для проверки

        Returns:
            bool: True если активен и назначен на курс
        """
        return self.is_active and self.courses.filter(id=course.id).exists()

    def get_pending_count(self) -> int:
        """
        Получить количество работ в очереди на проверку.

        Returns:
            int: Количество работ со статусом 'pending'
        """
        from reviewers.models import LessonSubmission

        return LessonSubmission.objects.filter(review__reviewer=self, status="pending").count()

    def get_statistics(self) -> dict[str, Any]:
        """
        Получить детальную статистику ревьюера за последние 30 дней.

        Returns:
            dict: Словарь с ключами:
                - total_reviews: всего проверок всегда
                - recent_reviews: проверок за последние 30 дней
                - accepted_count: одобрено
                - rejected_count: требуют изменений
                - acceptance_rate: процент принятых работ
                - average_time: среднее время проверки
                - pending_count: работ в очереди
        """
        from django.utils import timezone

        from reviewers.models import LessonSubmission

        submissions = LessonSubmission.objects.filter(review__reviewer=self)

        month_ago = timezone.now() - timedelta(days=30)
        recent_submissions = submissions.filter(review__reviewed_at__gte=month_ago)

        total_reviews = submissions.count()
        approved = submissions.filter(status="approved").count()
        changes_requested = submissions.filter(status="changes_requested").count()

        return {
            "total_reviews": total_reviews,
            "recent_reviews": recent_submissions.count(),
            "accepted_count": approved,
            "rejected_count": changes_requested,
            "acceptance_rate": (approved / total_reviews * 100) if total_reviews > 0 else 0,
            "average_time": float(self.average_review_time),
            "pending_count": self.get_pending_count(),
        }


class Mentor(models.Model):
    """
    Профиль ментора для ведения курсов и поддержки студентов.

    Ментор помогает студентам в обучении, может быть назначен на курсы.
    Ведет обучение, консультирует студентов, проверяет задания.

    Attributes:
        id: UUID первичный ключ
        user: Связь с пользователем (OneToOne)
        bio: Биография ментора и опыт работы
        expertise_areas: ManyToMany связь с областями экспертизы
        courses: Курсы, которые ведёт ментор
        is_active: Активен ли и может ли брать новые курсы
        registered_at: Дата регистрации
        updated_at: Дата последнего обновления
    """

    id: Any = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mentor")
    bio: str = models.TextField(blank=True, verbose_name="Биография")
    expertise_areas: Any = models.ManyToManyField(
        "ExpertiseArea", related_name="mentors", blank=True, verbose_name="Области экспертизы"
    )
    courses: Any = models.ManyToManyField(
        "courses.Course", related_name="mentors", blank=True, verbose_name="Курсы"
    )
    is_active: bool = models.BooleanField(default=True, verbose_name="Активен")
    registered_at: Any = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at: Any = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name: str = "Ментор"
        verbose_name_plural: str = "Менторы"
        ordering: list[str] = ["-registered_at"]
        permissions: list = [
            ("manage_courses", "Может управлять курсами"),
            ("create_lessons", "Может создавать уроки"),
            ("edit_course_content", "Может редактировать контент курсов"),
            ("view_student_progress", "Может просматривать прогресс студентов"),
            ("mentor_students", "Может менторить студентов"),
        ]
        indexes: list = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """Строковое представление ментора."""
        return f"Ментор: {self.user.email}"


class Manager(models.Model):
    """
    Профиль менеджера платформы.

    Менеджер управляет платформой: курсы, пользователи, статистика.
    Имеет доступ к специальному dashboard для администрирования.

    Attributes:
        id: UUID первичный ключ
        user: Связь с пользователем (OneToOne)
        bio: Описание роли и опыта менеджера
        is_active: Активен ли в системе
        registered_at: Дата регистрации
        updated_at: Дата последнего обновления
    """

    id: Any = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.OneToOneField(User, on_delete=models.CASCADE, related_name="manager")
    bio: str = models.TextField(blank=True, verbose_name="Описание")
    is_active: bool = models.BooleanField(default=True, verbose_name="Активен")
    registered_at: Any = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at: Any = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name: str = "Менеджер"
        verbose_name_plural: str = "Менеджеры"
        ordering: list[str] = ["-registered_at"]
        permissions: list = [
            ("access_dashboard", "Доступ к менеджерской панели управления"),
            ("view_platform_stats", "Просмотр статистики платформы"),
            ("manage_users", "Управление пользователями платформы"),
            ("manage_feedback", "Управление обратной связью"),
            ("view_system_logs", "Просмотр системных логов"),
        ]
        indexes: list = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """Строковое представление менеджера."""
        return f"Менеджер: {self.user.email}"


class Admin(models.Model):
    """
    Профиль администратора системы.

    Администратор имеет полный доступ к Django Admin и управлению данными.
    Права управляются через Django флаги: `user.is_staff` и `user.is_superuser`.

    Attributes:
        id: UUID первичный ключ
        user: Связь с пользователем (OneToOne)
        bio: Описание роли и опыта администратора
        is_active: Активен ли в системе
        registered_at: Дата регистрации
        updated_at: Дата последнего обновления
    """

    id: Any = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")
    bio: str = models.TextField(blank=True, verbose_name="Описание")
    is_active: bool = models.BooleanField(default=True, verbose_name="Активен")
    registered_at: Any = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at: Any = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name: str = "Администратор"
        verbose_name_plural: str = "Администраторы"
        ordering: list[str] = ["-registered_at"]
        permissions: list = [
            ("full_system_access", "Полный доступ ко всей системе"),
            ("manage_all_data", "Управление всеми данными через Django Admin"),
            ("configure_system", "Настройка системных параметров"),
            ("manage_permissions", "Управление правами доступа"),
        ]
        indexes: list = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """Строковое представление администратора."""
        return f"Админ: {self.user.email}"


class Support(models.Model):
    """
    Профиль сотрудника поддержки.

    Поддержка обрабатывает обращения пользователей, решает проблемы,
    управляет тикетами и техническими вопросами.

    Attributes:
        id: UUID первичный ключ
        user: Связь с пользователем (OneToOne)
        bio: Описание роли и опыта сотрудника
        is_active: Активен ли в системе
        registered_at: Дата регистрации
        updated_at: Дата последнего обновления
    """

    id: Any = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: User = models.OneToOneField(User, on_delete=models.CASCADE, related_name="support")
    bio: str = models.TextField(blank=True, verbose_name="Описание")
    is_active: bool = models.BooleanField(default=True, verbose_name="Активен")
    registered_at: Any = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at: Any = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name: str = "Поддержка"
        verbose_name_plural: str = "Поддержка"
        ordering: list[str] = ["-registered_at"]
        permissions: list = [
            ("handle_support_tickets", "Обработка обращений пользователей"),
            ("resolve_user_issues", "Решение проблем пользователей"),
            ("view_support_queue", "Просмотр очереди обращений"),
            ("manage_tickets", "Управление тикетами поддержки"),
        ]
        indexes: list = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        """Строковое представление сотрудника поддержки."""
        return f"Поддержка: {self.user.email}"
