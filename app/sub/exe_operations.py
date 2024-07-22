# exe_operations.py

import os
from dotenv import load_dotenv
from datetime import datetime
from app.sub import level_operations as level
from app.sub import music_operations as music
from app.sub import db_operations as db

#############################
# 変数
#############################
# 環境変数の読み込み
load_dotenv()
BOT_CHANNEL_ID = int(os.getenv('BOT_CHANNEL'))
BOT_CHANNEL2_ID = int(os.getenv('BOT_CHANNEL2'))

# ボイスチャンネル滞在
VOICE_CHANNEL_TIMES = {}


#############################
# 処理
#############################
# botの準備完了時
async def on_ready(bot):
    # 初期化
    global BOT
    global BOT_CHANNEL
    global BOT_CHANNEL2
    BOT = bot
    BOT_CHANNEL = bot.get_channel(BOT_CHANNEL_ID)
    BOT_CHANNEL2 = bot.get_channel(BOT_CHANNEL2_ID)
    # ユーザーデータに基づいてロールを付け替え
    for channel in [BOT_CHANNEL, BOT_CHANNEL2]:
        guild = channel.guild
        users = await db.get_all_users(guild.id)
        # ロール「レベル0」を準備
        await level.get_roles(guild, "レベル0")
        for (user_id, data) in users:
            member = guild.get_member(int(user_id))
            next_level_name = f"レベル{data['level']}"
            await level.add_roles(member, next_level_name)


# チャンネルを取得する
async def get_bot_channel(guild):
    if guild == BOT_CHANNEL.guild:
        return BOT_CHANNEL
    else:
        return BOT_CHANNEL2


# ユーザーのボイスチャンネル入退室
async def on_voice(member, before, after):
    if member.bot:
        return  # ボット自身の入退室は無視
    # channel取得
    channel = await get_bot_channel(member.guild)
    if before.channel is None and after.channel is not None:
        # ユーザーがボイスチャンネルに参加した場合
        VOICE_CHANNEL_TIMES[member.id] = datetime.now()
        await channel.send(f'{member.display_name}さんが {after.channel.name} に参加します！')
    elif before.channel is not None and after.channel is None:
        # ユーザーがボイスチャンネルから退出した場合
        join_time = VOICE_CHANNEL_TIMES.pop(member.id, None)
        if join_time:
            # レベルアップ処理を呼び出す
            stay_duration = datetime.now() - join_time
            minutes = int(stay_duration.total_seconds() // 60)
            await channel.send(f'{member.display_name}さん、ボイスチャンネルに{minutes}分間滞在しました。')
            await level.add_xp_and_check_level_up(member, minutes * 2)


# ユーザーがメッセージを送信した時
async def on_message(message):
    if message.author.bot:
        return  # ボット自身のメッセージは無視
    member = message.author
    xp_to_add = 10
    # レベルアップ処理を呼び出す
    await level.add_xp_and_check_level_up(member, xp_to_add)


# レベル0セット
async def set_level0(member):
    await level.set_level0(member)


# 挨拶
async def hello(ctx):
    user_name = ctx.author.display_name  # 発言したユーザー名
    await ctx.send(f'{user_name}さん こんちゃす☆彡')


# ステータス確認
async def stats(ctx):
    await level.stats(ctx)


# ランキング確認
async def ranking(ctx):
    await level.ranking(ctx)


# 音楽再生
async def play(ctx):
    await music.play(ctx)


# 音楽停止
async def stop(ctx):
    await music.stop(ctx)
