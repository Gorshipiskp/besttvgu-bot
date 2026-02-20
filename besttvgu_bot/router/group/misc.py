from datetime import datetime

from besttvgu_bot.api_contracts.group.misc import get_week_mark, get_week_mark_emoji
from besttvgu_bot.api_contracts.group.models import GroupScheduleInfo, WeekMarks, LessonPublic, ScheduleElement
from besttvgu_bot.api_contracts.models import SubjectPublic, TeacherPublic, format_subject_type
from besttvgu_bot.misc.datetime_lib import get_lesson_num_by_time
from besttvgu_bot.misc.misc import format_timestamp


class LessonView:
    def __init__(self, group_schedule: GroupScheduleInfo, lesson: LessonPublic, now: datetime) -> None:
        self.lesson: LessonPublic = lesson
        self.group_schedule: GroupScheduleInfo = group_schedule
        self.now: datetime = now

        cur_lesson_num_info: tuple[bool, int] | None = get_lesson_num_by_time(now)

        if cur_lesson_num_info is None:
            self.is_break: bool = False
            self.is_cur_lesson: bool = False
        else:
            is_cur_lesson: bool = cur_lesson_num_info[1] == self.lesson.lesson_number
            self.is_break: bool = cur_lesson_num_info[0] and is_cur_lesson
            self.is_cur_lesson: bool = is_cur_lesson and not self.is_break

        self.subject: SubjectPublic = self.group_schedule.subjects[self.lesson.subject_id]
        self.teachers: list[TeacherPublic] = [
            self.group_schedule.teachers[teacher_id] for teacher_id in self.lesson.teachers_ids
        ]

    def format_place(self) -> str:
        return self.group_schedule.places[self.lesson.place_id].name

    def format_subject_name(self) -> str:
        subject_name: str = self.subject.name

        return f"{get_week_mark_emoji(self.lesson.week_mark)} {subject_name}"

    def format_subject_type(self) -> str:
        subject_type: str = self.subject.type

        return format_subject_type(subject_type)

    def format_teachers(self) -> list[str]:
        # todo: Добавить сортировку по `is_small_teacher`
        return ", ".join(teacher.format_name() for teacher in self.teachers)

    def format_time(self) -> str:
        time_start: str = format_timestamp(self.lesson.time_start)
        time_end: str = format_timestamp(self.lesson.time_end)

        return f"{self.lesson.lesson_number + 1}. {time_start} - {time_end}"


def pick_relevant_lesson(lessons: list[LessonView], _cur_date: datetime) -> LessonView | None:
    if len(lessons) == 1:
        return lessons[0]

    # todo: Потом продумать лучшую стратегию выбора
    return lessons[0]


def get_day_lessons(group_schedule: GroupScheduleInfo, now: datetime, target_date: datetime) -> list[LessonView]:
    week_mark: WeekMarks = get_week_mark(target_date)
    schedule_day = group_schedule.schedule[target_date.weekday()]

    lessons: dict[int, LessonView] = {}

    for lesson_number, slot in [
        *schedule_day.get(week_mark, {}).items(),
        *schedule_day.get(WeekMarks.EVERY, {}).items()
    ]:
        lessons_in_slot: list[LessonPublic] = [
            *slot.get(ScheduleElement.LESSONS, []),
            # todo: Добавить поддержку изменений
            # *slot.get(ScheduleElement.EDITS, []),
        ]

        if len(lessons_in_slot) == 0:
            continue

        # todo: Сделать поддержку более одной пары в одном слоте
        lessons[lesson_number] = pick_relevant_lesson(lessons_in_slot, target_date)

    day_lessons: list[LessonView] = list(LessonView(group_schedule, lesson, now) for lesson in lessons.values())
    day_lessons.sort(key=lambda lesson_view: lesson_view.lesson.time_start)

    return day_lessons
