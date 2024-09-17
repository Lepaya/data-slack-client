"""Client to interact with Slack."""

from __future__ import annotations

import os
import random
import time
from datetime import datetime
from typing import Any, Optional, Union

import pytz
import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from .helpers.logging_helper import log, log_and_raise_error
from .models.config_model import SlackConfig

LOGGER = structlog.get_logger()
SEND_TO_SLACK = os.getenv("SEND_TO_SLACK", "FALSE").lower() == "true"


class SlackClient:
    """Client used to interact with Slack."""

    def __init__(
        self,
        config: SlackConfig,
        slack_channel: str,
        init_block: bool = True,
        header: Union[str, None] = None,
        stakeholders: Optional[dict] = {},
    ):
        """
        Initialize the Slack Client.

        Initialize the Slack block message and Slack api response.

        Args:
            config: Pydantic Slack config model.
            slack_channel: Name of Slack-Channel to write to.
            init_block: True if you want to add an introduction block
                        containing a python-job-name,date and time; else False.
            header: Name of Python-job if init_block is True, else None.
            stakeholders (dict[str, str]): A dictionary with stakeholder names as keys and member IDs as values.
        """
        assert isinstance(stakeholders, dict)
        self.config = config
        self.slack_channel = slack_channel
        self.header = header
        self.stakeholders = stakeholders
        self.blocks: list[dict] = []
        self.response: dict[Any, Any] | SlackResponse = None
        try:
            self.slack_client = WebClient(token=self.config.bot_token)
            log("Successfully initialized Slack WebClient")
        except SlackApiError as e:
            log_and_raise_error(
                f"Could not initialize SlackClient. " f"Error: {e.response.get('error', 'No error info in response')}."
            )
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
            backoff_time = min(retry_after, 30) + random.uniform(
                0, 10
            )  # Calculate exponential backoff time and Add jitter
            log(f"Rate limit exceeded. Retrying after {backoff_time} seconds.")
            time.sleep(backoff_time)
        else:
            log_and_raise_error(f"Slack API error: {e.response.get('error', 'No error info in response')}.")

    def post_simple_message(
        self, message: str, slack_channel: Optional[str] = None, tag_stakeholders: bool = False
    ) -> None:
        """
        Post a simple message on Slack.

        Args:
            message (str): Plain text message.
            slack_channel (str, optional): Name of Slack channel to write to. Defaults to None.
            tag_stakeholders (bool, optional): Whether to tag stakeholders in the message. Defaults to False.
        """
        assert isinstance(message, str)

        if tag_stakeholders and self.stakeholders:
            message += "\n" + self.build_tag_stakeholder_message()

        channel = f"#{slack_channel or self.slack_channel}"
        try:
            if SEND_TO_SLACK:
                self.slack_client.chat_postMessage(channel=channel, text=message)
                log("Successfully posted simple message")
            else:
                log(f"Simple message to slack: channel: {channel}\n\tmessage: {message}")
        except SlackApiError as e:
            self.handle_slack_api_error(e)

    def send_secret_message_in_channel(
        self, message: str, user_member_id: str | None = None, slack_channel: Optional[str] = None
    ) -> None:
        """
        Post a secret message on Slack to a particular user.

        Args:
             message: plain text message.
             user_member_id: user member id
             slack_channel [Optional]: Name of Slack-Channel to write to.
        """
        assert isinstance(message, str) and isinstance(user_member_id, str)

        channel = f"#{slack_channel or self.slack_channel}"
        try:
            if SEND_TO_SLACK:
                self.slack_client.chat_postEphemeral(
                    channel=channel,
                    text=message,
                    user=user_member_id,
                )
                log("Successfully posted secret message")
            else:
                log(f"Secret message to slack: channel: {channel}\n\tmessage: {message}")

        except SlackApiError as e:
            self.handle_slack_api_error(e)

    def send_block_message(self, slack_channel: Optional[str] = None, blocks: Optional[list[dict]] = None) -> None:
        """Send a block message on Slack and store the response.

        Args:
             slack_channel [Optional]: Name of Slack-Channel to write to.
             blocks: [Optional]: Slack message block object.
        """
        channel = f"#{slack_channel or self.slack_channel}"
        try:
            if SEND_TO_SLACK:
                self.response = self.slack_client.chat_postMessage(
                    channel=channel,
                    blocks=blocks or self.blocks,
                )
                log("Successfully sent message block")
            else:
                log(f"Block message to slack: channel: {channel}\n\tmessage: {blocks or self.blocks}")
        except SlackApiError as e:
            self.handle_slack_api_error(e)

    def update_block_message(self) -> None:
        """Dynamically update block message and update the response."""
        try:
            if SEND_TO_SLACK:
                self.response = self.slack_client.chat_update(
                    channel=self.response["channel"],
                    blocks=self.blocks,
                    ts=self.response["ts"],
                )
                log("Successfully updated message block")
            else:
                log(f"Block message to slack: message: {self.blocks})")
        except SlackApiError as e:
            self.handle_slack_api_error(e)
        except KeyError as e:
            log_and_raise_error(f"Key error: {e}.")

    def initialize_block_message(self, header_name: str) -> None:
        """
        Initialize Slack block message and send it to Slack.

        Args:
            header_name (str): Block message Header Name (e.g., Salesforce-Updater).
        """
        assert isinstance(header_name, str)
        amsterdam_tz = pytz.timezone("Europe/Amsterdam")
        block_elements = [
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
        self.blocks = block_elements  # type: ignore
        self.send_block_message()

    def add_message_block(
        self,
        message: str,
        img_url: str | None = None,
        img_alt_text: str = "",
        temp: bool = False,
        tag_stakeholders: bool = False,
    ) -> None:
        """
        Add a message to the Slack block message.

        Args:
            message (str): Plain text message.
            img_url (str, optional): URL of the image to add to the message. Defaults to None.
            img_alt_text (str, optional): Alt text for image. Defaults to "".
            temp (bool, optional): True if this is a temporary message. Defaults to False.
            tag_stakeholders (bool, optional): Whether to tag stakeholders in the message. Defaults to False.
        """
        block_elements = [{"type": "mrkdwn", "text": message}]

        if img_url is not None:
            block_elements.insert(0, {"type": "image", "image_url": img_url, "alt_text": img_alt_text})

        if tag_stakeholders and self.stakeholders:
            block_elements.append({"type": "mrkdwn", "text": self.build_tag_stakeholder_message()})

        self.blocks.append(
            {
                "type": "context",
                "elements": block_elements,
            }
        )
        if self.response is not None:
            self.update_block_message()
        else:
            self.send_block_message()

        if temp:
            self.blocks.pop()

    def add_success_block(self, tag_stakeholders: bool = False) -> None:
        """
        Add success message to block.

        Args:
            tag_stakeholders (bool, optional): Whether to tag stakeholders in the message. Defaults to False.
        """
        block_elements = [{"type": "mrkdwn", "text": " *Job Successful* !! :tada: "}]

        if tag_stakeholders and self.stakeholders:
            block_elements.append({"type": "mrkdwn", "text": self.build_tag_stakeholder_message()})

        self.blocks.append(
            {
                "type": "context",
                "elements": block_elements,
            }
        )

        self.update_block_message()

    def add_error_block(self, error_message: str | None = None, tag_stakeholders: bool = False) -> None:
        """
        Add error block to the Slack message block.

        Args:
            error_message (str, optional): Plain error text message. Defaults to None.
            tag_stakeholders (bool, optional): Whether to tag stakeholders in the message. Defaults to False.
        """
        block_elements = [{"type": "mrkdwn", "text": " *Job Unsuccessful* :disappointed_relieved: "}]

        if error_message is not None:
            block_elements.append({"type": "mrkdwn", "text": f" *Error Message* : {error_message} \n"})

        if tag_stakeholders and self.stakeholders:
            block_elements.append({"type": "mrkdwn", "text": self.build_tag_stakeholder_message()})

        self.blocks.append(
            {
                "type": "context",
                "elements": block_elements,
            }
        )

        self.update_block_message()

    def build_tag_stakeholder_message(self) -> str:
        """
        Builds a message tagging all stakeholders, with each tag on a new line.

        Returns:
            str: The message containing the tags of all stakeholders, or an empty string if there are no stakeholders.
        """
        if not self.stakeholders:
            return ""
        else:
            message = ""
            for name, member_id in self.stakeholders.items():
                message += f"<@{member_id}>\n"
            return message
