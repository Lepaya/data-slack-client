import os
import unittest
from pathlib import Path

from data_slack_client.slack_client import SlackClient
from tests.integration.configs.config_loader import load_config

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CONFIG_FILE_PATH = f"{PROJECT_ROOT}/tests/integration/configs/config.yml"
SEND_TO_SLACK = os.getenv("SEND_TO_SLACK", "false").lower() == "true"


@unittest.skipUnless(SEND_TO_SLACK, "Skipping tests because SEND_TO_SLACK is not set to true")
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
            stakeholders={
                "Humaid Mollah": "U03TQ448VS8",
                "Karolina Osiak": "U03RPSHJHK7",
            },
        )
        cls.valid_user_id = "U03TQ448VS8"
        cls.invalid_user_id = "Invalid ID"

    def test_post_simple_message(self):
        """Test posting a simple message."""
        try:
            self.client.post_simple_message("Test simple message from unittest")
            # Manual verification in Slack is required to confirm message posting
        except Exception as e:
            self.fail(f"Failed to post simple message: {e}")

    def test_post_simple_message_with_tagging(self):
        """Test posting a simple message with stakeholder tagging."""
        try:
            self.client.post_simple_message("Test simple message with tagging", tag_stakeholders=True)
            # Manual verification in Slack is required to confirm message posting
        except Exception as e:
            self.fail(f"Failed to post simple message with tagging: {e}")

    def test_send_secret_message_in_channel(self):
        """Test sending a secret message."""
        try:
            self.client.send_secret_message_in_channel("Secret message test", user_member_id=self.valid_user_id)
            # Manual verification in Slack is required to confirm message posting
        except Exception as e:
            self.fail(f"Failed to send secret message: {e}")

    def test_send_secret_message_in_channel_invalid_user_id(self):
        """Test sending a secret to an invalid user."""
        with self.assertRaises(ValueError):
            self.client.send_secret_message_in_channel("Secret message test", user_member_id=self.invalid_user_id)

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

    def test_add_message_block_with_tagging(self):
        """Test adding a message block with stakeholder tagging."""
        initial_blocks_count = len(self.client.blocks)
        self.client.add_message_block("Test block message with tagging", tag_stakeholders=True)
        self.assertTrue(len(self.client.blocks) > initial_blocks_count)
        message_block = self.client.blocks[-1]
        self.assertTrue(
            any(self.client.stakeholders["Humaid Mollah"] in element["text"] for element in message_block["elements"])
        )
        self.assertTrue(
            any(self.client.stakeholders["Karolina Osiak"] in element["text"] for element in message_block["elements"])
        )

    def test_add_success_block(self):
        """Test adding a success message block."""
        self.client.add_success_block()
        # Assuming success block is always added last
        success_block = self.client.blocks[-1]
        self.assertIn("Job Successful", success_block["elements"][0]["text"])

    def test_add_success_block_with_tagging(self):
        """Test adding a success message block with stakeholder tagging."""
        self.client.add_success_block(tag_stakeholders=True)
        success_block = self.client.blocks[-1]
        self.assertIn("Job Successful", success_block["elements"][0]["text"])
        self.assertTrue(
            any(self.client.stakeholders["Humaid Mollah"] in element["text"] for element in success_block["elements"])
        )
        self.assertTrue(
            any(self.client.stakeholders["Karolina Osiak"] in element["text"] for element in success_block["elements"])
        )

    def test_add_error_block_without_tagging(self):
        """Test adding an error block without stakeholder tagging."""
        initial_blocks_count = len(self.client.blocks)
        self.client.add_error_block("Test error", tag_stakeholders=False)
        self.assertTrue(len(self.client.blocks) > initial_blocks_count)
        error_block = self.client.blocks[-1]
        self.assertIn("Error Message", error_block["elements"][1]["text"])

    def test_add_error_block_with_tagging(self):
        """Test adding an error block with stakeholder tagging."""
        initial_blocks_count = len(self.client.blocks)
        self.client.add_error_block("Test error with tagging", tag_stakeholders=True)
        self.assertTrue(len(self.client.blocks) > initial_blocks_count)
        error_block = self.client.blocks[-1]
        self.assertIn("Error Message", error_block["elements"][1]["text"])
        self.assertTrue(
            any(self.client.stakeholders["Humaid Mollah"] in element["text"] for element in error_block["elements"])
        )
        self.assertTrue(
            any(self.client.stakeholders["Karolina Osiak"] in element["text"] for element in error_block["elements"])
        )

    def test_initialize_block_message(self):
        """Test the initialization of the block message."""
        # This method is implicitly tested in setUpClass but can be further tested here
        self.assertTrue(len(self.client.blocks) > 0, "Blocks should have been initialized")
        self.assertIn("Invoking", self.client.blocks[0]["elements"][0]["text"])


if __name__ == "__main__":
    unittest.main()
