"""Config model."""
from typing import Optional

from pydantic import BaseModel, constr


class SlackConfig(BaseModel):
    """Slack config data model."""

    bot_token: constr(min_length=1)  # type: ignore
    user1: Optional[constr(min_length=1)]  # type: ignore
    user2: Optional[constr(min_length=1)]  # type: ignore


class ConfigModel(BaseModel):
    """Config data model."""

    slack: SlackConfig
