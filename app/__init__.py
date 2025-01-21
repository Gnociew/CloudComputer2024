from flask import Flask,jsonify
from flask_cors import CORS
from app.routes.main import main_bp
from app.routes.generate import generate_bp
from app.routes.recommend import recommend_bp
from app.routes.shuwa import shuwa_bp
from app.routes.qa import qa_bp
from app.config import Config

def create_app(config_class=Config):
    """
    Flask 应用工厂函数
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 加载配置
    # app.config.from_object(Config)
    
    # 启用跨域支持
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(shuwa_bp, url_prefix='/api/shuwa')
    app.register_blueprint(generate_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(qa_bp)

    # 注册错误处理器
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
        
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not found"}), 404

    
    return app
