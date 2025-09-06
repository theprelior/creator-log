# cogs/general.py
import time
import discord
from discord.ext import commands
import logging

# Configuration can be imported if needed, e.g., for the prefix
from config import BOT_CONFIG

logger = logging.getLogger(__name__)

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Checks the bot's latency."""
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        websocket_latency = self.bot.latency * 1000

        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green(), timestamp=ctx.message.created_at)
        embed.add_field(name="Response Time", value=f"{response_time:.2f}ms", inline=True)
        embed.add_field(name="WebSocket Latency", value=f"{websocket_latency:.2f}ms", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await message.edit(content=None, embed=embed)
        logger.info(f"Ping command executed by {ctx.author}.")

    @commands.command(name='info', aliases=['about'])
    async def info_command(self, ctx): 
        """Displays information about the bot."""
        embed = discord.Embed(title="🤖 Bot Information",
                              color=discord.Color.blue(),
                              timestamp=ctx.message.created_at)

        # Bot statistics
        embed.add_field(
            name="📊 Statistics",
            value=f"Servers: {len(self.bot.guilds)}\nUsers: {len(self.bot.users)}\nCommands: {len(self.bot.commands)}",
            inline=True)

        # Bot status
        embed.add_field(
            name="🔧 Status",
            value=f"Latency: {self.bot.latency*1000:.2f}ms\nPrefix: `{BOT_CONFIG['command_prefix']}`",
            inline=True)

        # Version info
        embed.add_field(
            name="📋 Version",
            value=f"discord.py: {discord.__version__}",
            inline=True)

        if self.bot.user and self.bot.user.avatar:
             embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")

        await ctx.send(embed=embed)
        logger.info(f"Info command executed by {ctx.author}.")

# The setup function required to load this cog from the main bot file
async def setup(bot):
    await bot.add_cog(GeneralCog(bot))