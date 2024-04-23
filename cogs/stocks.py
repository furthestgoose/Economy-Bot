import asyncio
import discord
from discord.ext import commands
import sqlite3
import random

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('currency.db')
        self.c = self.conn.cursor()

        # Start the background task to update stock prices
        self.bot.loop.create_task(self.update_stock_prices())

    async def update_stock_prices(self):
        while True:
            # Retrieve all stocks from the database
            self.c.execute('SELECT * FROM stocks')
            all_stocks = self.c.fetchall()

            # Update prices for each stock
            for stock in all_stocks:
                stock_id, stock_guild_id, name, price, quantity = stock
                # Generate a random price change within a certain range
                price_change = random.uniform(-20, 20)  # Adjust the range as needed
                # Calculate the total amount bought and sold for the stock
                self.c.execute('SELECT SUM(quantity) FROM user_stocks WHERE stock_id = ?', (stock_id,))
                bought = self.c.fetchone()[0] or 0
                self.c.execute('SELECT SUM(quantity) FROM user_stocks WHERE stock_id = ? AND quantity < 0', (stock_id,))
                sold = self.c.fetchone()[0] or 0
                # Adjust the price based on demand and supply dynamics
                demand_supply_factor = (bought - sold) / quantity if quantity != 0 else 0
                price_change += demand_supply_factor * 2  # Adjust the scaling factor as needed
                new_price = max(price + price_change, 1)  # Ensure the price doesn't go below 1
                # Round the new price to the nearest whole number
                new_price = round(new_price)
                # Update the price of the stock in the database
                self.c.execute('UPDATE stocks SET price = ? WHERE id = ?', (new_price, stock_id))

            self.conn.commit()

            await asyncio.sleep(1800)  # Wait for 30 minutes before updating prices again

    @commands.slash_command(name="view_stocks", description="View the available stocks")
    async def view_stocks(self, ctx):
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        # Retrieve 5 random stocks with available quantity from the database for the guild
        self.c.execute('SELECT * FROM stocks WHERE quantity > 0 AND guild_id = ? ORDER BY RANDOM() LIMIT 5', (guild_id,))
        stocks = self.c.fetchall()

        if stocks:
            # Format the information about each stock
            stock_info = []
            for stock in stocks:
                stock_id, stock_guild_id, name, price, quantity = stock
                stock_info.append(f"Name: {name}, Price: {price:,}, Quantity: {quantity} stocks")

            # Send the formatted list of stocks as a message
            embed = discord.Embed(
                title="Stock List",
                description="\n".join(stock_info),
                color=discord.Colour.dark_gray(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Error",
                description="No free stocks available",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)

    @commands.slash_command(name="buy_stock", description="Buy a stock")
    async def buy_stocks(self, ctx, stock_name: str, quantity: int):
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        # Check if the quantity requested is valid
        if quantity < 1:
            await ctx.respond("Quantity must be at least 1.")
            return

        self.c.execute('SELECT * FROM stocks WHERE name = ? AND quantity > 0 AND guild_id = ?', (stock_name, guild_id))
        stock = self.c.fetchone()

        if stock:
            stock_id, stock_guild_id, name, price, available_quantity = stock
            # Check if the requested quantity is available
            if quantity <= available_quantity:
                # Check if the user has enough coins to purchase the stock
                self.c.execute('SELECT balance FROM currency WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
                row = self.c.fetchone()
                if row and row[0] >= price * quantity:
                    # Deduct the total price from the user's balance
                    total_price = price * quantity
                    self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ? AND guild_id = ?', (total_price, user_id, guild_id))
                    # Add the purchased stocks to the user's portfolio
                    self.c.execute('INSERT INTO user_stocks (user_id, stock_id, quantity,price) VALUES (?, ?, ?,?)', (user_id, stock_id, quantity,total_price))
                    # Update the available quantity of the stock
                    new_quantity = available_quantity - quantity
                    self.c.execute('UPDATE stocks SET quantity = ? WHERE id = ?', (new_quantity, stock_id))
                    self.conn.commit()
                    embed = discord.Embed(
                        title="Stock Purchase",
                        description=f"You've successfully purchased {quantity} shares of {name} for {total_price:,} coins!",
                        color=discord.Colour.green(),
                    )
                    await ctx.respond(embed=embed)
                else:
                    await ctx.respond("You don't have enough coins to purchase this stock.")
            else:
                await ctx.respond("There are not enough shares available for purchase.")
        else:
            await ctx.respond("Invalid stock name.")

    @discord.slash_command(name="view_stocks_info", description="View information about the stocks you own")
    async def view_stocks_info(self, ctx):
        user_id = ctx.author.id
        guild_id = ctx.guild.id 

        # Retrieve the stocks owned by the user from the database
        self.c.execute('SELECT s.name, SUM(us.quantity), us.price FROM user_stocks AS us INNER JOIN stocks AS s ON us.stock_id = s.id WHERE us.user_id = ? AND s.guild_id = ? GROUP BY s.name', (user_id, guild_id))
        user_stocks = self.c.fetchall()

        if user_stocks:
            stock_info = []
            total_change = 0
            for stock in user_stocks:
                name, total_quantity, purchase_price = stock
                # Retrieve the current price of the stock
                self.c.execute('SELECT price FROM stocks WHERE name = ? AND guild_id = ?', (name, guild_id))
                current_price = self.c.fetchone()[0]
                # Calculate the change in price
                change = current_price - purchase_price
                total_change += change * total_quantity
                # Calculate the percentage change in price
                if purchase_price != 0:
                    change_percentage = ((current_price - purchase_price) / purchase_price) * 100
                else:
                    change_percentage = 0
                stock_info.append(f"Name: {name}, Quantity: {total_quantity}, Current Price: {current_price}, Change (%): {change_percentage:.2f}%")

            # Send the formatted list of stocks along with the total change
            embed = discord.Embed(
                title="Your Stocks Information",
                description="\n".join(stock_info),
                color=discord.Colour.dark_blue(),
            )
            embed.add_field(name="Total Change", value=f"{total_change}")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="No Stocks Owned",
                description="You currently do not own any stocks.",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)



    @discord.slash_command(name="sell_stock", description="Sell a stock")
    async def sell_stock(self, ctx, stock_name: str, quantity: int):
        user_id = ctx.author.id
        guild_id = ctx.guild.id 

        # Check if the quantity requested is valid
        if quantity < 1:
            await ctx.respond("Quantity must be at least 1.")
            return

        # Retrieve the stock details from the database
        self.c.execute('SELECT * FROM stocks WHERE name = ? AND guild_id = ?', (stock_name, guild_id))
        stock = self.c.fetchone()

        if stock:
            stock_id, stock_guild_id, name, current_price, available_quantity = stock
            # Retrieve the user's stock details
            self.c.execute('SELECT * FROM user_stocks WHERE user_id = ? AND stock_id = ?', (user_id, stock_id))
            user_stock = self.c.fetchone()

            if user_stock:
                user_stock_id, user_id, stock_id, user_quantity, purchase_price = user_stock
                # Check if the user has enough stocks to sell
                if quantity <= user_quantity:
                    # Calculate the total price for selling the stocks
                    total_price = current_price * quantity
                    # Calculate the profit or loss based on the difference between the current price and the purchase price
                    profit_loss = (current_price - purchase_price) * quantity
                    # Update the user's balance by adding the total price (including profit/loss)
                    self.c.execute('UPDATE currency SET balance = balance + ? WHERE user_id = ? AND guild_id = ?', (total_price, user_id, guild_id))
                    # Update the user's stock quantity by subtracting the sold quantity
                    new_quantity = user_quantity - quantity
                    if new_quantity == 0:
                        # If the user sells all their stocks, remove the entry from the user_stocks table
                        self.c.execute('DELETE FROM user_stocks WHERE id = ?', (user_stock_id,))
                    else:
                        self.c.execute('UPDATE user_stocks SET quantity = ? WHERE id = ?', (new_quantity, user_stock_id))
                    self.conn.commit()

                    if profit_loss >= 0:
                        sale_message = f"You've successfully sold {quantity} shares of {name} for {total_price:,} coins!\nProfit: {profit_loss:,} coins"
                        color = discord.Colour.green()
                    else:
                        sale_message = f"You've sold {quantity} shares of {name} for {total_price:,} coins, incurring a loss of {-profit_loss:,} coins."
                        color = discord.Colour.red()

                    embed = discord.Embed(
                        title="Stock Sale",
                        description=sale_message,
                        color=color,
                    )
                    await ctx.respond(embed=embed)
                else:
                    await ctx.respond("You don't have enough stocks to sell.")
            else:
                await ctx.respond("You don't own any shares of this stock.")
        else:
            await ctx.respond("Invalid stock name.")



def setup(bot):
    bot.add_cog(Stocks(bot))
