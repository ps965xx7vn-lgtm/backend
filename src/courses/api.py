"""
Courses API Module - REST API для управления курсами и уроками.

Этот модуль содержит эндпоинты для работы с курсами:

Endpoints:
    GET    /api/courses/                       - Список всех курсов
    GET    /api/courses/{id}                   - Детали курса
    POST   /api/courses/                       - Создание курса
    GET    /api/courses/{id}/lessons           - Уроки курса
    POST   /api/courses/lessons/               - Создание урока
    GET    /api/courses/lessons/{id}           - Детали урока
    POST   /api/courses/steps/                 - Создание шага
    GET    /api/courses/steps/{id}             - Детали шага
    GET    /api/courses/submissions/           - Список отправленных работ
    POST   /api/courses/submissions/{id}/resubmit - Повторная отправка
    POST   /api/courses/submissions/{id}/review   - Проверка работы

Особенности:
    - Полная валидация через Pydantic схемы
    - Автоматическая документация через Django Ninja
    - Поддержка иерархической структуры
    - Обработка ошибок и валидация

Автор: Pyland Team
Дата: 2025
"""

from uuid import UUID

from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from reviewers.models import LessonSubmission

from .models import Course, Lesson, Step
from .schemas import (
    CourseCreateIn,
    CourseOut,
    LessonCreateIn,
    LessonOut,
    MentorReviewIn,
    StepCreateIn,
    StepOut,
    SubmissionOut,
    SubmissionResubmitIn,
    SubmissionsListOut,
)

router = Router(tags=["Courses"])


@router.get("/", response=list[CourseOut])
def list_courses(request):
    """
    Получить список всех курсов с уроками и шагами.
    """
    return [
        CourseOut(
            id=course.id,
            name=course.name,
            description=course.description,
            slug=course.slug,
            lessons=[
                LessonOut(
                    id=lesson.id,
                    name=lesson.name,
                    lesson_number=lesson.lesson_number,
                    slug=lesson.slug,
                    steps=[
                        StepOut(
                            id=step.id,
                            name=step.name,
                            step_number=step.step_number,
                            description=step.description,
                        )
                        for step in lesson.steps.all()
                    ],
                )
                for lesson in course.lessons.all()
            ],
        )
        for course in Course.objects.prefetch_related("lessons__steps").all()
    ]


@router.post("/", response=CourseOut)
def create_course(request, data: CourseCreateIn):
    """
    Создать новый курс.
    """
    course = Course.objects.create(name=data.name, description=data.description or "")
    return CourseOut(
        id=course.id,
        name=course.name,
        description=course.description,
        slug=course.slug,
        lessons=[],
    )


@router.get("/{course_id}", response=CourseOut)
def get_course(request, course_id: UUID):
    """
    Получить один курс по его ID.
    """
    try:
        course = Course.objects.prefetch_related("lessons__steps").get(id=course_id)
    except Course.DoesNotExist as e:
        raise HttpError(404, "Course not found") from e
    return CourseOut(
        id=course.id,
        name=course.name,
        description=course.description,
        slug=course.slug,
        lessons=[
            LessonOut(
                id=lesson.id,
                name=lesson.name,
                lesson_number=lesson.lesson_number,
                slug=lesson.slug,
                steps=[
                    StepOut(
                        id=step.id,
                        name=step.name,
                        step_number=step.step_number,
                        description=step.description,
                    )
                    for step in lesson.steps.all()
                ],
            )
            for lesson in course.lessons.all()
        ],
    )


@router.post("/lessons", response=LessonOut)
def create_lesson(request, data: LessonCreateIn):
    """
    Создать новый урок в курсе.
    """
    try:
        course = Course.objects.get(id=data.course_id)
    except Course.DoesNotExist as e:
        raise HttpError(404, "Course not found") from e
    lesson = Lesson.objects.create(course=course, name=data.name)
    return LessonOut(
        id=lesson.id,
        name=lesson.name,
        lesson_number=lesson.lesson_number,
        slug=lesson.slug,
        steps=[],
    )


@router.post("/steps", response=StepOut)
def create_step(request, data: StepCreateIn):
    """
    Создать новый шаг в уроке.
    """
    try:
        lesson = Lesson.objects.get(id=data.lesson_id)
    except Lesson.DoesNotExist as e:
        raise HttpError(404, "Lesson not found") from e
    step = Step.objects.create(lesson=lesson, name=data.name, description=data.description or "")
    return StepOut(
        id=step.id,
        name=step.name,
        step_number=step.step_number,
        description=step.description,
    )


# ============ SUBMISSIONS API ============


