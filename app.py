import eventlet
eventlet.monkey_patch()  # 确保这一行在其他导入之前
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import login_required, current_user
from config import Config
from models import db, login_manager
from models.user import User
from api.auth import auth_bp
from api.chat import chat_bp
import logging
from logging.handlers import RotatingFileHandler
import os
import base64
import time

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    # 日志目录
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志文件路径
    log_file = os.path.join(log_dir, 'app_log.txt')

    # 配置日志处理器
    handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(pathname)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        format='[%(asctime)s] [%(levelname)s] %(pathname)s:%(lineno)d - %(message)s'
    )

    logging.info("日志系统初始化完成")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 路由
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/chat')
    @login_required
    def chat():
        return render_template('chat.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/api/upload_screenshot', methods=['POST'])
    def upload_screenshot():
        data = request.get_json()
        img_base64 = data.get('image')
        if not img_base64:
            return jsonify({'success': False, 'msg': 'No image data'}), 400
        try:
            img_bytes = base64.b64decode(img_base64)
            filename = f"screenshot_{int(time.time())}.png"
            save_dir = os.path.join(os.path.dirname(__file__), 'logs', 'screenshots')
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            file_path = os.path.join(save_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
            logging.info(f"收到前端上传的截图，已保存为 {file_path}")
            return jsonify({'success': True, 'msg': 'Screenshot saved'})
        except Exception as e:
            logging.error(f"保存截图失败: {str(e)}")
            return jsonify({'success': False, 'msg': 'Save failed'}), 500

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '页面未找到'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': '服务器内部错误'}), 500

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app

# 创建应用和SocketIO实例
app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

# WebSocket事件处理
@socketio.on('connect')
@login_required
def handle_connect():
    join_room(f'user_{current_user.id}')
    emit('status', {'msg': f'{current_user.username} 已连接'})

@socketio.on('disconnect')
@login_required
def handle_disconnect():
    leave_room(f'user_{current_user.id}')

@socketio.on('join_chat')
@login_required
def handle_join_chat(data):
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('status', {'msg': f'已加入聊天室 {session_id}'})

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


