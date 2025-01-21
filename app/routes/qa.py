import sqlite3
from flask import Blueprint, request, jsonify
from app.services.rag_service import answer_question
from app.config import Config

qa_bp = Blueprint("qa", __name__)

import os

# 获取当前文件所在的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 生成数据库路径并标准化
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../data/media_store.db"))



def get_file_from_db(keyword):
    print(f"Database path: {DB_PATH}")
    """
    根据关键词从 SQLite 数据库中查询 file 列的数据。
    如果找到对应的文件，返回二进制数据；否则返回 None。
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file FROM media_store WHERE keyword = ?", (keyword,))
            result = cursor.fetchone()
            if result:
                return result[0]  # 返回文件的二进制数据
            else:
                return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

@qa_bp.route("/qa", methods=["POST"])  
def ask_question():
    print("arrive ask_question")
    """
    接收用户问题并返回答案
    """
    data = request.get_json()
    keyword = data.get("keyword", "")
    print(f"Received question: {keyword}")
    
    if not keyword:
        return jsonify({"error": "Question is required"}), 400
    else:
        question = f"如何用手语表示{keyword}"
    
    try:
        # 调用回答函数
        answer = answer_question(question, Config.VECTOR_DB_PATH)
        file_data = get_file_from_db(keyword)

        if answer:
            response = {"answer": answer}
            if file_data:
                # 如果有 .webm 文件，添加到返回结果中
                response["webm_file"] = file_data.hex()  # 将二进制数据转换为十六进制字符串
            return jsonify(response)
        else:
            return jsonify({"answer": "未能生成回答"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500