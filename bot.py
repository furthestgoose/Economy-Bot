import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
import random

load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to SQLite database
conn = sqlite3.connect('currency.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS currency (
             user_id INTEGER PRIMARY KEY,
             balance INTEGER DEFAULT 0
             )''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS horses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    owner_id INTEGER,
    price INTEGER,
    speed INTEGER,
    stamina INTEGER,
    strength INTEGER
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
        c.execute('INSERT OR IGNORE INTO currency (user_id, balance) VALUES (?, ?)', (user_id, 1000))
        conn.commit()
        horse_names = ['Shadow', 'Thunder', 'Blaze', 'Spirit', 'Storm', 'Mystic', 'Midnight', 'Raven', 'Whisper', 'Spirit']
        # Insert randomly generated horses into the database
        for i in range(1, 3 + 1):
            name = random.choice(horse_names) + str(i)
            price = random.randint(100000, 500000)  # Random price between 100 and 1000 coins
            speed = random.randint(1, 10)      # Random speed between 1 and 10
            stamina = random.randint(1, 10)    # Random stamina between 1 and 10
            strength = random.randint(1, 10)   # Random strength between 1 and 10
            c.execute('INSERT INTO horses (name, price, speed, stamina, strength) VALUES (?, ?, ?, ?, ?)', (name, price, speed, stamina, strength))
            conn.commit()
@bot.event
async def on_member_join(member):
    user_id = member.id
    c.execute('INSERT OR IGNORE INTO currency (user_id, balance) VALUES (?, ?)', (user_id, 1000))
    conn.commit()
    horse_names = ['Shadow', 'Thunder', 'Blaze', 'Spirit', 'Storm', 'Mystic', 'Midnight', 'Raven', 'Whisper', 'Spirit']
        # Insert randomly generated horses into the database
    for i in range(1, 3 + 1):
        name = random.choice(horse_names) + str(i)
        price = random.randint(1000, 10000)  # Random price between 100 and 1000 coins
        speed = random.randint(1, 5)      # Random speed between 1 and 10
        stamina = random.randint(1, 5)    # Random stamina between 1 and 10
        strength = random.randint(1, 5)   # Random strength between 1 and 10
        c.execute('INSERT INTO horses (name, price, speed, stamina, strength) VALUES (?, ?, ?, ?, ?)', (name, price, speed, stamina, strength))
        conn.commit()

bot.load_extension('cogs.Horses')
bot.load_extension('cogs.Games')
bot.load_extension('cogs.DailyReward')
bot.load_extension('cogs.money')
bot.run(os.getenv('TOKEN'))
