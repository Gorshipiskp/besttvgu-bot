import hashlib
from json import dumps, load
from pathlib import Path
from typing import Final

from besttvgu_bot.api_contracts.pdn.contracts import get_pdn_consent_user
from besttvgu_bot.consts import PDN_PREFIX, PDN_VERSION

# todo: Повесить кэширование на функции (особенно на IO-функции)

PDN_HASHES_FILE: Final[str] = "pdn_hashes.json"
PDNS_DIRNAME: Final[str] = "pdns"

PDNS_DIR: Final[Path] = Path(__file__).parent.parent / PDNS_DIRNAME
PDN_HASHES_FILE_PATH: Final[Path] = PDNS_DIR / PDN_HASHES_FILE


def get_cur_pdn_hashes() -> dict[str, str]:
    with open(PDN_HASHES_FILE_PATH, "r", encoding="UTF-8") as f:
        return load(f)


def check_pdn_hash_file() -> None:
    if not PDNS_DIR.exists():
        with PDNS_DIR.open("w+", encoding="UTF-8") as f:
            f.write("{}")


def get_pdn_path() -> Path:
    return PDNS_DIR / f"{PDN_PREFIX}_{PDN_VERSION}.pdf"


async def get_pdn_file() -> Path:
    file_path: Path = get_pdn_path()

    if not file_path.exists():
        raise FileNotFoundError

    return file_path


async def is_user_has_actual_pdn_consent(telegram_id: int) -> bool:
    return await get_pdn_consent_user(telegram_id)


async def accept_pdn_consent(call) -> None:
    async with tvgu_db.get_async_session() as session:
        new_pdn: PDNConsent = PDNConsent(
            telegram_id=call.from_user.id,
            policy_version=PDN_VERSION
        )
        session.add(new_pdn)
        await session.commit()


class PDNNeedsVersionUpdate(Exception):
    pass


def update_actuality_pdn() -> None:
    file_path: Path = get_pdn_path()

    file_bytes: bytes = file_path.read_bytes()
    file_hash: str = hashlib.sha256(file_bytes).hexdigest()

    pdn_hashes: dict[str, str] = get_cur_pdn_hashes()

    if pdn_hashes.get(PDN_VERSION) is None:
        pdn_hashes[PDN_VERSION] = file_hash

        with open(PDN_HASHES_FILE_PATH, "w+", encoding="UTF-8") as f:
            f.write(dumps(pdn_hashes, ensure_ascii=False))
    else:
        if pdn_hashes[PDN_VERSION] == file_hash:
            print("BestTvGU: ✅  No need to update PDN")
        else:
            raise PDNNeedsVersionUpdate(
                f"BestTvGU: ❌  Need to update PDN (from {pdn_hashes[PDN_VERSION]} to {file_hash})"
            )


def init_pdn() -> None:
    check_pdn_hash_file()
    update_actuality_pdn()
