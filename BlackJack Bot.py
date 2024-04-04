import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
import random
import datetime

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


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    user_id = member.id
    c.execute('INSERT OR IGNORE INTO currency (user_id, balance) VALUES (?, ?)', (user_id, 1000))
    conn.commit()
    
bot.load_extension('cogs.Games')
bot.load_extension('cogs.DailyReward')
bot.load_extension('cogs.money')
bot.run(os.getenv('TOKEN'))
