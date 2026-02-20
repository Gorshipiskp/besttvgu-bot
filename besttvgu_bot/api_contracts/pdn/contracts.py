from besttvgu_bot.api_contracts.api_requests import api_post, api_get
from besttvgu_bot.api_contracts.pdn.models import IsUserHasAllConsents, IsUserConsentsValid
from besttvgu_bot.modules.documents_validator import UserConsents


class ConsentsIsInvalid(Exception):
    pass


async def get_user_consents_contract() -> UserConsents:
    return await api_get(
        "get_user_required_consents",
        UserConsents
    )


async def validate_user_consents_documents_contract(
        policy_version: str,
        policy_hash: str,
        agreement_version: str,
        agreement_hash: str,
        hash_method: str
) -> bool:
    validity_info: IsUserConsentsValid = await api_post(
        "validate_user_consents_documents",
        {
            "policy_version": policy_version,
            "policy_hash": policy_hash,
            "agreement_version": agreement_version,
            "agreement_hash": agreement_hash,
            "hash_method": hash_method
        },
        IsUserConsentsValid
    )

    if not validity_info.is_valid:
        raise ConsentsIsInvalid("Consents aren't set right")

    return validity_info.is_valid


async def check_user_consents_contract(telegram_id: int) -> bool:
    consented_info: IsUserHasAllConsents = await api_post(
        "check_user_consents",
        {
            "telegram_id": telegram_id
        },
        IsUserHasAllConsents
    )

    if consented_info.non_valid_consents is not None:
        raise ConsentsIsInvalid("Consents aren't set right")

    return consented_info.is_consents_accepted


async def accept_user_consents_contract(telegram_id: int) -> None:
    await api_post(
        "accept_user_consents",
        {
            "telegram_id": telegram_id
        }
    )
