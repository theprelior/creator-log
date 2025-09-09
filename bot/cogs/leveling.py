import discord
from discord.ext import commands
import logging

# Import our new JSON handler
from utils.json_handler import load_data

logger = logging.getLogger(__name__)

class LevelingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Leveling Cog loaded.")

    # A helper function to calculate XP for the next level
    def get_xp_for_level(self, level: int):
        return 5 * (level ** 2) + (50 * level) + 100

    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Checks the rank and level of a user."""
        # If no member is specified, default to the command author
        target = member or ctx.author
        
        # Load the leveling data
        data = await load_data()
        
        # Get the data for the current server
        guild_id = str(ctx.guild.id)
        user_id = str(target.id)
        
        guild_data = data.get(guild_id, {})
        user_data = guild_data.get(user_id)
        
        # Check if the user has any data
        if not user_data:
            await ctx.send(f"**{target.display_name}** hasn't earned any XP yet.")
            return
            
        # Get current xp and level
        xp = user_data.get("xp", 0)
        level = user_data.get("level", 0)
        
        # Calculate XP needed for next level
        xp_needed = self.get_xp_for_level(level)
        
        # Create a simple progress bar
        progress = int((xp / xp_needed) * 20)
        progress_bar = '🟩' * progress + '⬛' * (20 - progress)

        # Create the embed
        embed = discord.Embed(
            title=f"{target.display_name}'s Rank",
            color=target.color,
            timestamp=ctx.message.created_at
        )
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
            
        embed.add_field(name="Level", value=f"**`{level}`**", inline=True)
        embed.add_field(name="XP", value=f"**`{xp} / {xp_needed}`**", inline=True)
        embed.add_field(name="Progress", value=f"`{progress_bar}`", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=['lb'])
    async def leaderboard(self, ctx):
        """Shows the server's top 10 users."""
        data = await load_data()
        guild_id = str(ctx.guild.id)
        
        guild_data = data.get(guild_id)
        if not guild_data:
            await ctx.send("The leaderboard is currently empty!")
            return
            
        # Sort users by XP in descending order
        sorted_users = sorted(guild_data.items(), key=lambda item: item[1].get('xp', 0), reverse=True)
        
        # Create the embed
        embed = discord.Embed(
            title=f"🏆 {ctx.guild.name} Leaderboard",
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at
        )
        
        description = ""
        # Get top 10 or fewer if the server has less than 10 members with XP
        for i, (user_id, user_data) in enumerate(sorted_users[:10]):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User ID: {user_id}"
            level = user_data.get('level', 0)
            xp = user_data.get('xp', 0)
            
            # Use emoji for top 3
            rank_emoji = ""
            if i == 0: rank_emoji = "🥇"
            elif i == 1: rank_emoji = "🥈"
            elif i == 2: rank_emoji = "🥉"
            else: rank_emoji = f"**#{i+1}**"
            
            description += f"{rank_emoji} **{name}** - Level {level} ({xp} XP)\n"
            
        if not description:
             await ctx.send("The leaderboard is currently empty!")
             return

        embed.description = description
        await ctx.send(embed=embed)


# The setup function required to load this cog
async def setup(bot):
    await bot.add_cog(LevelingCog(bot))

