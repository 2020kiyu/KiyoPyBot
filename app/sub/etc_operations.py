# etc_operations.py

import os
from dotenv import load_dotenv
from app.sub import level_operations as level
from app.sub import db_operations as db

#############################
# 変数
#############################
#環境変数の読み込み
load_dotenv()
BOT_CHANNEL = int(os.getenv('BOT_CHANNEL'))

#ボイスチャンネル滞在
VOICE_CHANNEL_TIMES = {}


#############################
# 処理
#############################
# botの準備完了時
async def on_ready(bot):
    # BOTチャンネル
    global BOT_CHANNEL
    BOT_CHANNEL = bot.get_channel(BOT_CHANNEL)
    # ユーザーデータをロード
    global USER_DICT
    USER_DICT = db.get_all_users()
    # ロール「レベル0」を準備
    await level.get_roles("レベル0")
    # ユーザーデータに基づいてロールを付け替え
    guild = BOT_CHANNEL.guild
    for user_id, data in USER_DICT.items():
        member = guild.get_member(int(user_id))
        if member:
            next_level_name = f"レベル{data['level']}"
            await level.add_roles(member, next_level_name)
    # メッセージ
    await BOT_CHANNEL.send(f'{member.display_name}さんがサーバーに参加しました。レベル0のロールを付与しました。')

# ユーザーのボイスチャンネル入退室
async def on_voice(member, before, after):
   if member.bot:
       return  # ボット自身の入退室は無視
   if before.channel is None and after.channel is not None:
       # ユーザーがボイスチャンネルに参加した場合
       VOICE_CHANNEL_TIMES[member.id] = datetime.now()
       await BOT_CHANNEL.send(f'{member.display_name}さんが {after.channel.name} に参加します！')
   elif before.channel is not None and after.channel is None:
       # ユーザーがボイスチャンネルから退出した場合
       join_time = VOICE_CHANNEL_TIMES.pop(member.id, None)
       if join_time:
           await BOT_CHANNEL.send(f'{member.display_name}さん、ボイスチャンネルに{minutes:.2f}分間滞在しました。')
           # レベルアップ処理を呼び出す
           stay_duration = datetime.now() - join_time
           minutes = int(stay_duration.total_seconds() / 60)
           await add_xp_and_check_level_up(member.id, minutes * 2)

# ユーザーがメッセージを送信した時
async def on_message(message):
    if message.author.bot:
        return  # ボット自身のメッセージは無視
    user_id = message.author.id
    xp_to_add = 10
    # レベルアップ処理を呼び出す
    await level.add_xp_and_check_level_up(user_id, xp_to_add)

# 挨拶
async def hello(ctx):
    user_name = ctx.author.display_name  # 発言したユーザー名
    await ctx.send(f'{user_name}さん こんちゃす☆彡')
