from besttvgu_bot.api_contracts.api_requests import api_post
from besttvgu_bot.api_contracts.group.models import GroupScheduleInfo
from besttvgu_bot.api_contracts.models import GroupFullPublic


async def get_group_schedule(group_id: int) -> GroupScheduleInfo:
    return await api_post(
        "get_group_schedule",
        {
            "group_id": group_id
        },
        GroupScheduleInfo
    )


async def get_full_group_info(group_id: int) -> GroupFullPublic:
    return await api_post(
        "get_full_group_info",
        {
            "group_id": group_id
        },
        GroupFullPublic
    )
