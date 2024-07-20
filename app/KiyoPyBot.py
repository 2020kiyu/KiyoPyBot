import os
import asyncio
import json
import discord
import logging
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    print(f'Ping')
    await ctx.send("Pong!")

bot.run(os.getenv('BOT_TOKEN'))
