"""Client to interact with Slack."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from .models.config_model import SlackConfig

LOGGER = structlog.get_logger()


class SlackClient:
    """Client used to interact with Slack."""

    def __init__(self, config: SlackConfig, python_job_name: str):
        """
        Initialize the Slack Client.

        Initialize the Slack block message and Slack api response.

        Args:
            config: Pydantic Slack config model.
            python_job_name: Name of Python job.
        """
        self.config = config
        self.slack_channel = self.config.channel
        self.blocks: list[dict] = []
        self.response: dict[Any, Any] | SlackResponse = {}
        try:
            self.slack_client = WebClient(token=self.config.bot_token)
        except SlackApiError as e:
            LOGGER.info(
                f"Could not initialize SlackClient. Error: {e.response['error']}",
            )
        self.initialize_block_message(job_name=python_job_name)

    def post_simple_message(self, message: str) -> None:
        """
        Post a simple message on Slack.

        Args:
             message : plain text message.
        """
        assert type(message) == str
        try:
            self.slack_client.chat_postMessage(
                channel=f"#{self.slack_channel}", text=message
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post message on Slack. Error: {e.response['error']}",
            )

    def send_secret_message_in_channel(
            self,
            message: str,
            user: str | None = None,
    ) -> None:
        """
        Post a secret message on Slack to a particular user.

        Args:
             message: plain text message.
             user: user id (member id).
        """
        assert type(message) == str and type(user) == str
        try:
            self.slack_client.chat_postEphemeral(
                channel=f"#{self.slack_channel}", text=message, user=user
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post secret message on Slack. Error: {e.response['error']}",
            )

    def send_block_message(self) -> None:
        """Send a block message (self.blocks) on Slack and store the response."""
        try:
            self.response = self.slack_client.chat_postMessage(
                channel=f"#{self.slack_channel}", blocks=self.blocks
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post message on Slack. Error: {e.response['error']}",
            )

    def update_block_message(self) -> None:
        """Dynamically update block message and update the response."""
        try:
            self.response = self.slack_client.chat_update(
                channel=self.response["channel"],
                blocks=self.blocks,
                ts=self.response["ts"],
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post message on Slack. Error: {e.response['error']}",
            )

    def initialize_block_message(self, job_name: str) -> None:
        """
        Initialize Slack block message and send it to Slack.

        Args:
             job_name: Name of python job (Eg. Salesforce-Updater).
        """
        assert type(job_name) == str
        self.blocks = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Hello *Data Team*! \n Invoking *{job_name}* :on: .\n \
                        Date: {datetime.now().strftime('%Y-%m-%d')} \t \
                        Time: {datetime.now().time()} ",
                    }
                ],
            },
            {"type": "divider"},
        ]
        self.send_block_message()

    def add_message_block(
            self,
            message: str,
            img_url: str | None = None,
            temp: bool = False,
    ) -> None:
        """
        Add a message to the Slack block message.

        Args:
            message: plain text message.
            img_url: url of the image to add to the message [Optional].
            temp: True if this is a temporary message.
        """
        if img_url is not None:
            self.blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url": img_url,
                            "alt_text": "contentstack_image",
                        },
                        {"type": "mrkdwn", "text": message},
                    ],
                },
            )
        else:
            self.blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": message},
                    ],
                },
            )
        self.update_block_message()
        if temp:
            self.blocks.pop()

    def add_success_block(self) -> None:
        """Add success message to block."""
        self.blocks.append(
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": " *Job Successful* !! :tada: "},
                ],
            },
        )
        self.update_block_message()

    def add_error_block(
            self, error_message: str | None = None, notify: bool = False
    ) -> None:
        """
        Add error block to the Slack message block.

        Args:
            error_message: plain error text message.
            notify: True if you want to notify team members to fix the error,
                else False.
        """
        self.blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": " *Job Unsuccessful* :disappointed_relieved: ",
                    },
                ],
            },
        )
        if error_message is not None:
            self.blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f" *Error Message* : {error_message} ",
                        },
                    ],
                },
            )
        if notify:
            self.blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"<@{self.config.user1}> and \
                            <@{self.config.user2}> Please fix the error!",
                        },
                    ],
                },
            )
        self.update_block_message()
