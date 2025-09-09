import logging
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random

# Importing configuration files and our JSON handler
from config import SERVER_CHANNELS
from utils.json_handler import load_data, save_data

logger = logging.getLogger(__name__)

class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # A dictionary to handle per-user cooldowns for XP
        self.xp_cooldowns = {}

    # This helper function is also in LevelingCog, but having it here prevents
    # needing to fetch the other cog just for this calculation.
    def get_xp_for_level(self, level: int):
        """Calculates the total XP needed to reach a certain level."""
        return 5 * (level ** 2) + (50 * level) + 100

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        This event is triggered for every message. It handles logging mentions
        and granting XP to users.
        """
        # --- PRE-CHECKS: Ignore messages we don't want to process ---
        # Ignore messages from DMs, bots, or that start with the command prefix
        if message.author.bot or not message.guild:
            return

        # Log when the bot is mentioned (optional)
        if self.bot.user in message.mentions:
            logger.info(f"Bot mentioned by {message.author} in #{message.channel}: {message.content[:100]}")

        # If the message is a command, don't grant XP for it
        if message.content.startswith(self.bot.command_prefix):
            return

        # --- XP GRANTING LOGIC ---
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        # Cooldown check: users can only get XP once every 60 seconds
        now = datetime.utcnow()
        cooldown_key = (guild_id, user_id)
        
        if cooldown_key in self.xp_cooldowns and now < self.xp_cooldowns[cooldown_key]:
            return # User is on cooldown, do nothing
        
        self.xp_cooldowns[cooldown_key] = now + timedelta(seconds=60)
        
        data = await load_data()
        
        data.setdefault(guild_id, {})
        data[guild_id].setdefault(user_id, {"xp": 0, "level": 0})
        
        xp_to_add = random.randint(15, 25)
        data[guild_id][user_id]["xp"] += xp_to_add
        
        # --- LEVEL UP CHECK ---
        current_level = data[guild_id][user_id]["level"]
        current_xp = data[guild_id][user_id]["xp"]
        xp_needed = self.get_xp_for_level(current_level)
        
        if current_xp >= xp_needed:
            data[guild_id][user_id]["level"] += 1
            data[guild_id][user_id]["xp"] -= xp_needed # Carry over remaining XP
            
            new_level = data[guild_id][user_id]["level"]
            logger.info(f"LEVEL UP: {message.author} has reached level {new_level} in {message.guild.name}.")
            
            level_up_embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"Congratulations, {message.author.mention}! You've reached **Level {new_level}**!",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=level_up_embed, delete_after=10)
        
        await save_data(data)

    # --- Other events remain the same ---

    async def get_log_channel(self):
        """Finds and returns the log channel based on its ID."""
        log_channel_id = SERVER_CHANNELS.get('log_channel_id')
        if not log_channel_id: return None
        channel = self.bot.get_channel(log_channel_id)
        if not channel:
            logger.warning(f"Log channel with ID {log_channel_id} not found.")
        return channel

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, 'ready_once'):
            self.bot.ready_once = True
            logger.info(f"Bot logged in as {self.bot.user} (ID: {self.bot.user.id})")
            logger.info(f"Connected to {len(self.bot.guilds)} guilds")
            activity = discord.Activity(type=discord.ActivityType.listening, name=f"{self.bot.command_prefix}help")
            await self.bot.change_presence(activity=activity)
        else:
            logger.info("Bot reconnected.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_channel_id = SERVER_CHANNELS.get('welcome_channel_id')
        if not welcome_channel_id: return
        channel = self.bot.get_channel(welcome_channel_id)
        if channel:
            embed = discord.Embed(title="📥 Welcome to the Server!", description=f"Welcome, {member.mention}! We're happy to have you.", color=discord.Color.green(), timestamp=datetime.utcnow())
            if member.avatar: embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.guild.name} • Total Members: {member.guild.member_count}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        goodbye_channel_id = SERVER_CHANNELS.get('goodbye_channel_id')
        if not goodbye_channel_id: return
        channel = self.bot.get_channel(goodbye_channel_id)
        if channel:
            embed = discord.Embed(title="📤 A Member Left", description=f"**{member.name}#{member.discriminator}** has left the server.", color=discord.Color.red(), timestamp=datetime.utcnow())
            if member.avatar: embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.guild.name} • Total Members: {member.guild.member_count}")
            await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.content: return
        log_channel = await self.get_log_channel()
        if log_channel:
            embed = discord.Embed(title="🗑️ Message Deleted", description=f"A message sent by **{message.author.mention}** in **#{message.channel.name}** was deleted.", color=discord.Color.orange(), timestamp=datetime.utcnow())
            embed.add_field(name="Message Content", value=f"```{message.content}```", inline=False)
            embed.set_footer(text=f"User ID: {message.author.id}")
            await log_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content: return
        log_channel = await self.get_log_channel()
        if log_channel:
            embed = discord.Embed(title="✏️ Message Edited", description=f"**{before.author.mention}** edited their [message]({after.jump_url}) in **#{before.channel.name}**.", color=discord.Color.blue(), timestamp=datetime.utcnow())
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
            if before.channel is None and after.channel is not None:
                embed = discord.Embed(title="🔊 Joined Voice Channel", description=f"{member.mention} joined the voice channel **{after.channel.name}**.", color=discord.Color.blue(), timestamp=datetime.utcnow())
            elif before.channel is not None and after.channel is None:
                embed = discord.Embed(title="🔇 Left Voice Channel", description=f"{member.mention} left the voice channel **{before.channel.name}**.", color=discord.Color.dark_orange(), timestamp=datetime.utcnow())
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

# The setup function required to load this cog
async def setup(bot):
    await bot.add_cog(EventsCog(bot))

