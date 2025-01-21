import sqlite3
import psycopg2
from sqlalchemy import create_engine, MetaData, Table

# SQLite 数据库连接
sqlite_db = "db.sqlite"  # SQLite 数据库文件路径
sqlite_conn = sqlite3.connect(sqlite_db)
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL 数据库连接信息
pg_host = "pgm-bp1ydqzg4937odnzxo.pg.rds.aliyuncs.com"  # PostgreSQL RDS 实例的公网地址
pg_port = "5432"  # PostgreSQL 默认端口
pg_user = "gimpyo"  # PostgreSQL 用户名
pg_password = "Jinbiao0416"  # PostgreSQL 用户密码
pg_dbname = "langchain"  # PostgreSQL 数据库名称

# 创建 PostgreSQL 连接
pg_conn = psycopg2.connect(
    host=pg_host,
    port=pg_port,
    user=pg_user,
    password=pg_password,
    dbname=pg_dbname
)
pg_cursor = pg_conn.cursor()

# 创建 SQLAlchemy 引擎，连接到 PostgreSQL
engine = create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_dbname}")

# 获取 SQLite 中的所有表
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

# 迁移每个表的数据
for table in tables:
    table_name = table[0]

    # 获取 SQLite 表的列名和数据类型
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = sqlite_cursor.fetchall()

    # 创建 PostgreSQL 表（确保表结构相同）
    column_definitions = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]  # 这里根据需要做更复杂的类型映射
        column_definitions.append(f"{col_name} {col_type}")
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
    pg_cursor.execute(create_table_sql)

    # 获取 SQLite 表的数据
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    # 插入数据到 PostgreSQL 表
    if rows:
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({', '.join([col[1] for col in columns])}) VALUES ({placeholders})"
        pg_cursor.executemany(insert_sql, rows)

# 提交更改并关闭连接
pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print("Data migration completed successfully.")
