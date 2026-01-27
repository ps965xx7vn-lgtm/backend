"""
Courses Models Module - Модели данных для управления курсами и уроками.

Этот модуль определяет иерархическую структуру обучающего контента:

Модели:
    Course - Основная модель курса (название, описание, цена, статус)
    Lesson - Урок внутри курса
    Step - Шаг (элемент) внутри урока
    StepProgress - Прогресс студента по шагу
    LessonSubmission - Отправленная работа студента на проверку
    Tip - Подсказка к шагу
    ExtraSource - Дополнительный источник информации

Иерархия:
    Course → Lesson → Step → (Tip, ExtraSource)
                    → StepProgress (прогресс студента)
           → LessonSubmission (отправленные работы)

Статусы проверки (LessonSubmission):
    - pending: Ожидает проверки
    - changes_requested: Требуются исправления
    - approved: Одобрено

Особенности:
    - Использование UUID для первичных ключей
    - Slug-based URL для SEO
    - Кеширование прогресса студентов
    - Автоматическая генерация slug
    - Поддержка различных статусов курсов (draft, active, archived)

Автор: Pyland Team
Дата: 2025
"""

import uuid

from django.db import models
from django.db.models import Count, Q
from django.template.defaultfilters import slugify
from django.urls import reverse

from students.cache_utils import safe_cache_delete, safe_cache_get, safe_cache_set


class Course(models.Model):
    """
    Модель курса с названием, описанием, изображением и уникальным slug.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Название курса", verbose_name="Название")
    description = models.TextField(blank=True, help_text="Описание курса", verbose_name="Описание")
    short_description = models.CharField(
        max_length=350,
        blank=True,
        help_text="Краткое описание курса",
        verbose_name="Краткое описание",
    )
    image = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True,
        help_text="Обложка курса",
        verbose_name="Изображение",
    )
    slug = models.SlugField(unique=True, help_text="Уникальный slug курса", verbose_name="Slug")

    # Дополнительные поля
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Цена курса (0 = бесплатно)",
        verbose_name="Цена",
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("web", "Веб-разработка"),
            ("data-science", "Data Science"),
            ("other", "Другое"),
        ],
        default="python",
        help_text="Категория курса",
        verbose_name="Категория",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=5.0,
        help_text="Рейтинг курса (0-5)",
        verbose_name="Рейтинг",
    )
    is_featured = models.BooleanField(
        default=False, help_text="Отображать как 'Хит' или 'Новый'", verbose_name="Избранный"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Активный"),
            ("draft", "Черновик"),
            ("archived", "Архив"),
            ("coming_soon", "Скоро"),
        ],
        default="active",
        help_text="Статус курса",
        verbose_name="Статус",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата создания курса", verbose_name="Создан"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Дата последнего обновления курса", verbose_name="Обновлен"
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("courses:course_detail", kwargs={"course_slug": self.slug})

    def __str__(self) -> str:
        return self.name

    def get_progress_for_profile(self, profile, use_cache=True):
        """
        Возвращает словарь со статистикой прогресса по курсу для указанного профиля.
        Использует кэширование для оптимизации повторных вычислений.

        Keys: total_steps, completed_steps, completion_percentage,
              total_lessons, completed_lessons, last_activity
        """
        cache_key = f"course_progress_{self.id}_{profile.id}"

        if use_cache:
            cached_result = safe_cache_get(cache_key)
            if cached_result is not None:
                return cached_result

        from reviewers.models import StepProgress

        # Оптимизированный запрос с prefetch
        total_steps = self.lessons.aggregate(total=Count("steps"))["total"] or 0

        completed_steps = StepProgress.objects.filter(
            profile=profile,
            step__lesson__course=self,
            is_completed=True,
        ).count()

        completion_percentage = (
            round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
        )

        lessons_qs = self.lessons.annotate(
            total_steps=Count("steps", distinct=True),
            completed_steps=Count(
                "steps__progress",
                filter=Q(steps__progress__profile=profile, steps__progress__is_completed=True),
                distinct=True,
            ),
        )

        total_lessons = lessons_qs.count()
        completed_lessons = 0
        for lesson_item in lessons_qs:
            if (
                lesson_item.total_steps > 0
                and lesson_item.total_steps == lesson_item.completed_steps
            ):
                completed_lessons += 1

        last_activity = (
            StepProgress.objects.filter(
                profile=profile, step__lesson__course=self, is_completed=True
            )
            .order_by("-completed_at")
            .first()
        )

        result = {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "completion_percentage": (
                int(completion_percentage) if completion_percentage is not None else 0
            ),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "last_activity": last_activity,
        }

        # Кэшируем результат на 15 минут
        if use_cache:
            safe_cache_set(cache_key, result, 60 * 15)

        return result

    def invalidate_progress_cache(self, profile):
        """Инвалидирует кэш прогресса для конкретного профиля"""
        cache_key = f"course_progress_{self.id}_{profile.id}"
        safe_cache_delete(cache_key)

    def get_progress_for_profiles(self, profiles):
        """
        Оптимизированное получение прогресса для нескольких профилей сразу.
        Возвращает словарь {profile_id: progress_data}
        """
        from reviewers.models import StepProgress

        profiles_dict = {p.id: p for p in profiles}
        result = {}

        # Получаем все данные одним запросом
        progress_data = (
            StepProgress.objects.filter(
                profile__in=profiles, step__lesson__course=self, is_completed=True
            )
            .values("profile_id")
            .annotate(completed_count=Count("id"))
        )

        total_steps = self.lessons.aggregate(total=Count("steps"))["total"] or 0

        # Формируем результат для каждого профиля
        progress_by_profile = {
            item["profile_id"]: item["completed_count"] for item in progress_data
        }

        for profile_id, profile in profiles_dict.items():
            completed_steps = progress_by_profile.get(profile_id, 0)
            completion_percentage = (
                round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
            )

            result[profile_id] = {
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "completion_percentage": int(completion_percentage),
                "profile": profile,
            }

        return result


class Lesson(models.Model):
    """
    Модель урока, связанного с курсом.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Название урока", verbose_name="Название")
    course = models.ForeignKey(
        Course,
        related_name="lessons",
        on_delete=models.CASCADE,
        help_text="Курс",
        verbose_name="Курс",
    )
    slug = models.SlugField(unique=True, help_text="Уникальный slug урока", verbose_name="Slug")
    lesson_number = models.PositiveIntegerField(
        default=1, help_text="Порядковый номер урока в курсе", verbose_name="№ урока"
    )
    short_description = models.CharField(
        max_length=350,
        blank=True,
        help_text="Краткое описание урока",
        verbose_name="Краткое описание",
    )
    image = models.ImageField(
        upload_to="lessons/",
        blank=True,
        null=True,
        help_text="Обложка урока",
        verbose_name="Изображение",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата создания урока", verbose_name="Создан"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Дата последнего обновления урока", verbose_name="Обновлен"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["lesson_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "lesson_number"], name="unique_lesson_number_per_course"
            )
        ]
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["lesson_number"]),
        ]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.pk:
            last_lesson = (
                Lesson.objects.filter(course=self.course).order_by("-lesson_number").first()
            )
            self.lesson_number = (last_lesson.lesson_number + 1) if last_lesson else 1
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse(
            "courses:lesson_detail",
            kwargs={"course_slug": self.course.slug, "lesson_slug": self.slug},
        )

    def __str__(self) -> str:
        return f"{self.course.name} — {self.name}"

    def get_progress_for_profile(self, profile, use_cache=True):
        """
        Возвращает статистику прогресса по уроку для указанного профиля.
        Использует кэширование для оптимизации повторных вычислений.

        Keys: total_steps, completed_steps, completion_percentage, is_completed
        """
        cache_key = f"lesson_progress_{self.id}_{profile.id}"

        if use_cache:
            cached_result = safe_cache_get(cache_key)
            if cached_result is not None:
                return cached_result

        from reviewers.models import StepProgress

        total_steps = self.steps.count()
        completed_steps = StepProgress.objects.filter(
            profile=profile, step__lesson=self, is_completed=True
        ).count()
        completion_percentage = (
            round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
        )
        is_completed = total_steps > 0 and completed_steps == total_steps

        result = {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "completion_percentage": (
                int(completion_percentage) if completion_percentage is not None else 0
            ),
            "is_completed": is_completed,
        }

        # Кэшируем результат на 15 минут
        if use_cache:
            safe_cache_set(cache_key, result, 60 * 15)

        return result

    def invalidate_progress_cache(self, profile):
        """Инвалидирует кэш прогресса для конкретного профиля"""
        cache_key = f"lesson_progress_{self.id}_{profile.id}"
        safe_cache_delete(cache_key)
        # Также инвалидируем кэш курса
        self.course.invalidate_progress_cache(profile)


