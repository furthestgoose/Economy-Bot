from discord.ext import commands
import sqlite3
import datetime

class DailyReward(commands.Cog):
    last_daily_reward = {}  # Class attribute to track last daily rewards

    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('currency.db')
        self.c = self.conn.cursor()

    @commands.command(name="daily", description="Get 1,000 coins a day")
    async def daily(self, ctx):  # Add the context parameter
        user_id = ctx.author.id

        # Check if the user has claimed the daily reward today
        if user_id in DailyReward.last_daily_reward:
            last_claimed = DailyReward.last_daily_reward[user_id]
            if (datetime.datetime.now() - last_claimed).days < 1:
                await ctx.send("You have already claimed your daily reward today.")
                return

        # Give the user the daily reward
        self.c.execute('UPDATE currency SET balance = balance + ? WHERE user_id = ?', (1000, user_id))
        self.conn.commit()
        await ctx.send("You have claimed your daily reward of 1,000 coins!")

        # Update the last claimed time for the user
        DailyReward.last_daily_reward[user_id] = datetime.datetime.now()

def setup(bot):
    bot.add_cog(DailyReward(bot))