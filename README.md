Modular Discord Bot
A modern, modular Discord bot built with Python and the discord.py library. This bot uses a Cog-based architecture, making it easy to extend, manage, and maintain.

Features
Modular Design: Commands and events are organized into separate 'Cogs' (e.g., general, moderation, events) for clean and scalable code.

Configuration Driven: All sensitive data (like tokens) and server-specific settings (like channel IDs) are managed via a .env file.

Comprehensive Logging: Detailed logging for events, commands, and errors, both in the console and optionally to a file.

General Commands: Includes essential commands like ping and info.

Moderation Tools: Comes with commands like clear (purge messages) and rules posting.

Event Handling: Logs important server events such as member joins/leaves, message edits/deletes, and voice channel activity.

🚀 Setup and Installation
Follow these steps to get the bot running on your own server.

1. Prerequisites
Python 3.8 or higher

A Discord Bot Token from the Discord Developer Portal

2. Clone the Repository
git clone [https://github.com/theprelior/creator-log.git](https://github.com/theprelior/creator-log.git)
cd creator-log

3. Set Up the Environment File
Create a file named .env in the root directory of the project. This file will store your secret token and channel IDs.

Copy the example below into your .env file and fill in the values.

# --- BOT SETTINGS ---
DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
COMMAND_PREFIX="!"

# --- SERVER CHANNEL IDs ---
# You need to enable Developer Mode in Discord to get these IDs.
LOG_CHANNEL_ID="YOUR_LOG_CHANNEL_ID"
WELCOME_CHANNEL_ID="YOUR_WELCOME_CHANNEL_ID"
GOODBYE_CHANNEL_ID="YOUR_GOODBYE_CHANNEL_ID"
RULES_CHANNEL_ID="YOUR_RULES_CHANNEL_ID"

4. Install Dependencies
Install the required Python libraries using the requirements.txt file.

pip install -r requirements.txt

5. Run the Bot
You can now start the bot by running the app.py file.

python app.py

If everything is configured correctly, you will see log messages in your console indicating that the bot has successfully connected to Discord.

Usage
The default command prefix is !. You can change this in the .env file.

!ping - Checks the bot's latency.

!info - Displays information about the bot.

!clear <amount> - Deletes a specified number of messages.

!rules <rules text> - Posts the server rules in the designated channel.