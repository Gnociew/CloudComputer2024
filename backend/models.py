# models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from database import engine

Base = declarative_base()

class QuestionRecord(Base):
    """
    存储每道题目的信息 + LangChain 生成的解题提示
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)  # 学生输入的题目
    hint_text = Column(Text, nullable=True)       # 生成的解题提示

class AnswerRecord(Base):
    """
    存储学生提交的答案及验证结果
    """
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, nullable=False)  # 外键指向 QuestionRecord
    student_answer = Column(Text, nullable=False)  # 学生提交的答案
    verification_result = Column(Text, nullable=True)  # 系统判定的结果
