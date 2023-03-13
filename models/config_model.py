"""Config model."""
from pydantic import BaseModel, constr


class SnowflakeConfig(BaseModel):
    """Snowflake config data model."""

    account: constr(min_length=1)  # type: ignore
    username: constr(min_length=1)  # type: ignore
    password: constr(min_length=1)  # type: ignore
    database_name: constr(min_length=1)  # type: ignore
    schema_name: constr(min_length=1)  # type: ignore


class ContentStackConfig(BaseModel):
    """Google config data model."""

    api_key: constr(min_length=1)  # type: ignore
    delivery_token: constr(min_length=1)  # type: ignore
    environment: constr(min_length=1)  # type: ignore


class SlackConfig(BaseModel):
    """Slack config data model."""

    bot_token: constr(min_length=1)  # type: ignore
    channel: constr(min_length=1)  # type: ignore
    user1: constr(min_length=1)  # type: ignore
    user2: constr(min_length=1)  # type: ignore


class ConfigModel(BaseModel):
    """App config data model."""

    snowflake: SnowflakeConfig
    contentstack: ContentStackConfig
    slack: SlackConfig
