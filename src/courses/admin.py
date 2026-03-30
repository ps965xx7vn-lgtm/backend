"""
Courses Admin Module - Административный интерфейс Django для управления курсами.

Этот модуль содержит настройки Django Admin для всех моделей курсов:

ModelAdmin классы:
    - CourseAdmin: Управление курсами с inline уроками
    - LessonAdmin: Управление уроками с inline шагами
    - StepAdmin: Управление шагами уроков
    - StepProgressAdmin: Просмотр прогресса студентов
    - LessonSubmissionAdmin: Управление отправленными работами
    - TipAdmin: Управление подсказками к шагам
    - ExtraSourceAdmin: Управление дополнительными материалами

Особенности:
    - Inline редактирование иерархии (курс → урок → шаг)
    - Списковые фильтры по статусу, дате, автору
    - Кастомные действия для базовых операций
    - Отображение счетчиков (количество шагов, студентов)
    - Ссылки на связанные объекты

Автор: Pyland Team
Дата: 2025
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from reviewers.models import LessonSubmission, StepProgress

from .models import Course, ExtraSource, Lesson, Step, Tip


class LessonInline(admin.TabularInline):
    """
    Inline-редактор для уроков, связанных с курсом.
    Позволяет редактировать уроки прямо на странице курса.
    """

    model = Lesson
    extra = 0
    fields = ("name", "lesson_number", "slug", "steps_count", "created_at")
    readonly_fields = ("created_at", "updated_at", "steps_count")
    show_change_link = True

    @admin.display(description="Шагов")
    def steps_count(self, obj):
        """Количество шагов в уроке"""
        if obj.id:
            count = obj.steps.count()
            return format_html('<span style="font-weight: bold;">{}</span>', count)
        return "-"


class StepInline(admin.TabularInline):
    """
    Inline-редактор для шагов, связанных с уроком.
    Позволяет редактировать шаги прямо на странице урока.
    """

    model = Step
    extra = 0
    fields = ("name", "step_number", "description", "has_image")
    readonly_fields = ("has_image",)
    show_change_link = True

    @admin.display(description="Изображение")
    def has_image(self, obj):
        """Есть ли изображение"""
        if obj.image:
            return format_html('<span style="color: #10b981;">✓ Есть</span>')
        return format_html('<span style="color: #6b7280;">✗ Нет</span>')


class TipInline(admin.TabularInline):
    """
    Inline-редактор для советов, связанных с шагом.
    Позволяет добавлять советы прямо на страницу шага.
    """

    model = Tip
    extra = 1
    fields = ("title", "description")


class LessonSubmissionInline(admin.TabularInline):
    """Inline для отправленных работ студентов на странице урока"""

    model = LessonSubmission
    extra = 0
    fields = ("edit_link", "student_link", "status", "mentor", "submitted_at")
    readonly_fields = ("edit_link", "student_link", "submitted_at")
    can_delete = False

    @admin.display(description="Действия")
    def edit_link(self, obj):
        """Ссылка на редактирование работы"""
        if not obj.id:
            return "-"
        url = reverse("admin:reviewers_lessonsubmission_change", args=[obj.id])
        return format_html(
            '<a href="{}" style="display: inline-flex; align-items: center; gap: 0.5rem; '
            'color: #3b82f6; font-weight: 600; text-decoration: none;">'
            '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="flex-shrink: 0;">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>'
            "</svg>"
            "Редактировать</a>",
            url,
        )

    @admin.display(description="Студент")
    def student_link(self, obj):
        """Ссылка на студента"""
        if not obj.student:
            return "-"
        url = reverse("admin:authentication_student_change", args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.user.username)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничиваем выбор ментора только пользователями с ролью 'Ментор'"""
        if db_field.name == "mentor":
            from authentication.models import Role, Student

            # Получаем роль ментора (точное совпадение или частичное)
            mentor_role = Role.objects.filter(name__icontains="ментор").first()
            if mentor_role:
                # Фильтруем только профили с этой ролью
                kwargs["queryset"] = (
                    Student.objects.filter(roles=mentor_role)
                    .select_related("user")
                    .order_by("user__username")
                )
            else:
                # Если роли нет, показываем всех пользователей для отладки
                # В продакшене должно быть Student.objects.none()
                kwargs["queryset"] = (
                    Student.objects.all().select_related("user").order_by("user__username")
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Админка для модели Course.

    Позволяет просматривать, искать и фильтровать курсы, а также редактировать связанные уроки (Lesson) прямо на странице курса.
    В списке отображаются название, slug и даты создания/обновления. Slug генерируется автоматически по названию.
    """

    list_display = (
        "name",
        "slug",
        "status_display",
        "category",
        "price_display",
        "rating",
        "lessons_count",
        "total_steps_count",
        "students_count",
        "is_featured",
        "created_at",
    )
    search_fields = ("name", "slug", "description")
    list_filter = ("status", "created_at", "updated_at", "category", "is_featured")
    readonly_fields = ("created_at", "updated_at", "course_stats")
    inlines = [LessonInline]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)

    actions = ["duplicate_course"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "slug", "description", "short_description", "image")},
        ),
        ("Настройки курса", {"fields": ("status", "category", "price", "rating", "is_featured")}),
        ("Статистика", {"fields": ("course_stats",), "classes": ("collapse",)}),
        ("Системная информация", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Статус")
    def status_display(self, obj):
        """Отображение статуса курса"""
        status_colors = {
            "active": "#10b981",
            "draft": "#fbbf24",
            "archived": "#6b7280",
            "coming_soon": "#8b5cf6",
        }
        status_labels = {
            "active": "Активный",
            "draft": "Черновик",
            "archived": "Архив",
            "coming_soon": "Скоро",
        }
        color = status_colors.get(obj.status, "#6b7280")
        label = status_labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color,
            label,
        )

    @admin.display(description="Уроков")
    def lessons_count(self, obj):
        """Количество уроков"""
        count = obj.lessons.count()
        return format_html(
            '<span style="background: #3b82f6; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            count,
        )

    @admin.display(description="Цена")
    def price_display(self, obj):
        """Отображение цены"""
        if obj.price == 0:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-weight: bold;">Бесплатно</span>'
            )
        return format_html(
            '<span style="background: #0ea5e9; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-weight: bold;">${}</span>',
            obj.price,
        )

    @admin.display(description="Всего шагов")
    def total_steps_count(self, obj):
        """Общее количество шагов"""
        count = Step.objects.filter(lesson__course=obj).count()
        return format_html("<strong>{}</strong>", count)

    @admin.display(description="Студентов")
    def students_count(self, obj):
        """Количество студентов"""
        count = obj.student_enrollments.count()
        return format_html('<span style="color: #10b981; font-weight: bold;">👥 {}</span>', count)

    @admin.display(description="Статистика")
    def course_stats(self, obj):
        """Детальная статистика курса"""
        if not obj.id:
            return "Курс еще не создан"

        lessons_count = obj.lessons.count()
        steps_count = Step.objects.filter(lesson__course=obj).count()
        students_count = obj.student_enrollments.count()
        submissions_count = LessonSubmission.objects.filter(lesson__course=obj).count()

        # Прогресс студентов
        total_progress = StepProgress.objects.filter(step__lesson__course=obj).count()
        completed_progress = StepProgress.objects.filter(
            step__lesson__course=obj, is_completed=True
        ).count()

        completion_rate = (completed_progress / total_progress * 100) if total_progress > 0 else 0

        return format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'color: white; padding: 20px; border-radius: 10px;">'
            '<h3 style="margin-top: 0; color: white;">📊 Статистика курса</h3>'
            '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px;">'
            '<div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">'
            '<div style="font-size: 32px; font-weight: bold; margin-bottom: 5px;">{}</div>'
            '<div style="font-size: 14px; opacity: 0.9;">Уроков</div>'
            "</div>"
            '<div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">'
            '<div style="font-size: 32px; font-weight: bold; margin-bottom: 5px;">{}</div>'
            '<div style="font-size: 14px; opacity: 0.9;">Шагов</div>'
            "</div>"
            '<div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">'
            '<div style="font-size: 32px; font-weight: bold; margin-bottom: 5px;">👥 {}</div>'
            '<div style="font-size: 14px; opacity: 0.9;">Студентов</div>'
            "</div>"
            "</div>"
            '<div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px;">'
            '<div style="margin-bottom: 10px;"><strong>📤 Отправлено работ:</strong> {}</div>'
            '<div style="margin-bottom: 10px;"><strong>✓ Выполнено заданий:</strong> {} / {}</div>'
            "<div><strong>📈 Средний прогресс:</strong> {:.1f}%</div>"
            "</div>"
            "</div>",
            lessons_count,
            steps_count,
            students_count,
            submissions_count,
            completed_progress,
            total_progress,
            completion_rate,
        )

    @admin.action(description="📋 Дублировать курс")
    def duplicate_course(self, request, queryset):
        """Дублирование курса"""
        for course in queryset:
            self.message_user(request, f"Дублирование курса '{course.name}' (функция в разработке)")

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.prefetch_related("lessons", "student_enrollments")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Админка для модели Lesson.

    Позволяет управлять уроками, связанными с курсами. В списке отображаются название, курс, номер урока, slug и даты.
    Можно искать по названию и курсу, а также редактировать шаги (Step) прямо на странице урока.
    """

    list_display = (
        "name",
        "course_link",
        "lesson_number",
        "slug",
        "steps_count",
        "submissions_count",
        "created_at",
    )
    search_fields = ("name", "slug", "course__name", "short_description")
    list_filter = ("course", "created_at")
    readonly_fields = ("created_at", "updated_at", "lesson_stats")
    inlines = [StepInline, LessonSubmissionInline]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("course", "lesson_number")

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "course", "lesson_number", "slug")},
        ),
        ("Описание", {"fields": ("short_description", "image")}),
        ("Статистика", {"fields": ("lesson_stats",), "classes": ("collapse",)}),
        ("Системная информация", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Курс")
    def course_link(self, obj):
        """Ссылка на курс"""
        url = reverse("admin:courses_course_change", args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', url, obj.course.name)

    @admin.display(description="Шагов")
    def steps_count(self, obj):
        """Количество шагов"""
        count = obj.steps.count()
        return format_html(
            '<span style="background: #10b981; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            count,
        )

    @admin.display(description="Работ отправлено")
    def submissions_count(self, obj):
        """Количество отправленных работ"""
        count = obj.submissions.count()
        return format_html("<strong>📤 {}</strong>", count)

    @admin.display(description="Статистика")
    def lesson_stats(self, obj):
        """Статистика урока"""
        if not obj.id:
            return "Урок еще не создан"

        steps_count = obj.steps.count()
        submissions_count = obj.submissions.count()

        total_progress = StepProgress.objects.filter(step__lesson=obj).count()
        completed_progress = StepProgress.objects.filter(
            step__lesson=obj, is_completed=True
        ).count()

        completion_rate = (completed_progress / total_progress * 100) if total_progress > 0 else 0

        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">'
            '<h4 style="margin-top: 0;">📊 Статистика урока</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">'
            "<div><strong>Шагов:</strong> {}</div>"
            "<div><strong>Работ:</strong> {}</div>"
            "<div><strong>Выполнено:</strong> {} / {}</div>"
            "<div><strong>Прогресс:</strong> {:.1f}%</div>"
            "</div>"
            "</div>",
            steps_count,
            submissions_count,
            completed_progress,
            total_progress,
            completion_rate,
        )

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related("course").prefetch_related("steps", "submissions")


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    """
    Админка для модели Step.

    Позволяет управлять шагами урока. В списке отображаются название, урок, номер шага, описание, действия, проверка себя и изображение.
    Можно искать по названию и фильтровать по уроку.
    """

    list_display = (
        "name",
        "lesson_link",
        "step_number",
        "has_description",
        "has_image",
        "completion_rate",
    )
    search_fields = ("name", "lesson__name", "description")
    list_filter = ("lesson__course", "lesson")
    ordering = ("lesson", "step_number")
    readonly_fields = ("step_stats",)
    inlines = [TipInline]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "lesson", "step_number")}),
        (
            "Контент",
            {
                "fields": (
                    "description",
                    "actions",
                    "self_check",
                    "self_check_items",
                    "image",
                    "articles",
                )
            },
        ),
        (
            "Помощь студентам",
            {
                "fields": ("troubleshooting_help",),
                "description": "Подсказки, которые видят студенты при возникновении проблем",
            },
        ),
        (
            "Административные поля",
            {
                "fields": ("repair_description",),
                "classes": ("collapse",),
                "description": "Служебные поля для администратора (не видны студентам)",
            },
        ),
        ("Статистика", {"fields": ("step_stats",), "classes": ("collapse",)}),
    )

    @admin.display(description="Урок")
    def lesson_link(self, obj):
        """Ссылка на урок"""
        url = reverse("admin:courses_lesson_change", args=[obj.lesson.id])
        return format_html('<a href="{}">{} ({})</a>', url, obj.lesson.name, obj.lesson.course.name)

    @admin.display(description="Описание")
    def has_description(self, obj):
        """Есть ли описание"""
        if obj.description:
            return format_html('<span style="color: #10b981;">✓</span>')
        return format_html('<span style="color: #ef4444;">✗</span>')

    @admin.display(description="Изображение")
    def has_image(self, obj):
        """Есть ли изображение"""
        if obj.image:
            return format_html('<span style="color: #10b981;">✓</span>')
        return format_html('<span style="color: #6b7280;">✗</span>')

    @admin.display(description="Завершено")
    def completion_rate(self, obj):
        """Процент завершения"""
        total = obj.progress.count()
        if total == 0:
            return "-"

        completed = obj.progress.filter(is_completed=True).count()
        rate = completed / total * 100

        color = "#10b981" if rate >= 70 else "#f59e0b" if rate >= 40 else "#ef4444"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>', color, int(rate)
        )

    @admin.display(description="Статистика")
    def step_stats(self, obj):
        """Статистика шага"""
        if not obj.id:
            return "Шаг еще не создан"

        total_users = obj.progress.count()
        completed_users = obj.progress.filter(is_completed=True).count()
        tips_count = obj.tips.count()

        completion_rate = (completed_users / total_users * 100) if total_users > 0 else 0

        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            '<h4 style="margin-top: 0;">📊 Статистика шага</h4>'
            "<div><strong>Пользователей начало:</strong> {}</div>"
            "<div><strong>Завершили:</strong> {} ({:.1f}%)</div>"
            "<div><strong>Советов:</strong> {}</div>"
            "</div>",
            total_users,
            completed_users,
            completion_rate,
            tips_count,
        )

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related("lesson", "lesson__course").prefetch_related("progress", "tips")


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    """
    Админка для модели Tip.

    Позволяет просматривать и редактировать советы, связанные с шагами урока. В списке отображаются заголовок, шаг и описание.
    Доступен поиск по заголовку и фильтрация по шагу.
    """

    list_display = ("title", "step_link", "has_description")
    search_fields = ("title", "step__name", "description")
    list_filter = ("step__lesson__course", "step__lesson")

    @admin.display(description="Шаг")
    def step_link(self, obj):
        """Ссылка на шаг"""
        url = reverse("admin:courses_step_change", args=[obj.step.id])
        return format_html('<a href="{}">{}</a>', url, obj.step.name)

    @admin.display(description="Описание")
    def has_description(self, obj):
        """Есть ли описание"""
        if obj.description:
            return format_html('<span style="color: #10b981;">✓</span>')
        return format_html('<span style="color: #6b7280;">✗</span>')


