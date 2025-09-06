"""
Discord Bot Main Entry Point
Initializes and runs the Discord bot with a modular cog-based structure.
"""

import asyncio
import logging
import os
import discord
from discord.ext import commands

# Import configuration and logger from our utility files
from config import BOT_CONFIG, ERROR_MESSAGES
from utils.logger import setup_logger

# Initialize logging
logger = setup_logger()

class DiscordBot(commands.Bot):
    """An advanced, Cog-based Discord Bot class."""

    def __init__(self):
        # Define the bot's intents to specify which events it will listen to
        intents = discord.Intents.default()
        intents.message_content = True  # Required for reading message content
        intents.members = True          # Required for member join/leave events
        intents.voice_states = True     # Required for voice state events

        super().__init__(
            command_prefix=BOT_CONFIG['command_prefix'],
            intents=intents,
            help_command=None  # We will use a custom help command
        )

    async def setup_hook(self):
        """Asynchronous setup to be performed when the bot starts."""
        logger.info("--- Initializing Bot ---")
        
        # Find all .py files in the 'bot/cogs' folder and load them as extensions
        for filename in os.listdir('./bot/cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'bot.cogs.{filename[:-3]}')
                    logger.info(f"Loaded Cog: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load Cog: {filename} - Error: {e}")
        
        logger.info("--- All Cogs Loaded Successfully ---")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Handles errors that occur in commands globally."""
        prefix = BOT_CONFIG['command_prefix']
        
        if isinstance(error, commands.CommandNotFound):
            logger.warning(f"Unknown command attempt by {ctx.author}: {ctx.message.content}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(ERROR_MESSAGES['missing_required_argument'].format(param_name=error.param.name))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(ERROR_MESSAGES['command_on_cooldown'].format(remaining=error.retry_after))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(ERROR_MESSAGES['no_permission'])
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(ERROR_MESSAGES['bot_missing_permissions'])
        else:
            logger.error(f"An unexpected command error occurred: {error}", exc_info=True)
            await ctx.send(ERROR_MESSAGES['unexpected_error'])


async def main():
    """The main function that runs the bot."""
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if not bot_token:
        logger.critical("DISCORD_BOT_TOKEN not found! Check your .env file.")
        return

    bot = DiscordBot()
    try:
        await bot.start(bot_token)
    except discord.LoginFailure:
        logger.critical("Invalid bot token. Please check your .env file.")
    except Exception as e:
        logger.critical(f"A critical error occurred while starting the bot: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user.")
