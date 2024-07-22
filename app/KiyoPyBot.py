"""
Discord Bot Script
KiyoPyBot
 
・ユーザーのレベル管理を行う。
・ボイスチャンネルで音楽を流す。

Author      : Yushi Kiyota
Created     : 2024-07-18
Last Updated: 2024-07-21
 
Commands:
- /hello  : 挨拶コマンド.
- /play   : 音楽再生コマンド.
- /stop   ; 音楽停止コマンド
- /stats  : ユーザーのレベル表示コマンド.
- /ranking: ランキング表示コマンド.
 
仕様:
- サーバー参加時に自動で"レベル0"ロールが割り当てられます.
- botはユーザのレベルと経験値(XP)を管理しています。
- 発言1回につき10XPもらえます。
- 音声サーバーに1分滞在するごとに2XPもらえます。
"""
import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from app.sub import exe_operations as exe
from flask import Flask
from threading import Thread
import asyncio

#############################
# 変数
#############################
# 環境変数の読み込み
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

# Flask アプリの設定
app = Flask(__name__)


#############################
# 処理
#############################
# botの準備完了時
@bot.event
async def on_ready():
    logging.info(f'event on_ready [{bot.user.name}]')
    await exe.on_ready(bot)


# ユーザーのボイスチャンネル入退室
@bot.event
async def on_voice_state_update(member, before, after):
    logging.info('event on_voice_state_update')
    await exe.on_voice(member, before, after)


# ユーザーがメッセージを送信した時のイベント
@bot.event
async def on_message(message):
    logging.info('event on_message')
    await exe.on_message(message)
    await bot.process_commands(message)


# サーバー参加時にロール「レベル0」を付与
@bot.event
async def on_member_join(member):
    logging.info('event on_member_join')
    await exe.set_level0(member)


# (hello)挨拶するコマンド
@bot.command()
async def hello(ctx):
    logging.info('command hello')
    await exe.hello(ctx)


# (play)ボイスチャンネルに参加してMP3ファイルを再生するコマンド
@bot.command()
async def play(ctx):
    logging.info('command play')
    await exe.play(ctx)


# (stop)ボイスチャンネルを出てMP3ファイルを停止するコマンド
@bot.command()
async def stop(ctx):
    logging.info('command stop')
    await exe.stop(ctx)


# (stats)現在のXPとレベルを表示するコマンド
@bot.command()
async def stats(ctx):
    logging.info('command stats')
    await exe.stats(ctx)


# (ranking)XP取得ランキングを表示するコマンド
@bot.command()
async def ranking(ctx):
    logging.info('command ranking')
    await exe.ranking(ctx)


# Flask アプリをバックグラウンドで実行するための関数
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))


# メイン関数
async def main():
    # Flask アプリをバックグラウンドで実行
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Discord ボットを実行
    await bot.start(os.getenv('BOT_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
