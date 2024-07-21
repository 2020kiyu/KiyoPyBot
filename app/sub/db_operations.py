# db_operations.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

#環境変数の読み込み
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# DBの設定
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 全データ取得
def get_all_users():
    response = supabase.table('USER_DATA').select('*').execute()
    users = response.data  # データをusers変数に格納
    # id をキーにして XP と LEVEL を持つ辞書を作成
    user_dict = {}
    for user in users:
        user_dict[user['id']] = {'xp': user['xp'], 'level': user['level']}
    # 辞書形式でデータを返却
    return user_dict

# 取得
def get_user_data(user_id):
    response = supabase.table('USER_DATA').select('*').eq('id', user_id).execute()
    return response.data

# 更新
def update_user_data(user_id, xp, level):
    response = supabase.table('USER_DATA').update({'xp': xp, 'level': level}).eq('id', user_id).execute()
    return response.data

# 挿入
def insert_user_data(user_id, xp, level):
    response = supabase.table('USER_DATA').insert({'id': user_id, 'xp': xp, 'level': level}).execute()
    return response.data

# ランキング取得
def get_users_sorted_by_xp():
    response = supabase.table('USER_DATA').select('*').order('xp', desc=True).execute()
    return response.data