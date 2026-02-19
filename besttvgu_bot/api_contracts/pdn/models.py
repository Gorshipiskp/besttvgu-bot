from pydantic import BaseModel


class IsUserHasAllConsents(BaseModel):
    is_consents_accepted: bool
    non_valid_consents: bool | None = None

    model_config = {"frozen": True}


class IsUserConsentsValid(BaseModel):
    is_valid: bool

    model_config = {"frozen": True}
