from flask import Blueprint, jsonify, request, Response
from app.services.pipeline_service import PipelineService

shuwa_bp = Blueprint('shuwa', __name__)
pipeline_service = PipelineService()

@shuwa_bp.route('/record', methods=['POST'])
def record():
    try:
        return pipeline_service.handle_recording()
    except Exception as e:
        print(f"Record route error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@shuwa_bp.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        gloss_name = data.get('name')
        if not gloss_name:
            return jsonify({"error": "No name provided"}), 400
        return pipeline_service.save_recording(gloss_name)
    except Exception as e:
        print(f"Save route error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@shuwa_bp.route('/translate', methods=['POST'])
def translate():
    try:
        return pipeline_service.translate_recording()
    except Exception as e:
        print(f"Translate route error: {str(e)}")
        return jsonify({"error": str(e)}), 500 

@shuwa_bp.route('/video_feed')
def video_feed():
    return Response(pipeline_service.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')