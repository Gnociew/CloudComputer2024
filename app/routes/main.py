from flask import Blueprint, render_template, jsonify, request

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/search_sign', methods=['POST'])
def search_sign():
    data = request.get_json()
    query = data.get('query')
    
    try:
        # 这里添加您的后端逻辑，从数据库或其他来源获取视频信息
        # 示例返回数据
        result = {
            'video_url': f'/static/videos/{query}.mp4',  # 视频URL
            'description': f'这是"{query}"的手语示范视频。手语动作描述：[具体描述]',  # 视频描述
            'success': True
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
