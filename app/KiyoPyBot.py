import os
import asyncio
import json
import discord
import logging
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from app import music_operations as music
from app import etc_operations as etc
from app import level_operations as level

#############################
# 変数
#############################
#環境変数の読み込み
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# インテントの設定
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# bot初期化
bot = commands.Bot(command_prefix='/', intents=intents)

# ロギングの設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#############################
# 処理
#############################
# botの準備完了時
@bot.event
async def on_ready():
    logging.info(f'event on_ready [{bot.user.name}]')
    await etc.on_ready()

# ユーザーのボイスチャンネル入退室
@bot.event
async def on_voice_state_update(member, before, after):
    logging.info('event on_voice_state_update')
    await etc.on_voice(member, before, after)
 
# ユーザーがメッセージを送信した時のイベント
@bot.event
async def on_message(message):
    logging.info('event on_message')
    await etc.on_message(message)
    await bot.process_commands(message)

# サーバー参加時にロール「レベル0」を付与
@bot.event
async def on_member_join(member):
    logging.info('event on_member_join')
    await level.set_level0(member)

# (hello)挨拶するコマンド
@bot.command()
async def hello(ctx):
    logging.info('command hello')
    await etc.hello(ctx)

# (play)ボイスチャンネルに参加してMP3ファイルを再生するコマンド
@bot.command()
async def play(ctx):
    logging.info('command play')
    await music.play(ctx)

# (stop)ボイスチャンネルを出てMP3ファイルを停止するコマンド
@bot.command()
async def stop(ctx):
    logging.info('command stop')
    await music.stop(ctx)

# (stats)現在のXPとレベルを表示するコマンド
@bot.command()
async def stats(ctx):
    logging.info('command stats')
    await level.stats(ctx)

# (ranking)XP取得ランキングを表示するコマンド
@bot.command()
async def ranking(ctx):
    logging.info('command ranking')
    await level.ranking(ctx)

# 実行
bot.run(BOT_TOKEN)
