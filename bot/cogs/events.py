# bot/cogs/events.py
import logging
import discord
from discord.ext import commands
from datetime import datetime

# Importing configuration files
from config import SERVER_CHANNELS

logger = logging.getLogger(__name__)

class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_log_channel(self):
        """Finds and returns the log channel based on its ID."""
        log_channel_id = SERVER_CHANNELS.get('log_channel_id')
        if not log_channel_id:
            return None
        
        channel = self.bot.get_channel(log_channel_id)
        if not channel:
            logger.warning(f"Log channel with ID {log_channel_id} not found.")
        return channel

    async def get_executor(self, guild, action, target=None):
        """Finds the user who performed a specific action from the audit log."""
        try:
            async for entry in guild.audit_logs(limit=5, action=action):
                if target and hasattr(entry.target, "id") and entry.target.id == target.id:
                    return entry.user
            # If not found in the targeted search, assume the last non-targeted action
            async for entry in guild.audit_logs(limit=1, action=action):
                return entry.user
        except discord.Forbidden:
            return None # If permission to access audit log is denied
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        # This check prevents on_ready from running again when the bot reconnects,
        # it only runs on the initial startup.
        if not hasattr(self.bot, 'ready_once'):
            self.bot.ready_once = True
            logger.info(f"Bot logged in as {self.bot.user} (ID: {self.bot.user.id})")
            logger.info(f"Connected to {len(self.bot.guilds)} guilds")
            activity = discord.Activity(type=discord.ActivityType.listening, name=f"{self.bot.command_prefix}help")
            await self.bot.change_presence(activity=activity)
        else:
            logger.info("Bot reconnected.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by the bot itself or other bots
        if message.author.bot:
            return
        # Log when the bot is mentioned (optional)
        if self.bot.user in message.mentions:
            logger.info(f"Bot mentioned by {message.author} in #{message.channel}: {message.content[:100]}")
        # IMPORTANT: process_commands is not called within on_message in a Cog setup.
        # The main Bot class already handles this.

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_channel_id = SERVER_CHANNELS.get('welcome_channel_id')
        if not welcome_channel_id: return
        channel = self.bot.get_channel(welcome_channel_id)
        if channel:
            embed = discord.Embed(
                title="📥 Welcome to the Server!",
                description=f"Welcome, {member.mention}! We're happy to have you.",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            if member.avatar: embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.guild.name} • Total Members: {member.guild.member_count}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        goodbye_channel_id = SERVER_CHANNELS.get('goodbye_channel_id')
        if not goodbye_channel_id: return
        channel = self.bot.get_channel(goodbye_channel_id)
        if channel:
            embed = discord.Embed(
                title="📤 A Member Left",
                description=f"**{member.name}#{member.discriminator}** has left the server.",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            if member.avatar: embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.guild.name} • Total Members: {member.guild.member_count}")
            await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.content: return
        log_channel = await self.get_log_channel()
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=f"A message sent by **{message.author.mention}** in **#{message.channel.name}** was deleted.",
                color=discord.Color.orange(), timestamp=datetime.utcnow()
            )
            embed.add_field(name="Message Content", value=f"```{message.content}```", inline=False)
            embed.set_footer(text=f"User ID: {message.author.id}")
            await log_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content: return
        log_channel = await self.get_log_channel()
        if log_channel:
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"**{before.author.mention}** edited their [message]({after.jump_url}) in **#{before.channel.name}**.",
                color=discord.Color.blue(), timestamp=datetime.utcnow()
            )
            embed.add_field(name="Original Message", value=f"```{before.content}```", inline=False)
            embed.add_field(name="New Message", value=f"```{after.content}```", inline=False)
            embed.set_footer(text=f"User ID: {before.author.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot or before.channel == after.channel: return
        log_channel = await self.get_log_channel()
        if log_channel:
            embed = None
            # User joined a channel
            if before.channel is None and after.channel is not None:
                embed = discord.Embed(title="🔊 Joined Voice Channel", description=f"{member.mention} joined the voice channel **{after.channel.name}**.", color=discord.Color.blue(), timestamp=datetime.utcnow())
            # User left a channel
            elif before.channel is not None and after.channel is None:
                embed = discord.Embed(title="🔇 Left Voice Channel", description=f"{member.mention} left the voice channel **{before.channel.name}**.", color=discord.Color.dark_orange(), timestamp=datetime.utcnow())
            # User switched channels
            else:
                embed = discord.Embed(title="🔁 Switched Voice Channel", description=f"{member.mention} switched voice channels.", color=discord.Color.purple(), timestamp=datetime.utcnow())
                embed.add_field(name="From Channel", value=before.channel.name, inline=False)
                embed.add_field(name="To Channel", value=after.channel.name, inline=False)
            
            if embed:
                embed.set_footer(text=f"User ID: {member.id}")
                await log_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        logger.debug(f"Command '{ctx.command}' completed successfully by {ctx.author}")

# The setup function required to load this cog from the main bot file
async def setup(bot):
    await bot.add_cog(EventsCog(bot))