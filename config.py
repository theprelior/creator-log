"""
Bot Configuration Module
Contains all configuration settings for the Discord bot, loaded from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- BOT SETTINGS ---
BOT_CONFIG = {
    'command_prefix': os.getenv('COMMAND_PREFIX', '!'),
}

# --- LOGGING SETTINGS ---
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO').upper(),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',

    # --- File Logging Settings ---
    'log_to_file': os.getenv('LOG_TO_FILE', 'False').lower() == 'true',
    'log_file': os.getenv('LOG_FILE', 'bot.log'),
    'max_log_size': int(os.getenv('MAX_LOG_SIZE', 10485760)),  # 10MB
    'backup_count': int(os.getenv('BACKUP_COUNT', 5)),
}

# --- SERVER CHANNEL IDs ---
# Reads channel IDs from the .env file. Defaults to 0 if not found.
SERVER_CHANNELS = {
    'log_channel_id': int(os.getenv('LOG_CHANNEL_ID', 0)),
    'welcome_channel_id': int(os.getenv('WELCOME_CHANNEL_ID', 0)),
    'goodbye_channel_id': int(os.getenv('GOODBYE_CHANNEL_ID', 0)),
    'rules_channel_id': int(os.getenv('RULES_CHANNEL_ID', 0)),
}

# --- COMMAND COOLDOWNS (in seconds) ---
COOLDOWNS = {
    'default': 3,
    'clear': 15, # 1 use per 15 seconds
}

# --- MESSAGES ---
ERROR_MESSAGES = {
    'no_permission': "❌ You do not have permission to use this command.",
    'bot_missing_permissions': "❌ I don't have the required permissions to perform this command.",
    'command_on_cooldown': "❌ This command is on cooldown. Please try again in {remaining:.1f} seconds.",
    'command_not_found': "❌ Command not found. Use `{prefix}help` for a list of available commands.",
    'missing_required_argument': "❌ Missing a required argument for this command: `{param_name}`.",
    'unexpected_error': "❌ An unexpected error occurred. Please try again later."
}
