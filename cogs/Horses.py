import discord
from discord.ext import commands
import sqlite3
import random

class Horses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('currency.db')
        self.c = self.conn.cursor()

    @discord.slash_command(name="buy-horse", description="View available horses and purchase one")
    async def buy_horse(self, ctx, horse_name: str = None):
        user_id = ctx.author.id

        # If a horse name is provided, attempt to purchase that horse
        if horse_name is not None:
            # Retrieve the horse details from the database based on the provided horse name
            self.c.execute('SELECT * FROM horses WHERE name = ? AND owner_id IS NULL', (horse_name,))
            horse = self.c.fetchone()
    
            if horse:
                horse_id, name, owner_id, price, speed, stamina, strength = horse
                # Check if the horse is not already owned
                if owner_id is None:
                    # Check if the user already owns a horse
                    self.c.execute('SELECT owner_id FROM horses WHERE owner_id = ?', (user_id,))
                    existing_horse = self.c.fetchone()
                    if existing_horse:
                        embed = discord.Embed(
                            title= "Error",
                            description="You already own a horse.",
                            color=discord.Colour.red(),
                        )
                        await ctx.respond(embed=embed)
                        return
                
                    # Check if the user has enough coins to purchase the horse
                    self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
                    row = self.c.fetchone()
                    if row and row[0] >= price:
                        # Deduct the price from the user's balance
                        self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (price, user_id))
                        # Set the horse's owner to the user
                        self.c.execute('UPDATE horses SET owner_id = ? WHERE id = ?', (user_id, horse_id))
                        self.conn.commit()
                        embed = discord.Embed(
                            title= "Horse Purchase",
                            description=f"You've successfully purchased {name} for {price} coins!",
                            color=discord.Colour.green(),
                        )
                        await ctx.respond(embed=embed)
                    else:
                        embed = discord.Embed(
                            title= "Error",
                            description="You don't have enough coins to purchase this horse.",
                            color=discord.Colour.red(),
                        )
                        await ctx.respond(embed=embed)
                else:
                    await ctx.respond("This horse has already been purchased.")
            else:
                embed = discord.Embed(
                            title= "Error",
                            description="Invalid horse name.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
        else:
            # Retrieve 3 random unowned horses from the database
            self.c.execute('SELECT * FROM horses WHERE owner_id IS NULL ORDER BY RANDOM() LIMIT 3')
            horses = self.c.fetchall()

            if horses:
                # Format the information about each horse
                horse_info = []
                for horse in horses:
                    horse_id,name, owner_id, price, speed, stamina, strength = horse
                    horse_info.append(f"Name: {name}, Price: {price}, Speed: {speed}, Stamina: {stamina}, Strength: {strength}")

                # Send the formatted list of horses as a message
                embed = discord.Embed(
                            title= "Horse List",
                            description="\n".join(horse_info),
                            color=discord.Colour.dark_gold(),
                        )
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                            title= "Error",
                            description="No unowned horses found in database",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)

    @discord.slash_command(name="release-horse", description="Release ownership of your horse")
    async def release_horse(self, ctx):
        user_id = ctx.author.id

        # Check if the user owns a horse
        self.c.execute('SELECT * FROM horses WHERE owner_id = ?', (user_id,))
        horse = self.c.fetchone()

        if horse:
            # Release ownership of the horse
            horse_id, name, owner_id, price, speed, stamina, strength = horse
            self.c.execute('UPDATE horses SET owner_id = NULL WHERE owner_id = ?', (user_id,))
            self.conn.commit()
            embed = discord.Embed(
                            title= "Horse Released",
                            description=f"You have released ownership of {name}.",
                            color=discord.Colour.green(),
                        )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own any horse.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)

    # Define a function to calculate the upgrade cost based on the current speed
    def calculate_speed_upgrade_cost(self, current_speed):
        if current_speed == 10:
            return None
        else:
            return 3000 + (current_speed * 4000)  # Example: Base cost of 100 + 50 for each level
    def calculate_strength_upgrade_cost(self, current_strength):
        if current_strength == 10:
            return None
        else:
            return 1000 + (current_strength * 1000)
    def calculate_stamina_upgrade_cost(self, current_stamina):
        if current_stamina == 10:
            return None
        else:
            return 2000 + (current_stamina * 3000)

    @discord.slash_command(name="improve-horse-speed", description="pay to increase your horse speed")
    async def improve_speed(self, ctx):
        user_id = ctx.author.id
    
        # Retrieve the user's horse details from the database
        self.c.execute('SELECT speed FROM horses WHERE owner_id = ?', (user_id,))
        horse = self.c.fetchone()

        if horse:
            current_speed = horse[0]  # Extract the current speed from the tuple
        
            # Check if the current speed is already at the maximum level
            if current_speed >= 10:
                embed = discord.Embed(
                            title= "Error",
                            description="Your horse's speed is already at the maximum level.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
                return
        
            upgrade_cost = self.calculate_speed_upgrade_cost(current_speed)
        
            # Check if the user has enough funds to upgrade
            self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
            row = self.c.fetchone()
        
            if row and row[0] >= upgrade_cost:
                # Deduct the upgrade cost from the user's balance
                self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (upgrade_cost, user_id))
            
                # Increase the horse's speed by 1, but limit it to 10
                new_speed = min(current_speed + 1, 10)
                self.c.execute('UPDATE horses SET speed = ? WHERE owner_id = ?', (new_speed, user_id))
            
                self.conn.commit()
                embed = discord.Embed(
                            title= "Speed Increased",
                            description=f"Speed increased! Your horse's speed is now {new_speed}.",
                            color=discord.Colour.green(),
                        )
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                            title= "Error",
                            description="You don't have enough funds to improve your horse's speed.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own a horse.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)
    
    @discord.slash_command(name="improve-horse-strength", description="pay to increase your horse strength")
    async def improve_strength(self,ctx):
        user_id = ctx.author.id
    
        # Retrieve the user's horse details from the database
        self.c.execute('SELECT strength FROM horses WHERE owner_id = ?', (user_id,))
        horse = self.c.fetchone()

        if horse:
            current_strength = horse[0]  # Extract the current speed from the tuple
        
            # Check if the current speed is already at the maximum level
            if current_strength >= 10:
                embed = discord.Embed(
                            title= "Error",
                            description="Your horse's strength is already at the maximum level.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
                return
        
            upgrade_cost = self.calculate_strength_upgrade_cost(current_strength)
        
            # Check if the user has enough funds to upgrade
            self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
            row = self.c.fetchone()
        
            if row and row[0] >= upgrade_cost:
                # Deduct the upgrade cost from the user's balance
                self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (upgrade_cost, user_id))
            
                # Increase the horse's speed by 1, but limit it to 10
                new_strength = min(current_strength + 1, 10)
                self.c.execute('UPDATE horses SET strength = ? WHERE owner_id = ?', (new_strength, user_id))
            
                self.conn.commit()
                embed = discord.Embed(
                            title= "Strength Increased",
                            description=f"Strength increased! Your horse's speed is now {new_strength}.",
                            color=discord.Colour.green(),
                        )
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                            title= "Error",
                            description="You don't have enough funds to improve your horse's strength.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own a horse.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)
    
    @discord.slash_command(name="improve-horse-stamina", description="pay to increase your horse stamina")
    async def improve_stamina(self,ctx):
        user_id = ctx.author.id
    
        # Retrieve the user's horse details from the database
        self.c.execute('SELECT stamina FROM horses WHERE owner_id = ?', (user_id,))
        horse = self.c.fetchone()

        if horse:
            current_stamina = horse[0]  # Extract the current speed from the tuple
        
            # Check if the current speed is already at the maximum level
            if current_stamina >= 10:
                embed = discord.Embed(
                            title= "Error",
                            description="Your horse's stamina is already at the maximum level.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
                return
        
            upgrade_cost = self.calculate_stamina_upgrade_cost(current_stamina)
        
            # Check if the user has enough funds to upgrade
            self.c.execute('SELECT balance FROM currency WHERE user_id = ?', (user_id,))
            row = self.c.fetchone()
        
            if row and row[0] >= upgrade_cost:
                # Deduct the upgrade cost from the user's balance
                self.c.execute('UPDATE currency SET balance = balance - ? WHERE user_id = ?', (upgrade_cost, user_id))
            
                # Increase the horse's speed by 1, but limit it to 10
                new_stamina = min(current_stamina + 1, 10)
                self.c.execute('UPDATE horses SET stamina = ? WHERE owner_id = ?', (new_stamina, user_id))
            
                self.conn.commit()
                embed = discord.Embed(
                            title= "Stamina Increased",
                            description=f"Stamina increased! Your horse's speed is now {new_stamina}.",
                            color=discord.Colour.green(),
                        )
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                            title= "Error",
                            description="You don't have enough funds to improve your horse's stamina.",
                            color=discord.Colour.red(),
                        )
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own a horse.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)
    @discord.slash_command(name="view-horse-upgrade-costs", description="View the upgrade costs for your horse")
    async def view_costs(self, ctx):
        user_id = ctx.author.id

        # Retrieve the user's horse details from the database
        self.c.execute('SELECT speed, stamina, strength FROM horses WHERE owner_id = ?', (user_id,))
        horse = self.c.fetchone()

        if horse:
            current_speed, current_stamina, current_strength = horse
        
            # Calculate the upgrade costs for each attribute
            speed_upgrade_cost = self.calculate_speed_upgrade_cost(current_speed)
            stamina_upgrade_cost = self.calculate_stamina_upgrade_cost(current_stamina)
            strength_upgrade_cost = self.calculate_strength_upgrade_cost(current_strength)
        
            # Format the costs into a message
            message = ""
            if speed_upgrade_cost is not None:
                message += f"Speed Upgrade Cost: {speed_upgrade_cost}\n"
            if stamina_upgrade_cost is not None:
                message += f"Stamina Upgrade Cost: {stamina_upgrade_cost}\n"
            if strength_upgrade_cost is not None:
                message += f"Strength Upgrade Cost: {strength_upgrade_cost}"
            if message == "":
                message += "all attributes cannot be upgraded any further"
            embed = discord.Embed(
                title="Upgrade Costs",
                description=message,
                color=discord.Colour.dark_gold(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own a horse.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)

    @discord.slash_command(name="view-horse-information", description="View information about your horse")
    async def view_info(self, ctx):
        user_id = ctx.author.id

        # Retrieve the user's horse details from the database
        self.c.execute('SELECT name, speed, stamina, strength FROM horses WHERE owner_id = ?', (user_id,))
        horse = self.c.fetchone()

        if horse:
            name, speed, stamina, strength = horse
        
            # Format the horse information into a message
            message = f"Name: {name}\n"
            message += f"Speed: {speed}\n"
            message += f"Stamina: {stamina}\n"
            message += f"Strength: {strength}"

            embed = discord.Embed(
                title="Horse Information",
                description=message,
                color=discord.Colour.dark_gold(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own a horse.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)

    @discord.slash_command(name="horse-race", description="Initiate a horse race and place a bet")
    async def horse_race(self, ctx, amount: int):
        user_id = ctx.author.id

        # Retrieve the user's horse
        self.c.execute('SELECT * FROM horses WHERE owner_id = ?', (user_id,))
        user_horse = self.c.fetchone()
        if not user_horse:
            embed = discord.Embed(
                            title= "Error",
                            description="You don't own a horse to race.",
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)
            return

        # Retrieve a certain number of random horses from the database
        self.c.execute('SELECT * FROM horses WHERE id != ? ORDER BY RANDOM() LIMIT 3', (user_horse[0],))
        horses = self.c.fetchall()

        # Include the user's horse in the race
        horses.append(user_horse)

        # Simulate the race
        race_results = await self.simulate_race(horses)

        # Prepare the race results message
        message = "Race Results:\n"
        for horse, speed, stamina, strength, race_time in race_results["results"]:
            message += f"{horse}: {race_time} seconds (Speed: {speed}, Stamina: {stamina}, Strength: {strength})\n"

        message += f"\nRace Winner: {race_results['winner']}\n"
        message += f"Winning Time: {race_results['time']} seconds\n"

        # Check if the user's horse won
        if race_results['winner'] == user_horse[1]:
            payout = amount * 4
            self.c.execute('UPDATE currency SET balance = balance + ? WHERE user_id = ?', (payout, ctx.author.id))
            message += f"\nCongratulations! Your horse won the race. You've received {payout} coins."
            embed = discord.Embed(
                            title= "You Win",
                            description=message,
                            color=discord.Colour.green(),
                        )
            await ctx.respond(embed=embed)
        else:
            message += "\nBetter luck next time!"
            embed = discord.Embed(
                            title= "You lose",
                            description=message,
                            color=discord.Colour.red(),
                        )
            await ctx.respond(embed=embed)

    async def simulate_race(self, horses):
        race_results = []

        # Simulate the race by calculating the individual horse stats and race time
        for horse in horses:
            speed = horse[4]
            stamina = horse[5]
            strength = horse[6]
            race_time = await self.calculate_race_time(speed, stamina, strength)
            race_results.append((horse[1], speed, stamina, strength, race_time))

        # Determine the winner based on the race time (lowest time)
        race_results.sort(key=lambda x: x[4])
        winner = race_results[0][0]
        winning_time = race_results[0][4]

        return {"winner": winner, "time": winning_time, "results": race_results}

    async def calculate_race_time(self, speed, stamina, strength):
        # Calculate race time based on the individual stats
        # Horses with higher individual stats will have a lower race time
        return 480 - ((speed * 4) + (stamina * 3)  + (strength * 2))
    
def setup(bot):
    bot.add_cog(Horses(bot))
