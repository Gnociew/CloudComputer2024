import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# LangChain 相关
from langchain_community.chat_models import ChatZhipuAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 数据库相关
from database import SessionLocal, engine
from models import Base, QuestionRecord, AnswerRecord

load_dotenv()
app = Flask(__name__)

# 若表尚未创建，在这里执行表创建
Base.metadata.create_all(bind=engine)

# 初始化大模型 (智谱 API)
zhipu_api_key = os.getenv("ZHIPU_API_KEY", "")  # 从环境变量获取 API Key
llm = ChatZhipuAI(
    model="glm-4",  # 选择智谱模型，如 chatglm_pro
    temperature=0.3,      # 控制生成文本的随机性
    api_key=zhipu_api_key # 智谱 API 密钥
)
# --------------【1】解题提示生成 Chain --------------
prompt_template_for_hint = """
你是一名经验丰富的中学数学老师，善于给学生提供分步解题提示。
学生的问题是：{question}
请给出简明的解题步骤提示，不直接给出最终答案。
如果问题不符合中学数学水平或无意义，请说明。
"""
hint_prompt = PromptTemplate(
    template=prompt_template_for_hint,
    input_variables=["question"]
)
hint_chain = LLMChain(llm=llm, prompt=hint_prompt)

# --------------【2】答案验证 Chain --------------
prompt_template_for_verification = """
你是一名经验丰富的中学数学老师，善于批改学生作业。
给定的题目是：{question}
学生给出的答案是：{answer}
请判断该答案是否正确，如不正确，请给出一个简要的反馈或提示。
只需要输出“正确”或“错误：原因”。
"""
verify_prompt = PromptTemplate(
    template=prompt_template_for_verification,
    input_variables=["question", "answer"]
)
verify_chain = LLMChain(llm=llm, prompt=verify_prompt)

from sympy import sympify, Symbol, solve
import re
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64


@app.route("/api/plot_equation", methods=["POST"])
def plot_equation():
    data = request.get_json()
    equation = data.get("equation", "").strip()
    if not equation:
        return jsonify({"error": "No equation provided"}), 400

    # 预处理方程，将 '2x' 转换为 '2*x'
    equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)

    # 分割方程为两个函数
    try:
        left_expr, right_expr = map(sympify, equation.split('='))
    except Exception as e:
        return jsonify({"error": f"Invalid equation: {str(e)}"}), 400

    x = Symbol('x')
    x_vals = np.linspace(-10, 10, 400)
    y_left = [left_expr.subs(x, val) for val in x_vals]
    y_right = [right_expr.subs(x, val) for val in x_vals]

    # 求交点
    intersection = solve(left_expr - right_expr, x)
    intersection_y = [left_expr.subs(x, val) for val in intersection]

    plt.figure()
    plt.plot(x_vals, y_left, label='Left Function')
    plt.plot(x_vals, y_right, label='Right Function')
    plt.scatter(intersection, intersection_y, color='red', zorder=5, label='Intersection')
    plt.title(f"Graph of {equation}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()

    # 将图像保存到内存中
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return jsonify({"image": image_base64}), 200

import time

@app.route("/api/generate_hint", methods=["POST"])
def generate_hint():
    data = request.get_json()
    question_text = data.get("question", "").strip()
    if not question_text:
        return jsonify({"error": "No question provided"}), 400

    # 1. 调LangChain获取解题提示
    hint_result = hint_chain.run(question=question_text)

    # 在这里加上延时，避免触发 API 的请求频率限制
    time.sleep(1)  # 这里的 1 秒可以根据需求调整

    # 2. 写入数据库
    db = SessionLocal()
    try:
        # 新建一条 QuestionRecord
        new_question = QuestionRecord(
            question_text=question_text,
            hint_text=hint_result.strip()
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        question_id = new_question.id  # 获取新插入的ID
    finally:
        db.close()

    return jsonify({
        "question": question_text,
        "hint": hint_result.strip(),
        "question_id": question_id
    }), 200



@app.route("/api/verify_answer", methods=["POST"])
def verify_answer():
    data = request.get_json()
    question_text = data.get("question", "").strip()
    student_answer = data.get("answer", "").strip()

    if not question_text or not student_answer:
        return jsonify({"error": "question or answer missing"}), 400

    # 1. 调LangChain进行答案验证
    verification_result = verify_chain.run(
        question=question_text,
        answer=student_answer
    ).strip()

    # 在这里加上延时，避免触发 API 的请求频率限制
    time.sleep(1)  # 这里的 1 秒可以根据需求调整

    # 2. 查找对应 question_id（简单做法：根据 question_text 匹配最新一条）
    db = SessionLocal()
    try:
        # 先根据题目文本找到一个 QuestionRecord（此处简化为直接取最新）
        question_record = db.query(QuestionRecord)\
                            .filter(QuestionRecord.question_text == question_text)\
                            .order_by(QuestionRecord.id.desc())\
                            .first()

        question_id = question_record.id if question_record else None

        # 创建 AnswerRecord
        new_answer = AnswerRecord(
            question_id=question_id if question_id else 0,
            student_answer=student_answer,
            verification_result=verification_result
        )
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
    finally:
        db.close()

    return jsonify({
        "question": question_text,
        "student_answer": student_answer,
        "verification": verification_result
    }), 200



@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
