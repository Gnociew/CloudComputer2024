import sqlite3

# 初始化数据库
def init_db():
    conn = sqlite3.connect('recommendations.db')
    cursor = conn.cursor()
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_recent_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            recent_words TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def insert_test_data():
    conn = sqlite3.connect('recommendations.db')
    cursor = conn.cursor()

    # 定义多条测试数据
    test_data = [
        ('user1', '["你好", "谢谢", "对不起", "我爱你", "再见", "请", "帮忙", "喝水", "吃饭", "休息"]'),
        ('user2', '["早上好", "晚上好", "饿", "渴", "累", "睡觉", "工作", "学习", "朋友", "开心"]'),
        ('user3', '["家", "学校", "老师", "同学", "书", "学习", "电脑", "手机", "黑板", "桌子"]'),
        ('user4', '["北京", "上海", "广州", "深圳", "成都", "杭州", "重庆", "西安", "武汉", "南京"]'),
        ('user5', '["篮球", "足球", "乒乓球", "游泳", "跑步", "跳绳", "羽毛球", "健身", "瑜伽", "太极"]')
    ]

    # 批量插入数据
    cursor.executemany('''
        INSERT OR REPLACE INTO user_recent_words (user_id, recent_words)
        VALUES (?, ?)
    ''', test_data)

    conn.commit()
    conn.close()

# 初始化和插入数据
init_db()
insert_test_data()
