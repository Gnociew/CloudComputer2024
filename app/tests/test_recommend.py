import os
import sqlite3

user_id="user1"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATABASE_PATH = os.path.join(BASE_DIR, "app", "database", "recommendations.db")
print("Database Path:", DATABASE_PATH)
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
cursor.execute('SELECT recent_words FROM user_recent_words WHERE user_id = ?', (user_id,))
row = cursor.fetchone()
conn.close()
recent_words = eval(row[0])  # 转换为 Python 列表
print(recent_words)