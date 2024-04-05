# money_cog.py
from discord.ext import commands
import sqlite3
import discord
import random

class money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('currency.db')
        self.c = self.conn.cursor()

    @discord.slash_command(name="add", description="Add coins to a user's balance")
    async def add_coins(self, ctx, target_user: discord.Member, amount: int):
        if ctx.author.guild_permissions.administrator:
            if target_user.bot:
                await ctx.respond("You cannot give to a bot!")
                return
            user_id = target_user.id
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
            self.conn.commit()
            await ctx.respond(f"You've added {amount:,} coins to {target_user.display_name}'s balance.")
            guild_name = ctx.guild.name
            await target_user.send(f"{ctx.author.display_name} added {amount:,} coins to your balance in {guild_name}!")
        else:
            await ctx.respond("Only administrators can use this command.")

    @discord.slash_command(name="remove", description="Remove coins from a user's balance")
    async def remove_coins(self, ctx, target_user: discord.Member, amount: int):
        if ctx.author.guild_permissions.administrator:
            if target_user.bot:
                await ctx.respond("You cannot take from a bot!")
                return
            user_id = target_user.id
            self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
            row = self.c.fetchone()
            if row is None:
                await ctx.respond("The target user doesn't have a balance yet.")
            elif row[0] < amount:
                await ctx.respond("The target user doesn't have enough coins.")
            else:
                self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
                self.conn.commit()
                await ctx.respond(f"You've removed {amount:,} coins from {target_user.display_name}'s balance.")
                guild_name = ctx.guild.name
                await target_user.send(f"{ctx.author.display_name} removed {amount:,} coins from your balance in {guild_name}!")
        else:
            await ctx.send("Only administrators can use this command.")
    @discord.slash_command(name="steal", description="Attempt to steal coins from another user")
    async def steal(self,ctx, target_user: discord.Member):
    # Check if the target user is the same as the user invoking the command
        if target_user == ctx.author:
            await ctx.respond("You cannot steal from yourself!")
            return

        # Check if the target user is a bot
        if target_user.bot:
            await ctx.respond("You cannot steal from a bot!")
            return

        # Get the user IDs
        user_id = ctx.author.id
        target_user_id = target_user.id

        # Check if the target user has any coins
        self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (target_user_id,))
        target_user_balance = self.c.fetchone()[0]
        if target_user_balance <= 0:
            await ctx.respond("The target user does not have any coins to steal!")
            return

        # Set the success rate of the steal attempt (adjust as needed)
        success_rate = 0.5  # 50% chance of success

        # Determine if the steal attempt is successful
        if random.random() < success_rate:
            # Successful steal
            stolen_amount = random.randint(1, min(5000, target_user_balance))  # Random amount up to the target's balance or 100
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE user_id = ?', (stolen_amount, user_id))
            self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (stolen_amount, target_user_id))
            self.conn.commit()
            embed = discord.Embed(
                title= "Steal Result",
                description=f"You successfully stole {stolen_amount:,} coins from {target_user.display_name}!",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)

            # Notify the victim
            guild_name = ctx.guild.name
            await target_user.send(f"{ctx.author.display_name} stole {stolen_amount:,} coins from you in {guild_name}!")
        else:
            embed = discord.Embed(
                title= "Steal Result",
                description="Your steal attempt failed! Better luck next time.",
                color=discord.Colour.yellow(),
            )
            # Unsuccessful steal
            await ctx.respond(embed=embed)
            
    @discord.slash_command(name="transfer", description="Transfer coins to another user")
    async def transfer(self,ctx, target_user: discord.Member, amount: int):
        # Check if the target user is the same as the user invoking the command
        if target_user == ctx.author:
            await ctx.respond("You cannot transfer coins to yourself!")
            return
    
        # Check if the target user is a bot
        if target_user.bot:
            await ctx.respond("You cannot transfer coins to a bot!")
            return
    
        # Get the user IDs
        user_id = ctx.author.id
        target_user_id = target_user.id
    
        # Check if the user has enough coins to transfer
        self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
        user_balance = self.c.fetchone()[0]
        if user_balance < amount:
            await ctx.respond("You do not have enough coins to transfer.")
            return
    
        # Transfer the coins
        self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
        self.c.execute('UPDATE currency SET balance = balance + ? WHERE user_id = ?', (amount, target_user_id))
        self.conn.commit()
    
        # Notify both users
        guild_name = ctx.guild.name
        embed = discord.Embed(
                title="Balance",
                description=f"You have transferred {amount:,} coins to {target_user.display_name}.",
                color=discord.Colour.yellow(),
            )
        await ctx.respond(embed=embed)
        await target_user.send(f"{ctx.author.display_name} has transferred {amount:,} coins to you in {guild_name}!")
        
    @discord.slash_command(name = "balance" ,description = "view your balance")
    async def balance(self,ctx):
        user_id = ctx.author.id
        self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
        row = self.c.fetchone()
        if row is None:
            await ctx.respond("You don't have a balance yet. Use `!register` to create an account.")
        else:
            balance = row[0]
            embed = discord.Embed(
                title="Balance",
                description=f"Your balance is {balance:,} coins.",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)
            
    @discord.slash_command(name="leaderboard" ,description = "View the leaderboard")
    async def leaderboard(self,ctx):
        self.c.execute('SELECT user_id, balance FROM currency ORDER BY balance DESC LIMIT 5')
        rows = self.c.fetchall()
        leaderboard = []
        for idx, row in enumerate(rows, 1):
            user_id, balance = row
            user = await self.bot.fetch_user(user_id)
            leaderboard.append(f"{idx}. {user.name}: {balance:,} coins")
        embed = discord.Embed(
            title="Leaderboard",
            description="\n".join(leaderboard),
            color=discord.Colour.yellow(),
            )
        await ctx.respond(embed=embed)

    @discord.slash_command(name="view-users-balance", description="View another user's balance")
    async def userbalance(self, ctx, target_user: discord.Member):
        if target_user.bot:
            await ctx.respond("You cannot view the balance of a bot!")
            return
        else:
            user_id = target_user.id
            self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
            row = self.c.fetchone()
            if row is None:
                embed = discord.Embed(title="User Balance",
                                     description="This user doesn't have a balance yet.",
                                     color=discord.Colour.yellow(),)
            else:
                balance = row[0]
                embed = discord.Embed(title="User Balance", description=f"{target_user.display_name}'s balance is {balance:,} coins.", color=discord.Colour.yellow(),)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(money(bot))
