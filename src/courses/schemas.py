from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

# ----------------- INPUT SCHEMAS -----------------


class CourseCreateIn(BaseModel):
    """
    Схема для создания нового курса через API.
    """

    name: str
    description: Optional[str] = None


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
    description: Optional[str] = None


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
    mentor_comment: Optional[str] = None


# ----------------- OUTPUT SCHEMAS -----------------


class StepOut(BaseModel):
    """
    Схема для вывода информации о шаге урока.
    """

    id: UUID
    name: str
    step_number: int
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class LessonOut(BaseModel):
    """
    Схема для вывода информации об уроке.
    """

    id: UUID
    name: str
    lesson_number: int
    slug: str
    steps: List[StepOut] = []

    model_config = {"from_attributes": True}


class CourseOut(BaseModel):
    """
    Схема для вывода информации о курсе.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    slug: str
    lessons: List[LessonOut] = []

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
    mentor_comment: Optional[str] = None
    mentor_name: Optional[str] = None
    submitted_at: str
    reviewed_at: Optional[str] = None
    revision_count: int
    can_resubmit: bool
    is_approved: bool

    model_config = {"from_attributes": True}


class SubmissionsListOut(BaseModel):
    """
    Схема для списка работ с группировкой по статусам.
    """

    pending: List[SubmissionOut] = []
    changes_requested: List[SubmissionOut] = []
    approved: List[SubmissionOut] = []
    total_count: int
