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

# データ保存ファイル
DATA_FILE = './user_data.json'

# ロギングの設定
logging.basicConfig(filename='./kiyopybot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_user_data():
    global USER_DATA
    try:
        with open(DATA_FILE, 'r') as f:
            USER_DATA = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        USER_DATA = {}

def save_user_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(USER_DATA, f, indent=4)

@bot.event
async def on_ready():
    global BOT_CHANNEL
    BOT_CHANNEL = bot.get_channel(int(os.getenv('BOT_CHANNEL_ID')))
    
    # ロール「レベル0」を準備
    await get_roles("レベル0")
    
    # ユーザーデータをロード
    load_user_data()
    
    # ユーザーデータに基づいてロールを付け替え
    guild = BOT_CHANNEL.guild
    for display_name, data in USER_DATA.items():
        member = discord.utils.get(guild.members, display_name=display_name)
        if member:
            next_level_name = f"レベル{data['level']}"
            await add_roles(member, next_level_name)
    
    logging.info(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    next_level_name = "レベル0"
    await add_roles(member, next_level_name)
    await BOT_CHANNEL.send(f'{member.display_name}さんがサーバーに参加しました。レベル0のロールを付与しました。')

@bot.command()
async def hello(ctx):
    logging.info("hello command")
    user_name = ctx.author.display_name
    await ctx.    send(f'{user_name}さん こんちゃす☆彡')

@bot.command()
async def play(ctx):
    logging.info("play command")
    if ctx.author.voice is None:
        await ctx.send("まず、ボイスチャンネルに参加してください。")
        return

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    if vc is None:
        vc = await channel.connect()
    else:
        if vc.channel != channel:
            await vc.move_to(channel)

    vc.stop()  # 再生中の音楽があれば停止
    vc.play(discord.FFmpegPCMAudio(source='https://cdn.glitch.global/4f05773a-2baf-49a4-b4b5-021b91df5740/Loop_music.mp3?v=1721384317738'), after=lambda e: print(f'Error: {e}') if e else None)

    if not vc.is_playing():
        await ctx.send("音楽を再生できませんでした。")
        

@bot.command()
async def stats(ctx):
    display_name = ctx.author.display_name
    if display_name in USER_DATA:
        xp = USER_DATA[display_name]['xp']
        level = USER_DATA[display_name]['level']
        next_level = level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10
        zan_xp = next_xp - xp
        await ctx.send(f'{ctx.author.display_name}さん\n現在のXPは{xp}、レベルは{level}です。\n次のレベルまであと{zan_xp}XPです。')
    else:
        await ctx.send(f'{ctx.author.display_name}さんはまだXPを獲得していません。')

@bot.command()
async def ranking(ctx):
    sorted_users = sorted(USER_DATA.items(), key=lambda x: x[1]['xp'], reverse=True)
    ranking_message = "ランキング:\n"
    for i, (display_name, data) in enumerate(sorted_users, start=1):
        ranking_message += f'{i}. {display_name} - レベル: {data["level"]}, XP: {data["xp"]}\n'
    await ctx.send(ranking_message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    if before.channel is None and after.channel is not None:
        VOICE_CHANNEL_TIMES[member.id] = datetime.now()
        await BOT_CHANNEL.send(f'{member.display_name}さんが {after.channel.name} に参加します！')
    elif before.channel is not None and after.channel is None:
        join_time = VOICE_CHANNEL_TIMES.pop(member.id, None)
        if join_time:
            stay_duration = datetime.now() - join_time
            minutes = int(stay_duration.total_seconds() / 60)
            await BOT_CHANNEL.send(f'{member.display_name}さん、ボイスチャンネルに{minutes:.2f}分間滞在しました。')
            await add_xp_and_check_level_up(member, minutes * 2)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    display_name = message.author.display_name
    xp_to_add = 10
    await add_xp_and_check_level_up(message.author, xp_to_add)

async def add_xp_and_check_level_up(member, xp_to_add):
    display_name = member.display_name
    if display_name not in USER_DATA:
        USER_DATA[display_name] = {'xp': 0, 'level': 0}

    USER_DATA[display_name]['xp'] += xp_to_add
    while True:
        current_xp = USER_DATA[display_name]['xp']
        current_level = USER_DATA[display_name]['level']
        next_level = current_level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10

        if current_xp >= next_xp:
            USER_DATA[display_name]['level'] = next_level
            await BOT_CHANNEL.send(f'{display_name}さん、レベル{next_level}にアップしました！')
            next_level_name = f"レベル{next_level}"
            await add_roles(member, next_level_name)
        else:
            break

    save_user_data()

async def get_roles(next_level):
    guild = BOT_CHANNEL.guild
    role_next_level = discord.utils.get(guild.roles, name=next_level)
    if not role_next_level:
        role_next_level = await guild.create_role(name=next_level, reason=f"{next_level}ロールが存在しないため作成しました。")
    return role_next_level

async def add_roles(member, next_level):
    await remove_all_roles(member)
    role_next_level = await get_roles(next_level)
    await member.add_roles(role_next_level)

async def remove_all_roles(member):
    roles = member.roles[1:]
    if roles:
        await member.remove_roles(*roles)

@bot.command()
async def join(ctx):
    logging.info("JOIN command")
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
    logging.info("GO command")
    if ctx.voice_client:
        # 音声ファイルのパス
        audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source="./loop_music.mp3")
        ctx.voice_client.play(audio_source, after=lambda e: print(f'Error: {e}') if e else None)
        await ctx.send("Playing music!")
    else:
        await ctx.send("Bot is not connected to a voice channel.")

@bot.command()
async def stop(ctx):
    logging.info("STOP command")
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped and disconnected.")
    else:
        await ctx.send("Bot is not in a voice channel.")

bot.run(os.getenv('BOT_TOKEN'))
