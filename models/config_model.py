"""Config model."""
from pydantic import BaseModel, constr


class SlackConfig(BaseModel):
    """Slack config data model."""

    bot_token: constr(min_length=1)  # type: ignore
    channel: constr(min_length=1)  # type: ignore
    user1: constr(min_length=1)  # type: ignore
    user2: constr(min_length=1)  # type: ignore
