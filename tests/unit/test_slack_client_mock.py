import unittest
from unittest.mock import patch
import os
from data_slack_client.models.config_model import SlackConfig
from data_slack_client.slack_client import SlackClient

SEND_TO_SLACK = os.getenv("SEND_TO_SLACK", "false").lower() == "true"

@unittest.skipUnless(SEND_TO_SLACK, "Skipping tests because SEND_TO_SLACK is not set to true")
class TestSlackClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("data_slack_client.slack_client.WebClient")
        cls.mock_web_client = cls.patcher.start()

    def setUp(self):
        # Reset mock to clear call history before each test
        self.mock_web_client.reset_mock()
        # Mock instance of WebClient is also reset
        self.mock_slack_client_instance = self.mock_web_client.return_value

        self.slack_channel = "test_channel"
        self.header = "Test Job"
        self.message = "Test Message"
        self.user = "U123456"
        self.job_name = "Test Job Name"
        self.img_url = "Test Image URL"
        self.img_alt_text = "Test Alt text"

        self.stakeholders = {"stakeholder1": "U123456", "stakeholder2": "U654321"}

        self.config = SlackConfig(bot_token="test_token", user1="user_1", user2="user_2")
        self.slack_client = SlackClient(
            config=self.config,
            slack_channel=self.slack_channel,
            init_block=False,
            stakeholders=self.stakeholders,
        )

    @classmethod
    def tearDownClass(cls):
        # Stop the patcher once after all tests are done
        cls.patcher.stop()

    def test_post_simple_message_success(self):
        """Test posting a simple message successfully."""
        self.slack_client.post_simple_message(self.message)
        self.mock_slack_client_instance.chat_postMessage.assert_called_once_with(
            channel=f"#{self.slack_channel}", text=self.message
        )

    def test_post_simple_message_with_tag_stakeholders(self):
        """Test posting a simple message with stakeholder tags."""
        self.slack_client.post_simple_message(self.message, tag_stakeholders=True)
        message_with_tags = f"{self.message}\n<@U123456>\n<@U654321>\n"
        self.mock_slack_client_instance.chat_postMessage.assert_called_once_with(
            channel=f"#{self.slack_channel}", text=message_with_tags
        )

    def test_send_secret_message_in_channel_success(self):
        """Test sending a secret message to a channel successfully."""
        self.slack_client.send_secret_message_in_channel(self.message, self.user)
        self.mock_slack_client_instance.chat_postEphemeral.assert_called_once_with(
            channel=f"#{self.slack_channel}", text=self.message, user=self.user
        )

    def test_send_block_message(self):
        """Test sending a block message."""
        self.slack_client.send_block_message()
        self.mock_slack_client_instance.chat_postMessage.assert_called_once()

    def test_update_block_message(self):
        """Test updating a block message."""
        # Simulate a successful chat_postMessage to set the response
        self.mock_slack_client_instance.chat_postMessage.return_value = {
            "channel": self.slack_channel,
            "ts": "123.456",
        }
        self.slack_client.send_block_message()
        # Test update_block_message
        self.slack_client.update_block_message()
        self.mock_slack_client_instance.chat_update.assert_called_once()

    def test_initialize_block_message(self):
        """Test initializing and sending a block message."""
        # This will also implicitly test send_block_message
        self.slack_client.initialize_block_message(self.job_name)
        self.mock_slack_client_instance.chat_postMessage.assert_called_once()

    def test_add_message_block(self):
        """Test adding a message block."""
        self.mock_slack_client_instance.chat_postMessage.return_value = {
            "channel": self.slack_channel,
            "ts": "123.456",
        }
        self.slack_client.send_block_message()  # Setup initial message
        self.slack_client.add_message_block(self.message, self.img_url, self.img_alt_text, temp=False)
        self.mock_slack_client_instance.chat_update.assert_called_once()

    def test_add_success_block(self):
        """Test adding a success message block."""
        # Simulate initial block message post
        self.slack_client.send_block_message()
        # Mock `chat_postMessage` to populate `self.response` as expected
        self.mock_slack_client_instance.chat_postMessage.return_value = {
            "channel": "test_channel",
            "ts": "12345.678",
        }
        # Add success block
        self.slack_client.add_success_block()
        self.assertTrue(any("Job Successful" in block["elements"][0]["text"] for block in self.slack_client.blocks))

    def test_add_error_block(self):
        """Test adding an error message block."""
        # Simulate initial block message post
        self.slack_client.send_block_message()
        # Mock `chat_postMessage` to populate `self.response` as expected
        self.mock_slack_client_instance.chat_postMessage.return_value = {
            "channel": "test_channel",
            "ts": "12345.678",
        }
        # Add error block
        self.slack_client.add_error_block("Error occurred", True)
        self.assertTrue(any("Job Unsuccessful" in block["elements"][0]["text"] for block in self.slack_client.blocks))
        self.assertTrue(any("Error occurred" in block["elements"][1]["text"] for block in self.slack_client.blocks))

    def test_build_tag_stakeholder_message(self):
        """Test building stakeholder tag message."""
        message = self.slack_client.build_tag_stakeholder_message()
        self.assertEqual(message, "<@U123456>\n<@U654321>\n")


if __name__ == "__main__":
    unittest.main()