@admin.register(ExtraSource)
class ExtraSourceAdmin(admin.ModelAdmin):
    """
    Админка для модели ExtraSource.

    Позволяет управлять дополнительными источниками для шагов урока. В списке отображаются название и ссылка.
    Можно искать по названию и ссылке, а также связывать источники с шагами через интерфейс "многие ко многим".
    """

    list_display = ("name", "url_link", "steps_count")
    search_fields = ("name", "url")
    filter_horizontal = ("steps",)

    @admin.display(description="URL")
    def url_link(self, obj):
        """Кликабельная ссылка"""
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)

    @admin.display(description="Используется в шагах")
    def steps_count(self, obj):
        """Количество шагов"""
        count = obj.steps.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)


@admin.register(StepProgress)
class StepProgressAdmin(admin.ModelAdmin):
    """Админка для прогресса по шагам"""

    list_display = ("profile_link", "step_link", "completion_status", "completed_at")
    search_fields = ("profile__user__username", "profile__user__email", "step__name")
    list_filter = (
        "is_completed",
        "step__lesson__course",
        "step__lesson",
        "completed_at",
    )
    ordering = ("-completed_at",)
    readonly_fields = ("completed_at",)

    @admin.display(description="Студент")
    def profile_link(self, obj):
        """Ссылка на профиль"""
        url = reverse("admin:students_student_change", args=[obj.profile.id])
        return format_html('<a href="{}">{}</a>', url, obj.profile.user.username)

    @admin.display(description="Шаг")
    def step_link(self, obj):
        """Ссылка на шаг"""
        url = reverse("admin:courses_step_change", args=[obj.step.id])
        return format_html('<a href="{}">{} → {}</a>', url, obj.step.lesson.name, obj.step.name)

    @admin.display(description="Статус")
    def completion_status(self, obj):
        """Статус завершения"""
        if obj.is_completed:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-weight: bold;">✓ Выполнено</span>'
            )
        return format_html(
            '<span style="background: #6b7280; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold;">○ В процессе</span>'
        )

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related(
            "profile", "profile__user", "step", "step__lesson", "step__lesson__course"
        )
