"""
wwd:
认证相关API（登录、注册、权限验证等）
定义了一个 Flask 蓝图，用于处理用户认证相关的 API，例如注册、登录、登出和获取用户信息。
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
import re
# 创建蓝图，指定名称和模块名,创建一个名为 auth 的蓝图，后续会将相关的路由注册到这个蓝图中。
auth_bp = Blueprint('auth', __name__)
"""
@auth_bp.route('/register', methods=['POST'])：定义一个路由，处理 /register 地址的 POST 请求，调用 register 函数。
这是蓝图（Blueprint）的路由装饰器，用于在蓝图中注册路由。
'POST'支持多种HTTP方法的路由,用于处理客户端以 POST 方法发送到 /login 路径的请求。
HTTP 方法中，POST 常用于提交数据（如表单提交、发送用户名 / 密码等敏感信息），而 GET 用于获取数据。
注册 / 登录场景必须用 POST，因为需要提交用户输入的账号、密码等数据，且 POST 比 GET 更安全（数据在请求体中，不在 URL 中暴露）。
"""
@auth_bp.route('/register', methods=['POST'])
def register():
    #获取请求的 JSON 数据，解析为 Python 字典。
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    # 验证数据,检查是否所有字段都有值。如果有任一字段缺失，返回 400 状态码和错误信息。
    if not all([username, email, password]):
        return jsonify({'error': '所有字段都是必需的'}), 400
    #检查密码长度是否至少为 6 位，如果不足，返回 400 状态码和错误信息。
    if len(password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    #使用正则表达式检查邮箱格式是否正确，如果不符合，返回 400 状态码和错误信息
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    #查询数据库，检查是否有相同的用户名。如果存在，返回 400 状态码和错误信息。
    #使用了 SQLAlchemy 的 Query API 进行数据库查询
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400
    #创建一个新的 User 实例，使用提供的用户名和邮箱。
    user = User(username=username, email=email)
    #调用 set_password 方法，将密码进行哈希处理并存储。
    user.set_password(password)
    db.session.add(user)
    db.session.commit()#将新用户添加到数据库会话中，并提交更改以保存到数据库。
    #使用 login_user 函数登录新用户，创建用户会话
    login_user(user)
    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201
#用户登录 API

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': '用户名和密码都是必需的'}), 400

    user = User.query.filter_by(username=username).first()
    #如果用户存在且密码验证通过，调用 login_user 函数登录用户。
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'message': '登录成功', 'user': user.to_dict()}), 200
        #返回成功消息和用户信息，状态码为 200（成功）
    else:
        return jsonify({'error': '用户名或密码错误'}), 401
#用户登出 API
@auth_bp.route('/logout', methods=['POST'])
@login_required
#定义一个路由，处理 /logout 地址的 POST 请求，调用 logout 函数，并使用 @login_required 装饰器保护该路由，确保用户已登录。
def logout():
    logout_user()
    return jsonify({'message': '已成功退出'}), 200
#获取用户信息 API
@auth_bp.route('/profile', methods=['GET'])
@login_required
#定义一个路由，处理 /profile 地址的 GET 请求，调用 profile 函数，并使用 @login_required 装饰器保护该路由。
def profile():
    return jsonify({'user': current_user.to_dict()}), 200