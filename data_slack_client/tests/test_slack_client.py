import unittest
from data_slack_client.slack_client import SlackClient
from data_slack_client.models.config_model import SlackConfig

test_config = SlackConfig(
    bot_token='xoxb-2764711569008-4272862514676-zagRpjF0Es6xDf4kA5rcGtYS',
    user1='U03TQ448VS8',  # Can be None
    user2='U03TQ448VS8'  # Can be None
)
slack_channel = 'python-test'
python_job_name = 'Slack-Client Testing'


class TestSlackClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize the SlackClient with valid configuration."""
        cls.client = SlackClient(config=test_config, slack_channel=slack_channel, python_job_name=python_job_name)

    def test_post_simple_message(self):
        """Test posting a simple message."""
        try:
            self.client.post_simple_message("Test simple message from unittest")
            # Manual verification in Slack is required to confirm message posting
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to post simple message: {e}")

    def test_send_secret_message_in_channel(self):
        """Test sending a secret message."""
        valid_user_id = 'valid_user_id'  # Replace with an actual user ID
        try:
            self.client.send_secret_message_in_channel("Secret message test", user=valid_user_id)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to send secret message: {e}")

    def test_send_block_message(self):
        """Test sending a block message."""
        try:
            # Assuming that initialize_block_message has already added a block message
            # This will attempt to send it
            self.client.send_block_message()
            self.assertTrue(True)
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
        self.assertIn('Job Successful', success_block['elements'][0]['text'])

    def test_add_error_block_without_notify(self):
        """Test adding an error block without notification."""
        initial_blocks_count = len(self.client.blocks)
        self.client.add_error_block("Test error", notify=False)
        self.assertTrue(len(self.client.blocks) > initial_blocks_count)
        error_block = self.client.blocks[-1]
        self.assertIn('Error Message', error_block['elements'][0]['text'])

    def test_add_error_block_with_notify(self):
        """Test adding an error block with notification."""
        if self.client.config.user1 or self.client.config.user2:
            initial_blocks_count = len(self.client.blocks)
            self.client.add_error_block("Test error with notify", notify=True)
            self.assertTrue(len(self.client.blocks) > initial_blocks_count)
            notify_block = self.client.blocks[-1]
            self.assertTrue(any('<@' in element['text'] for element in notify_block['elements']))
        else:
            self.skipTest("No user specified in SlackConfig for notification")

    def test_initialize_block_message(self):
        """Test the initialization of the block message."""
        # This method is implicitly tested in setUpClass but can be further tested here
        self.assertTrue(len(self.client.blocks) > 0, "Blocks should have been initialized")
        self.assertIn('Hello *Data Team*!', self.client.blocks[0]['elements'][0]['text'])


if __name__ == "__main__":
    unittest.main()