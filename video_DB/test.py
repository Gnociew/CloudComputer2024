import sqlite3

# 数据库文件
db_path = "../data/media_store.db"

# 插入数据的函数
def insert_webm_file(keyword, file_path):
    # 读取 .webm 文件为二进制数据
    with open(file_path, "rb") as file:
        file_data = file.read()
    
    # 插入到 SQLite 数据库
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO media_store (keyword, file) VALUES (?, ?)",
            (keyword, file_data)
        )
        conn.commit()
        print(f"Inserted: {keyword} -> {file_path}")

# 示例调用
insert_webm_file("谢谢", "thanks.webm")
