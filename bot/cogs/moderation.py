# cogs/moderation.py
import asyncio
import discord
from discord.ext import commands
import logging

# Importing configuration files
from config import COOLDOWNS, ERROR_MESSAGES, SERVER_CHANNELS 

logger = logging.getLogger(__name__)

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clear', aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, COOLDOWNS.get('clear', 10), commands.BucketType.user)
    async def clear_command(self, ctx, amount: int = 5):
        """Clears a specified number of messages from the channel (requires manage messages permission)."""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Amount must be between 1 and 100.")
            return

        try:
            # +1 to include the command message itself
            deleted = await ctx.channel.purge(limit=amount + 1) 

            embed = discord.Embed(
                title="🧹 Messages Cleared",
                description=f"Successfully deleted {len(deleted) - 1} messages.",
                color=discord.Color.green())

            # Delete the confirmation message after 5 seconds
            await ctx.send(embed=embed, delete_after=5.0)

            logger.info(
                f"Clear command executed by {ctx.author} - Deleted {len(deleted) - 1} messages."
            )

        except discord.Forbidden:
            # Error message is fetched from the config file
            await ctx.send(ERROR_MESSAGES['bot_missing_permissions'])
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to delete messages: {e}")
            logger.error(f"Clear command failed: {e}")
    
    # Command name is now in English
    @commands.command(name="rules")
    @commands.has_permissions(administrator=True)
    async def rules_command(self, ctx, *, rules_text: str = ""):
        """Posts the server rules to the designated rules channel."""
        
        # Channel ID is read from the config, which gets it from .env
        rules_channel_id = SERVER_CHANNELS.get('rules_channel_id')
        if not rules_channel_id or ctx.channel.id != rules_channel_id:
            await ctx.send(
                f"❌ This command can only be used in the designated rules channel."
            )
            return

        if not rules_text.strip():
            await ctx.send(
                "❌ Please provide the rules to post.\nExample: `!rules No spamming.`"
            )
            return

        # Purge the channel first to keep it clean
        await ctx.channel.purge(limit=100)

        # Embed title
        embed = discord.Embed(title="📜 • Server Rules • 📜",
                              color=discord.Color.gold(),
                              timestamp=ctx.message.created_at)
        
        if ctx.guild.icon:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.set_footer(text=f"Last updated by {ctx.author.display_name}")

        # Send the embed
        await ctx.send(embed=embed)

        # Send the rules as a separate, plain text message for readability
        formatted_rules = "\n\n".join(
            [line.strip() for line in rules_text.split("\n") if line.strip()])

        await ctx.send(formatted_rules)
        logger.info(f"Server rules updated by {ctx.author}.")


# The setup function required to load this cog from the main bot file
async def setup(bot):
    await bot.add_cog(ModerationCog(bot))