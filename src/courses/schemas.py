"""
Courses Schemas Module - Pydantic схемы для Courses API.

Этот модуль содержит схемы для валидации входных/выходных данных:

Input схемы (*In):
    - CourseCreateIn: Создание нового курса
    - LessonCreateIn: Создание нового урока
    - StepCreateIn: Создание нового шага
    - SubmissionResubmitIn: Повторная отправка работы
    - MentorReviewIn: Проверка работы ментором

Output схемы (*Out):
    - CourseOut: Детали курса
    - LessonOut: Детали урока
    - StepOut: Детали шага
    - SubmissionOut: Информация об отправленной работе
    - SubmissionsListOut: Список отправленных работ

Автор: Pyland Team
Дата: 2025
"""

from uuid import UUID

from pydantic import BaseModel

# ----------------- INPUT SCHEMAS -----------------


class CourseCreateIn(BaseModel):
    """
    Схема для создания нового курса через API.
    """

    name: str
    description: str | None = None


class LessonCreateIn(BaseModel):
    """
    Схема для создания нового урока в курсе через API.
    """

    course_id: UUID
    name: str


class StepCreateIn(BaseModel):
    """
    Схема для создания нового шага в уроке через API.
    """

    lesson_id: UUID
    name: str
    description: str | None = None


class SubmissionCreateIn(BaseModel):
    """
    Схема для отправки работы на проверку.
    """

    lesson_id: UUID
    lesson_url: str


class SubmissionResubmitIn(BaseModel):
    """
    Схема для повторной отправки работы после правок.
    """

    lesson_url: str


class MentorReviewIn(BaseModel):
    """
    Схема для проверки работы ментором.
    """

    status: str  # 'changes_requested', 'approved'
    mentor_comment: str | None = None


# ----------------- OUTPUT SCHEMAS -----------------


class StepOut(BaseModel):
    """
    Схема для вывода информации о шаге урока.
    """

    id: UUID
    name: str
    step_number: int
    description: str | None = None

    model_config = {"from_attributes": True}


class LessonOut(BaseModel):
    """
    Схема для вывода информации об уроке.
    """

    id: UUID
    name: str
    lesson_number: int
    slug: str
    steps: list[StepOut] = []

    model_config = {"from_attributes": True}


class CourseOut(BaseModel):
    """
    Схема для вывода информации о курсе.
    """

    id: UUID
    name: str
    description: str | None = None
    slug: str
    lessons: list[LessonOut] = []

    model_config = {"from_attributes": True}


class SubmissionOut(BaseModel):
    """
    Схема для вывода информации о работе студента.
    """

    id: UUID
    lesson_id: UUID
    lesson_name: str
    course_name: str
    lesson_url: str
    status: str
    status_display: str
    status_icon: str
    status_color: str
    mentor_comment: str | None = None
    mentor_name: str | None = None
    submitted_at: str
    reviewed_at: str | None = None
    revision_count: int
    can_resubmit: bool
    is_approved: bool

    model_config = {"from_attributes": True}


class SubmissionsListOut(BaseModel):
    """
    Схема для списка работ с группировкой по статусам.
    """

    pending: list[SubmissionOut] = []
    changes_requested: list[SubmissionOut] = []
    approved: list[SubmissionOut] = []
    total_count: int
