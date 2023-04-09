"""Client to interact with Slack."""

from datetime import datetime
from typing import List

import structlog
from .models.config_model import SlackConfig
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

LOGGER = structlog.get_logger()


class SlackClient:
    """Client used to interact with Slack."""

    def __init__(self, config: SlackConfig, python_job_name: str):
        """
        Initialize the Slack Client.

        Args:
            config: Pydantic Slack config model.
            python_job_name: Name of the Python job for the block message title.
        """
        self.config = config
        self.slack_client = WebClient(token=self.config.bot_token)
        self.slack_channel = self.config.channel
        self.blocks: List[dict] = []
        self.response = None
        self.initialize_block_message(job_name=python_job_name)

    def post_simple_message(self, message: str):
        """Post a simple message on Slack.

        Args:
             message : str
        """
        assert type(message) == str
        try:
            self.slack_client.chat_postMessage(
                channel="#" + self.slack_channel, text=message
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post message on Slack. Error: {e.response['error']}"
            )

    def send_secret_message_in_channel(self, message: str, user: str | None = None):
        """Post a secret message on slack.

        Args:
             message : str
             user : str : user id (member id)
        """
        assert type(message) == str and type(user) == str
        try:
            self.slack_client.chat_postEphemeral(
                channel="#" + self.slack_channel, text=message, user=user
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post secret message on Slack. Error: {e.response['error']}"
            )

    def send_block_message(self):
        """Send a custom block message on Slack and store the response."""
        try:
            self.response = self.slack_client.chat_postMessage(
                channel="#" + self.slack_channel, blocks=self.blocks
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post message on Slack. Error: {e.response['error']}"
            )

    def update_block_message(self):
        """Dynamically update block message and update the response."""
        try:
            self.response = self.slack_client.chat_update(
                channel=self.response["channel"],
                blocks=self.blocks,
                ts=self.response["ts"],
            )
        except SlackApiError as e:
            LOGGER.info(
                f"Could not post message on Slack. Error: {e.response['error']}"
            )

    def initialize_block_message(self, job_name: str):
        """Initialize Slack block message for Python Jobs and send it.

        Args:
             job_name: str : Name of python job
        """
        assert type(job_name) == str
        self.blocks = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Hello *Data Team*! \n Starting *{job_name}* :on: .\n \
                                Date: {datetime.now().strftime('%Y-%m-%d')} \t \
                                Time: {datetime.now().time()} ",
                    }
                ],
            },
            {"type": "divider"},
        ]
        self.send_block_message()

    def add_message_block(
        self, message: str, img_url: str | None = None, temp: bool = False
    ):
        """Add a message to the Slack block message.

        Args:
            message: str
            img_url: str [Optional]
            temp: bool : if this a temporary message
        """
        if img_url is not None:
            self.blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url": img_url,
                            "alt_text": "image url",
                        },
                        {"type": "mrkdwn", "text": message},
                    ],
                }
            )
        else:
            self.blocks.append(
                {"type": "context", "elements": [{"type": "mrkdwn", "text": message}]}
            )
        self.update_block_message()
        if temp:
            self.blocks.pop()

    def add_success_block(self):
        """Add success message to block."""
        self.blocks.append(
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": " *Job Successful* !! :tada: "}
                ],
            }
        )
        self.update_block_message()

    def add_error_block(self, error_msg: str):
        """Add error block to the Slack message block."""
        self.blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f" *Job Unsuccessful* :confused: \n *Error Message* : {error_msg} ",
                    }
                ],
            }
        )
        self.blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"<@{self.config.user1}> and <@{self.config.user2}> Please fix the error!",
                    }
                ],
            }
        )
        self.update_block_message()
