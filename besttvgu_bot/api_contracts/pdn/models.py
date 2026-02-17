from datetime import datetime

from pydantic import BaseModel


class PDNConsent(BaseModel):
    telegram_id: int
    policy_version: str
    consent_at: datetime
    file_hash: str
    hash_method: str

    model_config = {"frozen": True}
