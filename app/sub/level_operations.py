# level_operations.py

import discord
from app.sub import db_operations as db

#############################
# 変数
#############################


#############################
# 処理
#############################
# レベル0」を付与
async def set_level0(member):
    next_level_name = "レベル0"
    await add_roles(member, next_level_name)

# 現在のXPとレベルを表示する
async def stats(ctx):
    user_id = ctx.author.id
    if user_id in USER_DICT:
        xp = USER_DICT[user_id]['xp']
        level = USER_DICT[user_id]['level']
        next_level = level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10
        zan_xp = next_xp - xp
        await ctx.send(f'{ctx.author.display_name}さん\n現在のXPは{xp}、\nレベルは{level}です。\n次のレベルまであと{zan_xp}XPです。')
    else:
        await ctx.send(f'{ctx.author.display_name}さんはまだXPを獲得していません。')

# XP取得ランキングを表示する
async def ranking(ctx):
    sorted_users = sorted(USER_DICT.items(), key=lambda x: x[1]['xp'], reverse=True)
    ranking_message = "ランキング:\n"
    for i, (user_id, data) in enumerate(sorted_users, start=1):
        user = await bot.fetch_user(user_id)
        ranking_message += f'{i}. {user.display_name} - レベル: {data["level"]}, XP: {data["xp"]}\n'
    await ctx.send(ranking_message)

# レベルアップ処理
async def add_xp_and_check_level_up(bot, BOT_CHANNEL, USER_DICT, user_id, xp_to_add):
    if user_id not in USER_DICT:
        USER_DICT[user_id] = {'xp': 0, 'level': 0}
    user = await bot.fetch_user(user_id)
    user_name = user.display_name
    # ユーザーにXPを付与
    USER_DICT[user_id]['xp'] += xp_to_add
    while True:
         # ユーザーのレベルをチェック
        current_xp = USER_DICT[user_id]['xp']
        current_level = USER_DICT[user_id]['level']
        next_level = current_level + 1
        next_xp = next_level * (next_level + 1) // 2 * 10
        if current_xp >= next_xp:
            # レベルアップ処理
            USER_DICT[user_id]['level'] = next_level
            await BOT_CHANNEL.send(f'{user_name}さん、レベル{next_level}にアップしました！')
            # ユーザーのレベルに応じたロールの付与と削除
            guild = BOT_CHANNEL.guild
            member = guild.get_member(user_id)
            next_level_name = f"レベル{next_level}"
            await add_roles(member, next_level_name)
            await db.update_user_data(user_id, USER_DICT[user_id]['xp'], USER_DICT[user_id]['level'])
        else:
            break

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

# ユーザーへロールを付与する
async def add_roles(member, next_level):
    # ユーザーのすべてのロールを削除
    await remove_all_roles(member)
    # 新しいレベルのロールを付与
    role_next_level = await get_roles(next_level)
    await member.add_roles(role_next_level)

# ユーザーのすべてのロールを削除する
async def remove_all_roles(member):
    if member.roles is None and member.roles.length > 1:
        roles = member.roles[1:]  # member.roles[0]は@everyoneロールなのでスキップ
        if roles:
            await member.remove_roles(*roles)

