import discord
from app.sub import db_operations as db


#############################
# 変数
#############################

#############################
# 処理
#############################
# botの準備完了時
async def on_ready(bot, bot_channel):
    # 初期化
    global BOT
    global BOT_CHANNEL
    BOT = bot
    BOT_CHANNEL = bot_channel


# 現在のXPとレベルを表示する
async def stats(ctx):
    user_id = ctx.author.id
    user_data = db.get_user_data(user_id)
    if user_data:
        xp = user_data['xp']
        level = user_data['level']
        next_level = level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10
        zan_xp = next_xp - xp
        await ctx.send(
            f'{ctx.author.display_name}さん\n現在のXPは{xp}、\nレベルは{level}です。\n次のレベルまであと{zan_xp}XPです。')
    else:
        await ctx.send(f'{ctx.author.display_name}さんはまだXPを獲得していません。')


# XP取得ランキングを表示する
async def ranking(ctx):
    # ユーザーXPによるソートデータの取得
    sorted_users = await db.get_users_sorted_by_xp()  # 非同期呼び出しに変更
    ranking_message = "ランキング:\n"
    for i, (user_id, data) in enumerate(sorted_users, start=1):
        try:
            user = await BOT.fetch_user(user_id)
            ranking_message += f'{i}. {user.display_name} - レベル: {data["level"]}, XP: {data["xp"]}\n'
        except Exception as e:
            ranking_message += f'{i}. ユーザー情報の取得に失敗しました。 - レベル: {data["level"]}, XP: {data["xp"]}\n'
    await ctx.send(ranking_message)


# レベルアップ処理
async def add_xp_and_check_level_up(user_id, xp_to_add):
    user_data = await db.get_user_data(user_id)
    if user_data is None:
        await db.insert_user_data(user_id, 0, 0)
        user_data = {'xp': 0, 'level': 0}  # ユーザーデータがNoneの場合に初期化
    user = await BOT.fetch_user(user_id)
    user_name = user.display_name
    # ユーザーにXPを付与
    user_data['xp'] += xp_to_add
    await db.update_user_data(user_id, user_data['xp'], user_data['level'])
    while True:
        # ユーザーのレベルをチェック
        user_data = await db.get_user_data(user_id)
        current_xp = user_data['xp']
        current_level = user_data['level']
        next_level = current_level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10
        if current_xp >= next_xp:
            user_data['level'] = next_level
            await db.update_user_data(user_id, current_xp, next_level)
            # ユーザーのレベルに応じたロールの付与と削除
            guild = BOT_CHANNEL.guild
            member = guild.get_member(user_id)
            next_level_name = f"レベル{next_level}"
            await add_roles(member, next_level_name)
            # レベルアップメッセージ
            await BOT_CHANNEL.send(f'{user_name}さん、レベル{next_level}にアップしました！')
        else:
            break


# レベル0」を付与
async def set_level0(member):
    next_level_name = "レベル0"
    await add_roles(member, next_level_name)


# ユーザーへロールを付与する
async def add_roles(member, next_level):
    # ユーザーのすべてのロールを削除
    await remove_all_roles(member)
    # 新しいレベルのロールを付与
    role_next_level = await get_roles(next_level)
    await member.add_roles(role_next_level)


# ロールを取得する
async def get_roles(next_level):
    guild = BOT_CHANNEL.guild
    admin_permissions = discord.Permissions(administrator=True)
    role_next_level = discord.utils.get(guild.roles, name=next_level)
    # なければ新規作成
    if not role_next_level:
        role_next_level = await guild.create_role(name=next_level, permissions=admin_permissions,
                                                  reason=f"{next_level}ロールが存在しないため作成しました。")
    # 返却
    return role_next_level


# ユーザーのすべてのロールを削除する
async def remove_all_roles(member):
    if member is not None and hasattr(member, 'roles') and len(member.roles) > 1:
        roles = member.roles[1:]  # member.roles[0]は@everyoneロールなのでスキップ
        if roles:
            await member.remove_roles(*roles)
