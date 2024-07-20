import os
import asyncio
import json
import discord
import logging
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Intents設定
intents = discord.Intents.default()
intents.members = True

# ボットのプレフィックスを設定
bot = commands.Bot(command_prefix='/', intents=intents)

# ユーザーの入退室時間を記録する辞書
VOICE_CHANNEL_TIMES = {}

# ユーザごとのデータ保持
USER_DATA = {}

@bot.event
async def on_ready():
    global BOT_CHANNEL
    BOT_CHANNEL = bot.get_channel(int(os.getenv('BOT_CHANNEL_ID')))
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    print("hello command")
    user_name = ctx.author.display_name
    await ctx.send(f'{user_name}さん こんちゃす☆彡')

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
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source="./loop_music.mp3")
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
