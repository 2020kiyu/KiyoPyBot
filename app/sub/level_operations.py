# level_operations.py

import discord
from app.sub import db_operations as db

#############################
# 変数
#############################

#############################
# 処理
#############################
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
        await ctx.send(f'{ctx.author.display_name}さん\n現在のXPは{xp}、\nレベルは{level}です。\n次のレベルまであと{zan_xp}XPです。')
    else:
        await ctx.send(f'{ctx.author.display_name}さんはまだXPを獲得していません。')

# XP取得ランキングを表示する
async def ranking(BOT, ctx):
    sorted_users = db.get_users_sorted_by_xp()
    ranking_message = "ランキング:\n"
    for i, (user_id, data) in enumerate(sorted_users, start=1):
        user = await BOT.fetch_user(user_id)
        ranking_message += f'{i}. {user.display_name} - レベル: {data["level"]}, XP: {data["xp"]}\n'
    await ctx.send(ranking_message)

# レベルアップ処理
async def add_xp_and_check_level_up(bot, BOT_CHANNEL, user_id, xp_to_add):
    user_data = db.get_user_data(user_id)
    if user_data is None:
        db.insert_user_data(user_id, 0, 0)
    user = await bot.fetch_user(user_id)
    user_name = user.display_name
    # ユーザーにXPを付与
    user_data['xp'] += xp_to_add
    db.update_user_data(user_id, user_data['xp'], user_data['level'])
    while True:
        # ユーザーのレベルをチェック
        user_data = db.get_user_data(user_id)
        current_xp = user_data['xp']
        current_level = user_data['level']
        next_level = current_level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10
        if current_xp >= next_xp:
            # ユーザーのレベルに応じたロールの付与と削除
            guild = BOT_CHANNEL.guild
            member = guild.get_member(user_id)
            next_level_name = f"レベル{next_level}"
            await add_roles(BOT_CHANNEL, member, next_level_name)
            db.update_user_data(user_id, user_data['xp'], user_data['level'])
            # レベルアップメッセージ
            await BOT_CHANNEL.send(f'{user_name}さん、レベル{next_level}にアップしました！')
        else:
            break

# レベル0」を付与
async def set_level0(BOT_CHANNEL, member):
    next_level_name = "レベル0"
    await add_roles(BOT_CHANNEL, member, next_level_name)

# ユーザーへロールを付与する
async def add_roles(BOT_CHANNEL, member, next_level):
    # ユーザーのすべてのロールを削除
    await remove_all_roles(member)
    # 新しいレベルのロールを付与
    role_next_level = await get_roles(BOT_CHANNEL, next_level)
    await member.add_roles(role_next_level)

# ロールを取得する
async def get_roles(BOT_CHANNEL, next_level):
    guild = BOT_CHANNEL.guild
    admin_permissions = discord.Permissions(administrator=True)
    role_next_level = discord.utils.get(guild.roles, name=next_level)
    # なければ新規作成
    if not role_next_level:
       role_next_level = await guild.create_role(name=next_level, permissions=admin_permissions, reason=f"{next_level}ロールが存在しないため作成しました。")
    # 返却
    return role_next_level

# ユーザーのすべてのロールを削除する
async def remove_all_roles(member):
    if member is not None and member.roles is not None and member.roles.length > 1:
        roles = member.roles[1:]  # member.roles[0]は@everyoneロールなのでスキップ
        if roles:
            await member.remove_roles(*roles)

