# 聊天相关API（发送消息、获取历史记录等）
"""
Blueprint：用于创建 Flask 蓝图，组织路由。
request：处理 HTTP 请求数据。
jsonify：将 Python 对象转换为 JSON 格式的响应。
login_required 和 current_user：用于用户认证。
db：数据库对象，进行 ORM 操作。
ChatMessage 和 ChatSession：导入聊天消息和会话模型。
ai_handler：自定义模块，处理 AI 相关功能。
uuid：生成唯一标识符。
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.chat import ChatMessage, ChatSession
from utils.ai_handlers import ai_handler
import uuid
import json
#创建蓝图：定义一个名为 chat 的蓝图，用于组织聊天相关的路由。
chat_bp = Blueprint('chat', __name__)

#发送消息 API
@chat_bp.route('/send', methods=['POST'])
@login_required
#定义路由：处理 /send 的 POST 请求，用户必须登录才能访问。
def send_message():
    #处理 HTTP 请求数据
    data = request.get_json()
    message = data.get('message', '').strip()
    session_id = data.get('session_id')
    #消息验证：如果消息为空，返回 400 错误。
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    #会话管理：如果没有提供 session_id，生成一个新的 UUID，并创建一个新的 ChatSession 实例。
    if not session_id:
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(user_id=current_user.id, session_id=session_id)
        db.session.add(chat_session)
#获取聊天历史：查询当前用户在指定会话中的最近 10 条聊天记录，并将其转换为字典格式。
    chat_history = ChatMessage.query.filter_by(user_id=current_user.id, session_id=session_id).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    chat_history_dict = [chat.to_dict() for chat in reversed(chat_history)]
#生成 AI 回复：调用 ai_handler 的 generate_response 方法，生成 AI 的回复。
    ai_response = ai_handler.generate_response(message, chat_history_dict)
#保存消息：创建 ChatMessage 实例，保存用户发送的消息和 AI 回复，并提交到数据库。
    chat_message = ChatMessage(user_id=current_user.id, message=message, response=ai_response, session_id=session_id)
    db.session.add(chat_message)
    db.session.commit()

    return jsonify({'message': chat_message.to_dict(), 'session_id': session_id}), 200
#获取聊天历史 API
@chat_bp.route('/history/', methods=['GET'])
@login_required
#定义路由：处理 /history/ 的 GET 请求，用户必须登录。
def get_chat_history():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': '缺少session_id'}), 400
    #查询消息：获取指定会话中的所有消息，按时间升序排列，并返回 JSON 格式。
    messages = ChatMessage.query.filter_by(user_id=current_user.id, session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    return jsonify({'messages': [msg.to_dict() for msg in messages]}), 200
#获取聊天会话 API
@chat_bp.route('/sessions', methods=['GET'])
@login_required
#定义路由：处理 /sessions 的 GET 请求，用户必须登录。
def get_chat_sessions():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return jsonify({'sessions': [session.to_dict() for session in sessions]}), 200

#会话反馈 CRUD
@chat_bp.route('/session/<session_id>/feedback', methods=['GET'])
@login_required
#获取反馈
def get_feedback(session_id):
    #定义路由：处理获取指定会话反馈的请求。查询会话，如果不存在则返回 404。
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    return jsonify({'feedback': session.feedback}), 200



@chat_bp.route('/session/<session_id>/feedback', methods=['POST'])
@login_required
#设置反馈,更新反馈：处理 POST 请求，更新指定会话的反馈。
def set_feedback(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    feedback = data.get('feedback')
    session.feedback = feedback
    db.session.commit()
    return jsonify({'message': '反馈已更新', 'feedback': session.feedback}), 200
#删除反馈
@chat_bp.route('/session/<session_id>/feedback', methods=['DELETE'])
@login_required
#删除反馈：处理 DELETE 请求，清除指定会话的反馈。
def delete_feedback(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    session.feedback = None
    db.session.commit()
    return jsonify({'message': '反馈已删除'}), 200

# 会话主题 CRUD
@chat_bp.route('/session/<session_id>/topic', methods=['GET'])
@login_required
def get_topic(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    return jsonify({'topic': session.topic}), 200

@chat_bp.route('/session/<session_id>/topic', methods=['POST'])
@login_required
def set_topic(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    topic = data.get('topic')
    session.topic = topic
    db.session.commit()
    return jsonify({'message': '主题已更新', 'topic': session.topic}), 200

@chat_bp.route('/session/<session_id>/topic', methods=['DELETE'])
@login_required
def delete_topic(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    session.topic = None
    db.session.commit()
    return jsonify({'message': '主题已删除'}), 200

# 会话上下文 CRUD
@chat_bp.route('/session/<session_id>/context', methods=['GET'])
@login_required
def get_context(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    context = json.loads(session.context) if session.context else None
    return jsonify({'context': context}), 200

@chat_bp.route('/session/<session_id>/context', methods=['POST'])
@login_required
def set_context(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    # 支持部分字段更新
    context = json.loads(session.context) if session.context else {}
    context.update(data.get('context', {}))
    session.context = json.dumps(context, ensure_ascii=False)
    db.session.commit()
    return jsonify({'message': '上下文已更新', 'context': context}), 200

@chat_bp.route('/session/<session_id>/context', methods=['DELETE'])
@login_required
def delete_context(session_id):
    session = ChatSession.query.filter_by(session_id=session_id, user_id=current_user.id).first_or_404()
    session.context = None
    db.session.commit()
    return jsonify({'message': '上下文已删除'}), 200