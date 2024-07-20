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

@bot.command()
async def join(ctx):
    print("JOIN command")
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
    else:
        await ctx.send("ボイスチャンネルに参加してください。")

@bot.command()
async def go(ctx):
    print("GO command")
    if ctx.voice_client:
        # 音声ファイルのパス
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source="./music/loop_music.mp3")
        ctx.voice_client.play(audio_source, after=lambda e: print(f'Error: {e}') if e else None)
        await ctx.send("Playing music!")
    else:
        await ctx.send("Bot is not connected to a voice channel.")

@bot.command()
async def stop(ctx):
    print("STOP command")
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped and disconnected.")
    else:
        await ctx.send("Bot is not in a voice channel.")

bot.run(os.getenv('BOT_TOKEN'))
