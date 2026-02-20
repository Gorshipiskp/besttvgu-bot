from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BotCommand, InlineKeyboardButton

from besttvgu_bot.api_contracts.group.contracts import get_group_schedule_contract, get_full_group_info_contract
from besttvgu_bot.api_contracts.group.misc import get_week_mark, get_week_mark_emoji
from besttvgu_bot.api_contracts.group.models import GroupScheduleInfo
from besttvgu_bot.api_contracts.models import UserFull, GroupFull, GROUP_TYPES_NAMES, UserGroupPublic, \
    UserPublic
from besttvgu_bot.consts import Templates, MAX_WEEK_DELTA_SCHEDULE
from besttvgu_bot.middlewares import CheckRegisterMiddleware
from besttvgu_bot.misc.caching import user_cache, CacheIdentifiers, full_groups_cache, groups_schedules_cache
from besttvgu_bot.misc.datetime_lib import now, translate_date, get_start_of_week, is_same_day
from besttvgu_bot.misc.jinja import answer_by_template
from besttvgu_bot.misc.replies import build_reply_keyboard
from besttvgu_bot.modules.commands import register_command, CommandAccessibilityInfo, InfoAvailability
from besttvgu_bot.router.group.callbacks_datas import ChooseGroupCallbackData, ScheduleMoveCallbackData
from besttvgu_bot.router.group.middlewares import GroupCheckMiddleware
from besttvgu_bot.router.group.misc import get_day_lessons, LessonView
from besttvgu_bot.router.user_settings.endpoints import settings

router: Router = Router(name="schedule")

router.message.middleware(
    CheckRegisterMiddleware()
)
router.message.middleware(
    GroupCheckMiddleware()
)

register_command(
    CommandAccessibilityInfo(
        need_registration=InfoAvailability.YES,
        min_role_level=10,
        max_role_level=99
    ),
    BotCommand(
        command="schedule",
        description="Расписание"
    )
)

register_command(
    CommandAccessibilityInfo(
        need_registration=InfoAvailability.YES,
        min_role_level=10,
        max_role_level=99
    ),
    BotCommand(
        command="group",
        description="Ваша группа"
    )
)


@router.callback_query(ChooseGroupCallbackData.filter())
async def handle_choose_group(
        callback_query: CallbackQuery,
        callback_data: ChooseGroupCallbackData,
        user: UserFull
) -> None:
    await user.telegram_settings.update_user_settings(user, {"cur_group_id": callback_data.group_id})

    await callback_query.answer("Текущая группа изменена ✅")

    user: UserFull = user_cache[CacheIdentifiers.user_info(user.telegram_id)]
    await settings(callback_query.message, user, edit=True)


@router.callback_query(ScheduleMoveCallbackData.filter())
async def handle_schedule_move_group(
        callback_query: CallbackQuery,
        callback_data: ScheduleMoveCallbackData,
        user: UserFull
) -> None:
    if callback_data.datetime == "today":
        target_date: datetime = now()
    else:
        target_date: datetime = datetime.fromisoformat(callback_data.datetime.replace(".", ":"))

    await schedule(callback_query.message, user, target_date, edit=True)


