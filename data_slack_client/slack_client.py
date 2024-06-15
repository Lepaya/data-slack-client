"""Client to interact with Slack."""
from __future__ import annotations

import random
import time
from datetime import datetime
from typing import Any, Union

import pytz
import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from .helpers.logging_helper import log, log_and_raise_error
from .models.config_model import SlackConfig

LOGGER = structlog.get_logger()


class SlackClient:
    """Client used to interact with Slack."""

    def __init__(self, config: SlackConfig,
                 slack_channel: str,
                 init_block: bool = True,
                 header: Union[str, None] = None):
        """
        Initialize the Slack Client.

        Initialize the Slack block message and Slack api response.

        Args:
            config: Pydantic Slack config model.
            slack_channel: Name of Slack-Channel to write to.
            init_block: True if you want to add an introduction block
                        containing a python-job-name,date and time; else False.
            header: Name of Python-job if init_block is True, else None.
        """
        self.config = config
        self.slack_channel = slack_channel
        self.header = header
        self.blocks: list[dict] = []
        self.response: dict[Any, Any] | SlackResponse = {}
        try:
            self.slack_client = WebClient(token=self.config.bot_token)
            log("Successfully initialized Slack WebClient")
        except SlackApiError as e:
            log_and_raise_error(f"Could not initialize SlackClient. "
                                f"Error: {e.response.get('error', 'No error info in response')}.")
        if init_block is True:
            assert header is not None
            self.initialize_block_message(header_name=header)

    @classmethod
    def handle_slack_api_error(cls, e: SlackApiError):
        """
        Handle Slack API Error including Rate Limit Error.

        Args:
             e : SlackApiError
        """
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 1))
            backoff_time = min(retry_after, 30) + random.uniform(0, 10)  # Calculate exponential backoff time and Add jitter
            log(f"Rate limit exceeded. Retrying after {backoff_time} seconds.")
            time.sleep(backoff_time)
        else:
            log_and_raise_error(f"Slack API error: {e.response.get('error', 'No error info in response')}.")

    def post_simple_message(self, message: str, slack_channel: str = None) -> None:
        """
        Post a simple message on Slack.

        Args:
             message: plain text message.
             slack_channel [Optional]: Name of Slack-Channel to write to.
        """
        assert type(message) == str
        try:
            self.slack_client.chat_postMessage(
                channel=f"#{slack_channel or self.slack_channel}", text=message
            )
            log("Successfully posted simple message")
        except SlackApiError as e:
            self.handle_slack_api_error(e)

    def send_secret_message_in_channel(
            self,
            message: str,
            user: str | None = None,
            slack_channel: str = None
    ) -> None:
        """
        Post a secret message on Slack to a particular user.

        Args:
             message: plain text message.
             user: user id (member id).
             slack_channel [Optional]: Name of Slack-Channel to write to. 
        """
        assert type(message) == str and type(user) == str
        try:
            self.slack_client.chat_postEphemeral(
                channel=f"#{slack_channel or self.slack_channel}", text=message, user=user
            )
            log("Successfully posted secret message")
        except SlackApiError as e:
            self.handle_slack_api_error(e)

    def send_block_message(self, slack_channel: str = None, blocks: list[dict] = None) -> None:
        """Send a block message on Slack and store the response.
        
        Args:
             slack_channel [Optional]: Name of Slack-Channel to write to. 
             blocks: [Optional]: Slack message block object.
        """
        try:
            self.response = self.slack_client.chat_postMessage(
                channel=f"#{slack_channel or self.slack_channel}", blocks=blocks or self.blocks
            )
            log("Successfully sent message block")
        except SlackApiError as e:
            self.handle_slack_api_error(e)

    def update_block_message(self) -> None:
        """Dynamically update block message and update the response."""
        try:
            self.response = self.slack_client.chat_update(
                channel=self.response["channel"],
                blocks=self.blocks,
                ts=self.response["ts"],
            )
            log("Successfully updated message block")
        except SlackApiError as e:
            self.handle_slack_api_error(e)
        except KeyError as e:
            log_and_raise_error(f"Key error: {e.response.get('error', 'No error info in response')}.")

    def initialize_block_message(self, header_name: str) -> None:
        """
        Initialize Slack block message and send it to Slack.

        Args:
             header_name: Block message Header Name (Eg. Salesforce-Updater).
        """
        assert type(header_name) == str
        amsterdam_tz = pytz.timezone("Europe/Amsterdam")
        self.blocks = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Invoking *{header_name}* :on: \n"
                                f"Date: {datetime.now(amsterdam_tz).strftime('%Y-%m-%d')} \t"
                                f"Time: {datetime.now(amsterdam_tz).time()}",
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
            img_alt_text: str = "",
            temp: bool = False,
    ) -> None:
        """
        Add a message to the Slack block message.

        Args:
            message: plain text message.
            img_url: url of the image to add to the message [Optional].
            img_alt_text: alt text for image [Optional].
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
                            "alt_text": img_alt_text,
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
            assert self.config.user1 is not None or self.config.user2 is not None

            user_str = ""
            if self.config.user1 is not None:
                user_str += f"<@{self.config.user1}>"
            if self.config.user2 is not None:
                # Add a space before appending user2 if user_str already contains user1
                if user_str:
                    user_str += " "
                user_str += f"<@{self.config.user2}>"

            self.blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": user_str,
                        },
                    ],
                },
            )
        self.update_block_message()
