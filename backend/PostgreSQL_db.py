# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库连接信息
DB_HOST = "pgm-bp1ydqzg4937odnzxo.pg.rds.aliyuncs.com"  # 阿里云 RDS 的公网地址
DB_PORT = "5432"  # PostgreSQL 默认端口
DB_USER = "gimpyo"  # RDS 数据库用户名
DB_PASSWORD = "Jinbiao0416"  # RDS 数据库密码
DB_NAME = "langchain"  # RDS 中的数据库名

# 创建 PostgreSQL 数据库引擎
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
