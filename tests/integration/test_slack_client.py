import unittest
from pathlib import Path

from data_slack_client.slack_client import SlackClient
from tests.integration.configs.config_loader import load_config

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CONFIG_FILE_PATH = f"{PROJECT_ROOT}/tests/integration/configs/config.yml"


class TestSlackClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the SlackClient with valid configuration."""
        configs = load_config(CONFIG_FILE_PATH)
        cls.client = SlackClient(
            config=configs.slack,
            slack_channel="python-test",
            init_block=True,
            header="Slack-Client Testing",
        )
        cls.valid_user_id = configs.slack.user1
        cls.invalid_user_id = "Invalid ID"

    def test_post_simple_message(self):
        """Test posting a simple message."""
        try:
            self.client.post_simple_message("Test simple message from unittest")
            # Manual verification in Slack is required to confirm message posting
        except Exception as e:
            self.fail(f"Failed to post simple message: {e}")

    def test_send_secret_message_in_channel(self):
        """Test sending a secret message."""

        try:
            self.client.send_secret_message_in_channel(
                "Secret message test", user=self.valid_user_id
            )
            # Manual verification in Slack is required to confirm message posting
        except Exception as e:
            self.fail(f"Failed to send secret message: {e}")

    def test_send_secret_message_in_channel_invalid_user_id(self):
        """Test sending a secret to an invalid user."""

        with self.assertRaises(ValueError):
            self.client.send_secret_message_in_channel(
                "Secret message test", user=self.invalid_user_id
            )

    def test_send_block_message(self):
        """Test sending a block message."""
        try:
            # Assuming that initialize_block_message has already added a block message
            # This will attempt to send it
            self.client.send_block_message()
        except Exception as e:
            self.fail(f"Failed to send block message: {e}")

    def test_add_message_block(self):
        """Test adding a message block."""
        initial_blocks_count = len(self.client.blocks)
        self.client.add_message_block("Test block message")
        self.assertTrue(len(self.client.blocks) > initial_blocks_count)

    def test_add_success_block(self):
        """Test adding a success message block."""
        self.client.add_success_block()
        # Assuming success block is always added last
        success_block = self.client.blocks[-1]
        self.assertIn("Job Successful", success_block["elements"][0]["text"])

    def test_add_error_block_without_notify(self):
        """Test adding an error block without notification."""
        initial_blocks_count = len(self.client.blocks)
        self.client.add_error_block("Test error", notify=False)
        self.assertTrue(len(self.client.blocks) > initial_blocks_count)
        error_block = self.client.blocks[-1]
        self.assertIn("Error Message", error_block["elements"][0]["text"])

    def test_add_error_block_with_notify(self):
        """Test adding an error block with notification."""
        if self.client.config.user1 or self.client.config.user2:
            initial_blocks_count = len(self.client.blocks)
            self.client.add_error_block("Test error with notify", notify=True)
            self.assertTrue(len(self.client.blocks) > initial_blocks_count)
            notify_block = self.client.blocks[-1]
            self.assertTrue(
                any("<@" in element["text"] for element in notify_block["elements"])
            )
        else:
            self.skipTest("No user specified in SlackConfig for notification")

    def test_initialize_block_message(self):
        """Test the initialization of the block message."""
        # This method is implicitly tested in setUpClass but can be further tested here
        self.assertTrue(
            len(self.client.blocks) > 0, "Blocks should have been initialized"
        )
        self.assertIn(
            "Invoking", self.client.blocks[0]["elements"][0]["text"]
        )


if __name__ == "__main__":
    unittest.main()
