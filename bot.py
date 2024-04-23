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
