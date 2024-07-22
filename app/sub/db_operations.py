# db_operations.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

#############################
# 変数
#############################
# 環境変数の読み込み
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# DBの設定
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


#############################
# 処理
#############################
# 全データ取得
def get_all_users():
    response = supabase.table('USER_DATA').select('*').execute()
    users = response.data  # データをusers変数に格納
    # id をキーにして XP と LEVEL を持つ辞書を作成
    user_dict = {}
    for user in users:
        user_dict[int(user['id'])] = {'xp': user['xp'], 'level': user['level']}
    # 辞書形式でデータを返却
    return user_dict


# 取得
def get_user_data(user_id):
    user_id = str(user_id)
    response = supabase.table('USER_DATA').select('*').eq('id', user_id).execute()
    user_list = response.data  # データをuser_list変数に格納
    if not user_list:
        return None  # ユーザーが存在しない場合
    user = user_list[0]  # リストの最初の要素を取得
    # id をキーにして XP と LEVEL を持つ辞書を作成
    user_data = {'xp': user['xp'], 'level': user['level']}
    return user_data


# 更新
def update_user_data(user_id, xp, level):
    user_id = str(user_id)
    xp = int(float(xp))
    level = int(float(level))
    response = supabase.table('USER_DATA').update({'xp': xp, 'level': level}).eq('id', user_id).execute()
    return response.data


# 挿入
def insert_user_data(user_id, xp, level):
    user_id = str(user_id)
    xp = int(float(xp))
    level = int(float(level))
    response = supabase.table('USER_DATA').insert({'id': user_id, 'xp': xp, 'level': level}).execute()
    return response.data


# ランキング取得
def get_users_sorted_by_xp():
    response = supabase.table('USER_DATA').select('*').order('xp', desc=True).execute()
    sorted_users = response.data  # データをusers変数に格納
    # タプルのリストに変換
    return [(int(user['id']), {'xp': user['xp'], 'level': user['level']}) for user in sorted_users]