@router.message(Command("schedule"))
async def schedule(message: Message, user: UserFull, target_date: datetime = None, edit: bool = False) -> None:
    if user.telegram_settings.cur_group.no_schedule:
        await answer_by_template(
            message,
            Templates.GROUP_NO_SCHEDULE,
        )
        return

    target_date: datetime = target_date or now()

    if abs(target_date - now()) > timedelta(weeks=MAX_WEEK_DELTA_SCHEDULE):
        await answer_by_template(
            message,
            Templates.NOT_SO_FAR_IN_SCHEDULE,
        )
        return

    real_now: datetime = now()

    async def get_group_schedule_kruto() -> GroupScheduleInfo:
        return await get_group_schedule_contract(user.telegram_settings.cur_group_id)

    group_schedule: GroupScheduleInfo = await groups_schedules_cache.get_or_set(
        CacheIdentifiers.group_schedule(user.telegram_settings.cur_group_id),
        get_group_schedule_kruto
    )

    day_lessons: list[LessonView] = get_day_lessons(group_schedule, now(), target_date)

    week_start: datetime = get_start_of_week(target_date)

    inline_buttons: list[InlineKeyboardButton] = []

    if not is_same_day(target_date, now()):
        inline_buttons.append(
            InlineKeyboardButton(
                text="Сегодня 🗓",
                callback_data=ScheduleMoveCallbackData(
                    datetime=now().isoformat().replace(":", ".")
                ).pack()
            )
        )

    for i in range(7):
        cur_day: datetime = week_start + timedelta(days=i)

        text: str = translate_date(cur_day.strftime("%A – %d %B %Y"))

        if is_same_day(target_date, cur_day):
            text = f"📅 {text} 📅"
        if is_same_day(real_now, cur_day):
            text = f"➡️ {text} ⬅️"

        inline_buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=ScheduleMoveCallbackData(
                    datetime=cur_day.isoformat().replace(":", ".")
                ).pack()
            )
        )

    next_week: datetime = week_start + timedelta(days=7)
    if abs(next_week - real_now) < timedelta(weeks=MAX_WEEK_DELTA_SCHEDULE):
        inline_buttons.append(
            InlineKeyboardButton(
                text="Следующая неделя ➡️",
                callback_data=ScheduleMoveCallbackData(
                    datetime=next_week.isoformat().replace(":", ".")
                ).pack()
            )
        )

    previous_week: datetime = week_start - timedelta(days=7)
    if abs(previous_week - real_now) < timedelta(weeks=MAX_WEEK_DELTA_SCHEDULE):
        inline_buttons.append(
            InlineKeyboardButton(
                text="Предыдущая неделя ⬅️",
                callback_data=ScheduleMoveCallbackData(
                    datetime=previous_week.isoformat().replace(":", ".")
                ).pack()
            )
        )

    await answer_by_template(
        message,
        Templates.GROUP_SCHEDULE,
        {
            "date_str": translate_date(target_date.strftime("%A – %d %B %Y")),
            "week_mark_emoji": get_week_mark_emoji(get_week_mark(target_date)),
            "group_schedule": group_schedule,
            "day_lessons": day_lessons,
            "len": len,
        },
        reply_markup=build_reply_keyboard(inline_buttons, 1),
        edit=edit
    )


@router.message(Command("group"))
async def group(message: Message, user: UserFull) -> None:
    async def get_full_group_kruto():
        return await get_full_group_info_contract(user.telegram_settings.cur_group.id)

    full_group_info: GroupFull = await full_groups_cache.get_or_set(
        CacheIdentifiers.full_group(user.telegram_settings.cur_group.id),
        get_full_group_kruto
    )

    members: list[dict[str, UserGroupPublic | UserPublic]] = []

    for member in full_group_info.members:
        member_user_group: UserGroupPublic | None = None

        for user_group in full_group_info.users_groups:
            if user_group.user_id == member.id:
                member_user_group = user_group
                break

        if member_user_group is not None:
            members.append({
                "member": member,
                "user_group": member_user_group
            })

    members.sort(key=lambda x: -x["user_group"].role.level)

    starosta: UserPublic | None = None

    for member in members:
        if member["user_group"].role.name == "starosta":
            starosta = member["member"]
            break

    group_inline_buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text="🗓 Расписание",
            callback_data=ScheduleMoveCallbackData(
                datetime="today"
            ).pack()
        )
    ]

    await answer_by_template(
        message,
        Templates.USER_GROUP,
        template_params={
            "cur_group": full_group_info,
            "user": user,
            "group_type_str": GROUP_TYPES_NAMES[full_group_info.type],
            "members_infos": members,
            "starosta": starosta,
        },
        reply_markup=build_reply_keyboard(group_inline_buttons, 1),
    )