@router.get("/submissions/my", response=SubmissionsListOut)
def get_my_submissions(request):
    """
    Получить список всех работ текущего пользователя, сгруппированных по статусам.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Authentication required")

    profile = request.user.student
    submissions = (
        LessonSubmission.objects.filter(student=profile)
        .select_related("lesson", "lesson__course", "mentor", "mentor__user")
        .order_by("-submitted_at")
    )

    def format_submission(sub):
        return SubmissionOut(
            id=sub.id,
            lesson_id=sub.lesson.id,
            lesson_name=sub.lesson.name,
            course_name=sub.lesson.course.name,
            lesson_url=sub.lesson_url,
            status=sub.status,
            status_display=sub.get_status_display(),
            status_icon=sub.get_status_icon(),
            status_color=sub.get_status_badge_color(),
            mentor_comment=sub.mentor_comment,
            mentor_name=sub.mentor.user.get_full_name() if sub.mentor else None,
            submitted_at=sub.submitted_at.strftime("%d.%m.%Y %H:%M"),
            reviewed_at=sub.reviewed_at.strftime("%d.%m.%Y %H:%M") if sub.reviewed_at else None,
            revision_count=sub.revision_count,
            can_resubmit=sub.can_resubmit(),
            is_approved=sub.is_approved(),
        )

    result = {
        "pending": [format_submission(s) for s in submissions if s.status == "pending"],
        "changes_requested": [
            format_submission(s) for s in submissions if s.status == "changes_requested"
        ],
        "approved": [format_submission(s) for s in submissions if s.status == "approved"],
        "total_count": submissions.count(),
    }

    return result


@router.get("/submissions/{submission_id}", response=SubmissionOut)
def get_submission_detail(request, submission_id: UUID):
    """
    Получить детальную информацию о работе.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Authentication required")

    try:
        submission = LessonSubmission.objects.select_related(
            "lesson", "lesson__course", "mentor", "mentor__user", "student", "student__user"
        ).get(id=submission_id)
    except LessonSubmission.DoesNotExist as e:
        raise HttpError(404, "Submission not found") from e

    # Проверка доступа
    if submission.student != request.user.student and not request.user.is_staff:
        raise HttpError(403, "Access denied")

    return SubmissionOut(
        id=submission.id,
        lesson_id=submission.lesson.id,
        lesson_name=submission.lesson.name,
        course_name=submission.lesson.course.name,
        lesson_url=submission.lesson_url,
        status=submission.status,
        status_display=submission.get_status_display(),
        status_icon=submission.get_status_icon(),
        status_color=submission.get_status_badge_color(),
        mentor_comment=submission.mentor_comment,
        mentor_name=submission.mentor.user.get_full_name() if submission.mentor else None,
        submitted_at=submission.submitted_at.strftime("%d.%m.%Y %H:%M"),
        reviewed_at=(
            submission.reviewed_at.strftime("%d.%m.%Y %H:%M") if submission.reviewed_at else None
        ),
        revision_count=submission.revision_count,
        can_resubmit=submission.can_resubmit(),
        is_approved=submission.is_approved(),
    )


@router.post("/submissions/resubmit/{submission_id}", response=SubmissionOut)
def resubmit_submission(request, submission_id: UUID, data: SubmissionResubmitIn):
    """
    Повторная отправка работы после внесения правок.
    """
    if not request.user.is_authenticated:
        raise HttpError(401, "Authentication required")

    try:
        submission = LessonSubmission.objects.select_related(
            "lesson", "lesson__course", "student", "student__user"
        ).get(id=submission_id)
    except LessonSubmission.DoesNotExist as e:
        raise HttpError(404, "Submission not found") from e

    # Проверка прав
    if submission.student != request.user.student:
        raise HttpError(403, "Access denied")

    # Проверка статуса
    if not submission.can_resubmit():
        raise HttpError(400, "Cannot resubmit this submission")

    # Обновление
    submission.lesson_url = str(data.lesson_url)
    submission.status = "pending"
    submission.mentor_comment = ""
    submission.reviewed_at = None
    submission.revision_count += 1
    submission.save()

    return SubmissionOut(
        id=submission.id,
        lesson_id=submission.lesson.id,
        lesson_name=submission.lesson.name,
        course_name=submission.lesson.course.name,
        lesson_url=submission.lesson_url,
        status=submission.status,
        status_display=submission.get_status_display(),
        status_icon=submission.get_status_icon(),
        status_color=submission.get_status_badge_color(),
        mentor_comment=submission.mentor_comment,
        mentor_name=None,
        submitted_at=submission.submitted_at.strftime("%d.%m.%Y %H:%M"),
        reviewed_at=None,
        revision_count=submission.revision_count,
        can_resubmit=submission.can_resubmit(),
        is_approved=submission.is_approved(),
    )


@router.post("/submissions/{submission_id}/review", response=SubmissionOut)
def mentor_review_submission(request, submission_id: UUID, data: MentorReviewIn):
    """
    Проверка работы ментором (только для staff).
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        raise HttpError(403, "Access denied")

    try:
        submission = LessonSubmission.objects.select_related(
            "lesson", "lesson__course", "student", "student__user"
        ).get(id=submission_id)
    except LessonSubmission.DoesNotExist as e:
        raise HttpError(404, "Submission not found") from e

    # Валидация статуса
    if data.status not in ["changes_requested", "approved"]:
        raise HttpError(400, "Invalid status")

    # Обновление
    submission.status = data.status
    submission.mentor = request.user.student
    submission.mentor_comment = data.mentor_comment or ""
    submission.reviewed_at = timezone.now()
    submission.save()

    return SubmissionOut(
        id=submission.id,
        lesson_id=submission.lesson.id,
        lesson_name=submission.lesson.name,
        course_name=submission.lesson.course.name,
        lesson_url=submission.lesson_url,
        status=submission.status,
        status_display=submission.get_status_display(),
        status_icon=submission.get_status_icon(),
        status_color=submission.get_status_badge_color(),
        mentor_comment=submission.mentor_comment,
        mentor_name=submission.mentor.user.get_full_name() if submission.mentor else None,
        submitted_at=submission.submitted_at.strftime("%d.%m.%Y %H:%M"),
        reviewed_at=(
            submission.reviewed_at.strftime("%d.%m.%Y %H:%M") if submission.reviewed_at else None
        ),
        revision_count=submission.revision_count,
        can_resubmit=submission.can_resubmit(),
        is_approved=submission.is_approved(),
    )
