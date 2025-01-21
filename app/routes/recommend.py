from flask import Blueprint, request, jsonify
from app.services.langchain_service import generate_recommendations
import sqlite3
import os

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend', methods=['POST'])
def recommend():
    """
    接收用户最近学习的手语词语，返回推荐内容。
    """

    # 从前端获取用户id
    # data = request.get_json()
    # user_id = data.get("user_id")
    #
    # if not user_id:
    #     return jsonify({"error": "User ID is required."}), 400

    user_id="user1"
    # 从数据库中查询用户的最近学习词语
    try:
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        DATABASE_PATH = os.path.join(BASE_DIR, "app", "database", "recommendations.db")
        print("Database Path:", DATABASE_PATH)
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT recent_words FROM user_recent_words WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    if not row:
        return jsonify({"error": "No recent words found for the given user ID."}), 404

    # 解析 JSON 数据
    recent_words = eval(row[0])  # 转换为 Python 列表

    # if not recent_words or len(recent_words) != 10:
    #     return jsonify({"error": "Please provide exactly 10 recently learned words."}), 400

    # 使用 LangChain 生成推荐内容
    result = generate_recommendations(recent_words)
    print(result)
    
    return jsonify({"recommendation_text": result})