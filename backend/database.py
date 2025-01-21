# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 这里使用相对路径或绝对路径都可以
# 例如放在 backend 同级目录下的 db.sqlite 文件中
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite')

# 创建数据库引擎（SQLite）
engine = create_engine(f"sqlite:///{DB_FILE_PATH}", echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
