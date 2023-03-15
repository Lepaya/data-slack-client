# Lepaya Slack Client
The Lepaya Slack Client is a Python library that allows you to interact with the Slack API and send custom messages to your Slack channels. This library was developed by Humaid Mollah for Lepaya.

## Installation
To install the project dependencies, use the following commands:
1. Clone the repository 
2. Navigate to the directory of the cloned repository using the cd command.
3. ``pipenv sync`` (to download all dependencies from the Pipfile)
4. ``pipenv shell`` (to create a new virtual environment and activate it)

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
    channel='YOUR_CHANNEL_NAME_HERE',
    user1='YOUR_USER_1_NAME_HERE',
    user2='YOUR_USER_2_NAME_HERE'
)
````

````
slack = SlackClient(config)
````

Make sure to replace YOUR_BOT_TOKEN_HERE, YOUR_CHANNEL_NAME_HERE, YOUR_USER_1_NAME_HERE, and YOUR_USER_2_NAME_HERE with the actual values for your Slack configuration.

### Functions

The following methods are available for use:

- ``post_simple_message``: Send a simple message to a Slack channel.
send_secret_message_in_channel: Send a message to a Slack channel that can only be seen by a specific user.
- ``initialize_block_message``: Initialize a custom block message for Python Jobs and send it.
- ``add_message_block``: Add a message to the Slack block message.
- ``add_success_block``: Add a success message to the Slack block message.
- ``add_error_block``: Add an error message to the Slack block message.
- ``notify_error_block``: Notify specific users to fix an error in the Slack block message.
