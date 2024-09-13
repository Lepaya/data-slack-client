# Lepaya Slack Client
The Lepaya Slack Client is a Python library that allows you to interact with the Slack API and send custom messages to your Slack channels. This library was developed by Humaid Mollah for Lepaya.

## Pre-requisites

1. Python 3.11
2. Pipenv

## Installation
To install this python package, run the following command:
``pipenv install -e "git+https://github.com/Lepaya/data-slack-client@release-4.0#egg=data-slack-client``

## Usage

### Initialization
This package provides a Slack client that can be used to interact with Slack. 

To initialize the Slack client using the SlackConfig model, follow these steps:

1. First, make sure that you have the SlackConfig model defined in your code.
2. Create an instance of the SlackConfig model by passing in the required parameters for bot_token, channel, user1, and user2.
3. Pass the SlackConfig instance to the SlackClient constructor to create a new instance of the SlackClient class.

Here's an example of how you can do this:

from lepaya_python_slackclient.models.config_model import SlackConfig
from lepaya_python_slackclient.slack_client import SlackClient

````
config = SlackConfig(
    bot_token='YOUR_BOT_TOKEN_HERE',
)
````

````
slack = SlackClient(config: SlackConfig, slack_channel: str, header: str, stakeholders: dict)
````

Make sure to replace YOUR_BOT_TOKEN_HERE, YOUR_CHANNEL_NAME_HERE, YOUR_USER_1_NAME_HERE, and YOUR_USER_2_NAME_HERE with the actual values for your Slack configuration.

### Functions

The following methods are available for use:
- ``__init__(self, config: SlackConfig, slack_channel: str, init_block: bool = True, python_job_name: Union[str, None] = None)``: Initializes the Slack client and optionally sends an introduction message blocks.
- ``post_simple_message(self, message: str)``: Posts a simple plain text message on Slack.
- ``send_secret_message_in_channel(self, message: str, user: str | None = None)``: Sends a secret message on Slack to a particular user.
- ``send_block_message(self)``: Sends a block message on Slack and stores the response.
- ``update_block_message(self)``: Dynamically updates the block message and updates the response.
- ``initialize_block_message(self, job_name: str)``: Initializes the Slack block message and sends it to Slack.
- ``add_message_block(self, message: str, img_url: str | None = None, temp: bool = False)``: Adds a message to the Slack block message.
- ``add_success_block(self)``: Adds a success message to the Slack block message.
- ``add_error_block(self, error_message: str | None = None, notify: bool = False)``: Adds an error block to the Slack message block.
