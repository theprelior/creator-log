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

    # A helper function to avoid duplicating the formula
    def get_xp_for_level(self, level: int):
        """Calculates the total XP needed to reach a certain level."""
        return 5 * (level ** 2) + (50 * level) + 100

    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Checks the rank and level of a user."""
        # If no member is specified, default to the command author
        target_user = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(target_user.id)

        data = await load_data()

        # Check if the user has any XP data
        if guild_id in data and user_id in data[guild_id]:
            user_data = data[guild_id][user_id]
            xp = user_data["xp"]
            level = user_data["level"]
            xp_needed = self.get_xp_for_level(level)

            embed = discord.Embed(
                title=f"🏆 Rank for {target_user.display_name}",
                color=target_user.color,
                timestamp=ctx.message.created_at
            )
            if target_user.avatar:
                embed.set_thumbnail(url=target_user.avatar.url)
            
            embed.add_field(name="Level", value=f"`{level}`", inline=True)
            embed.add_field(name="XP", value=f"`{xp} / {xp_needed}`", inline=True)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")

            # Create a simple progress bar
            progress = int((xp / xp_needed) * 20) if xp_needed > 0 else 0
            progress_bar = "✅" * progress + "⬜" * (20 - progress)
            embed.add_field(name="Progress to Next Level", value=f"[{progress_bar}]", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{target_user.display_name} has not earned any XP yet.")

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        """Shows the server's top 10 users, sorted correctly by level then XP."""
        guild_id = str(ctx.guild.id)
        data = await load_data()

        if guild_id not in data or not data[guild_id]:
            await ctx.send("There is no XP data for this server yet.")
            return

        # DÜZELTME: Kullanıcılar önce seviyeye, sonra XP'ye göre sıralanıyor.
        sorted_users = sorted(
            data[guild_id].items(), 
            key=lambda item: (item[1]['level'], item[1]['xp']), 
            reverse=True
        )

        embed = discord.Embed(
            title=f"🏆 Leaderboard for {ctx.guild.name}",
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at
        )

        description = ""
        for i, (user_id, user_data) in enumerate(sorted_users[:10]):
            try:
                # fetch_member kullanmak, üye sunucuda olmasa bile hata vermeden devam etmemizi sağlar
                # ve en güncel bilgiyi alır.
                member = await ctx.guild.fetch_member(int(user_id))
                display_name = member.display_name
            except discord.NotFound:
                display_name = f"Unknown User (ID: {user_id})"
            
            level = user_data['level']
            xp = user_data['xp']
            
            rank_emoji = ""
            if i == 0: rank_emoji = "🥇"
            elif i == 1: rank_emoji = "🥈"
            elif i == 2: rank_emoji = "🥉"
            else: rank_emoji = f"**#{i+1}**"

            description += f"{rank_emoji} **{display_name}** - Level {level} ({xp} XP)\n"

        if not description:
            description = "No users with XP on the leaderboard yet."

        embed.description = description
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")

        await ctx.send(embed=embed)


# The setup function required to load this cog
async def setup(bot):
    await bot.add_cog(LevelingCog(bot))

