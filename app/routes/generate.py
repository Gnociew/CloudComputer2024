from flask import Blueprint, request, jsonify
from app.services.ark_client import client

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate_sentence', methods=['POST'])
def generate_sentence():
    data = request.json
    gloss_words = data['gloss_words']
    gloss_content = " ".join(gloss_words)

    # 创建系统消息和用户消息
    system_message = {"role": "system", "content": "你是一个语言生成助手，根据提供的 gloss 词生成中文句子。"}
    user_message = {"role": "user", "content": f"请根据以下 gloss 词生成中文句子：{gloss_content}"}

    # 调用模型生成句子
    completion = client.chat.completions.create(
        model="ep-20250102153719-nsvdq",
        messages=[system_message, user_message],
        extra_headers={'x-is-encrypted': 'true'}
    )

    # 返回生成的句子
    return jsonify({'sentence': completion.choices[0].message.content})