class Step(models.Model):
    """
    Модель шага урока, связанного с конкретным уроком.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Название шага", verbose_name="Название")
    lesson = models.ForeignKey(
        "Lesson",
        related_name="steps",
        on_delete=models.CASCADE,
        help_text="Урок",
        verbose_name="Урок",
    )
    step_number = models.PositiveIntegerField(
        default=1, help_text="Порядковый номер шага в уроке", verbose_name="№ шага"
    )
    description = models.TextField(blank=True, help_text="Описание шага", verbose_name="Описание")
    actions = models.TextField(blank=True, help_text="Действия шага", verbose_name="Действия")
    self_check = models.TextField(
        blank=True, help_text="Проверка себя", verbose_name="Проверка себя"
    )
    repair_description = models.CharField(
        max_length=200, blank=True, help_text="Описание ремонта", verbose_name="Описание ремонта"
    )
    image = models.ImageField(
        upload_to="steps/",
        blank=True,
        null=True,
        help_text="Изображение шага",
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "Шаг урока"
        verbose_name_plural = "Шаги урока"
        ordering = ["step_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "step_number"], name="unique_step_number_per_lesson"
            )
        ]
        indexes = [
            models.Index(fields=["lesson"]),
            models.Index(fields=["step_number"]),
        ]

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            last_step = Step.objects.filter(lesson=self.lesson).order_by("-step_number").first()
            self.step_number = (last_step.step_number + 1) if last_step else 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.lesson.name} — {self.name}"


class Tip(models.Model):
    """
    Модель совета, привязанного к шагу урока.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Заголовок совета", verbose_name="Заголовок")
    description = models.TextField(help_text="Описание совета", verbose_name="Описание")
    step = models.ForeignKey(
        Step,
        related_name="tips",
        on_delete=models.CASCADE,
        help_text="Шаг урока",
        verbose_name="Шаг",
    )

    class Meta:
        verbose_name = "Совет"
        verbose_name_plural = "Советы"
        indexes = [
            models.Index(fields=["step"]),
        ]

    def __str__(self) -> str:
        return self.title


class ExtraSource(models.Model):
    """
    Модель дополнительного источника для шагов урока.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Название источника", verbose_name="Название")
    url = models.URLField(blank=True, help_text="Ссылка на источник", verbose_name="Ссылка")
    steps = models.ManyToManyField(
        Step,
        related_name="extra_sources",
        blank=True,
        help_text="Шаги, к которым относится источник",
        verbose_name="Шаги",
    )

    class Meta:
        verbose_name = "Дополнительный источник"
        verbose_name_plural = "Дополнительные источники"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name
