import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
import random
import string

load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to SQLite database
conn = sqlite3.connect('currency.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS currency (
             guild_id INTEGER,
             user_id INTEGER,
             balance INTEGER DEFAULT 0,
             PRIMARY KEY (guild_id, user_id)
             )''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS horses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    name TEXT,
    owner_id INTEGER,
    price INTEGER,
    speed INTEGER,
    stamina INTEGER,
    strength INTEGER
)''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    name TEXT,
    price INTEGER,
    quantity INTEGER
)''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS user_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    stock_id INTEGER,
    quantity INTEGER,
    price INTEGER,
    FOREIGN KEY (user_id) REFERENCES currency(user_id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
)''')
conn.commit()

@bot.slash_command(name = "help", description = "Shows all commands")
async def help(ctx):
    embed = discord.Embed(title="Commands", description="List of all commands", color= discord.Color.light_grey())
    embed.add_field(name="/help", value="Shows all commands", inline=False)
    embed.add_field(name="Money commands", inline=False)
    embed.add_field(name="/daily", value="Claim your daily reward", inline=False)
    embed.add_field(name="/steal", value="Steal coins from a user of your choice", inline=False)
    embed.add_field(name="/transfer", value="Transfer coins to a user of your choice", inline=False)
    embed.add_field(name="/balance", value="Shows your balance", inline=False)
    embed.add_field(name="/view-user-balance", value="View another users balance", inline=False)
    embed.add_field(name="/leaderboard", value="Shows the leaderboard", inline=False)
    embed.add_field(name="Game commands", inline=False)
    embed.add_field(name="/slots", value="Play the slots", inline=False)
    embed.add_field(name="/blackjack", value="Play blackjack", inline=False)
    embed.add_field(name="/coinflip", value="Play coinflip", inline=False)
    embed.add_field(name="Horse commands", inline=False)
    embed.add_field(name="/buy-horse (no name given)", value="View available horses", inline=False)
    embed.add_field(name="/buy-horse (name given)", value="Buy a horse", inline=False)
    embed.add_field(name="/view-horse-upgrade-costs", value="View the costs to upgrade your horse", inline=False)
    embed.add_field(name="/upgrade-horse-stamina", value="Upgrade your horse's stamina", inline=False)
    embed.add_field(name="/upgrade-horse-speed", value="Upgrade your horse's speed", inline=False)
    embed.add_field(name="/upgrade-horse-strength", value="Upgrade your horse's strength", inline=False)
    embed.add_field(name="/view-horse-information", value="View your horse stats", inline=False)
    embed.add_field(name="/horse-race", value="race your horse and bet on the result", inline=False)
    embed.add_field(name="/release-horse", value="Release your horse", inline=False)
    embed.add_field(name="Stock commands", inline=False)
    embed.add_field(name="/view_stocks", value="View all stocks", inline=False)
    embed.add_field(name="/buy_stock", value="Buy a stock", inline=False)
    embed.add_field(name="/sell_stock", value="Sell a stock", inline=False)
    embed.add_field(name="/view_stocks_info", value="View your stocks (prices update every 30 minutes)", inline=False)
    embed.add
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_guild_join(guild):
    for member in guild.members:
        # Check if the member is a bot
        if member.bot:
            continue
        
        # Add the member to the database if not already present
        user_id = member.id
        guild_id = guild.id
        c.execute('INSERT OR IGNORE INTO currency (guild_id, user_id, balance) VALUES (?, ?, ?)', (guild_id, user_id, 1000))
        conn.commit()
        
        # Insert randomly generated horses into the database for each member
       # Lists of naming components
        prefixes = ['Silver', 'Midnight', 'Crimson', 'Ebony', 'Misty', 'Twilight', 'Ember', 'Thunder']
        suffixes = ['Mane', 'Blaze', 'Wind', 'Spirit', 'Whisper', 'Dancer', 'Stride', 'Stride']
        adjectives = ['Wild', 'Majestic', 'Fierce', 'Graceful', 'Brave', 'Noble', 'Regal', 'Valiant']

        for i in range(1, 3 + 1):
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            adjective = random.choice(adjectives)
            name = f"{prefix} {adjective} {suffix}"
            price = random.randint(100000, 500000)
            speed = random.randint(1, 5)
            stamina = random.randint(1, 5)
            strength = random.randint(1, 5)
            c.execute('INSERT INTO horses (guild_id, name, price, speed, stamina, strength) VALUES (?, ?, ?, ?, ?, ?)', (guild_id, name, price, speed, stamina, strength))
            conn.commit()
        
        characters = string.ascii_uppercase + string.digits

        for i in range(1, 40 + 1):
            ticker = ''.join(random.choices(characters, k=random.randint(3, 5)))
            price = random.randint(10, 1000)
            quantity = random.randint(1000, 10000)
            c.execute('INSERT INTO stocks (guild_id, name, price, quantity) VALUES (?, ?, ?, ?)', (guild_id, ticker, price, quantity))
            conn.commit()

@bot.event
async def on_member_join(member):
    # Add the member to the database if not already present
    user_id = member.id
    guild_id = member.guild.id  # Get the guild ID
    c.execute('INSERT OR IGNORE INTO currency (guild_id, user_id, balance) VALUES (?, ?, ?)', (guild_id, user_id, 1000))
    conn.commit()
    
    prefixes = ['Silver', 'Midnight', 'Crimson', 'Ebony', 'Misty', 'Twilight', 'Ember', 'Thunder']
    suffixes = ['Mane', 'Blaze', 'Wind', 'Spirit', 'Whisper', 'Dancer', 'Stride', 'Stride']
    adjectives = ['Wild', 'Majestic', 'Fierce', 'Graceful', 'Brave', 'Noble', 'Regal', 'Valiant']

    for i in range(1, 3 + 1):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        adjective = random.choice(adjectives)
        name = f"{prefix} {adjective} {suffix}"
        price = random.randint(100000, 500000)
        speed = random.randint(1, 5)
        stamina = random.randint(1, 5)
        strength = random.randint(1, 5)
        c.execute('INSERT INTO horses (guild_id, name, price, speed, stamina, strength) VALUES (?, ?, ?, ?, ?, ?)', (guild_id, name, price, speed, stamina, strength))
        conn.commit()

bot.load_extension('cogs.Horses')
bot.load_extension('cogs.Games')
bot.load_extension('cogs.DailyReward')
bot.load_extension('cogs.money')
bot.load_extension('cogs.stocks')
bot.run(os.getenv('TOKEN'))
