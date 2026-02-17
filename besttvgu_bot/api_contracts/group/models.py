from enum import Enum
from typing import Any

from pydantic import BaseModel

from besttvgu_bot.api_contracts.models import TeacherPublic, PlacePublic, SubjectPublic, GroupPublic


class WeekMarks(Enum):
    EVERY = "every"
    MINUS = "minus"
    PLUS = "plus"


class LessonPublic(BaseModel):
    id: int
    week_day: int
    lesson_number: int
    week_mark: WeekMarks
    time_start: int
    time_end: int
    place_id: int
    subject_id: int
    teachers_ids: list[int]
    groups_ids: list[int]
    cancelled: bool
    subgroup: int | None


class ScheduleElement(Enum):
    LESSONS = "lessons"
    EDITS = "edits"


class GroupScheduleInfo(BaseModel):
    group_id: int

    schedule: dict[int, dict[WeekMarks, dict[int, dict[ScheduleElement, list[LessonPublic]]]]]
    places: dict[int, PlacePublic]
    subjects: dict[int, SubjectPublic]
    groups: dict[int, GroupPublic]
    teachers: dict[int, TeacherPublic]

    model_config = {"frozen": True}
