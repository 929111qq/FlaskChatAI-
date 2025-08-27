from datetime import datetime
from models import db
import json


#定义了两个数据库模型 ChatSession 和 ChatMessage，用于管理聊天会话和聊天消息。
class ChatSession(db.Model):
    #定义一个名为 id 的列，类型为整数，且是主键，用于唯一标识每个聊天会话。
    id = db.Column(db.Integer, primary_key=True)
    #定义一个名为 session_id 的列，类型为字符串，最大长度为 64，必须唯一且不能为空，并且为其创建索引，以便于快速查询。
    session_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    #定义一个名为 user_id 的列，类型为整数，作为外键引用 user 表的 id 列，不能为空。
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #默认值为当前 UTC 时间，表示聊天会话开始时间。
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    #定义一个名为 status 的列，类型为字符串，最大长度为 20，默认值为 'active'，表示当前会话的状态。
    status = db.Column(db.String(20), default='active')
    #定义一个名为 topic 的列，类型为字符串，最大长度为 255，可以为空，表示聊天会话的主题。
    topic = db.Column(db.String(255), nullable=True)
    #定义一个名为 feedback 的列，类型为字符串，最大长度为 255，可以为空，表示用户对会话的反馈。
    feedback = db.Column(db.String(255), nullable=True)
    #定义一个名为 context 的列，类型为文本，可以为空，用于存储聊天上下文，通常以 JSON 字符串形式存储。
    context = db.Column(db.Text, nullable=True)  # 可存储JSON字符串
    meta_data = db.Column(db.Text, nullable=True) # 原metadata字段改名
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 表示聊天会话的创建时间

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'topic': self.topic,
            'feedback': self.feedback,
            'context': json.loads(self.context) if self.context else None,
            'meta_data': json.loads(self.meta_data) if self.meta_data else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(64), db.ForeignKey('chat_session.session_id'), nullable=False)
    #定义一个名为 message 的列，类型为文本，不能为空，表示用户发送的消息。
    message = db.Column(db.Text, nullable=False)
    #定义一个名为 response 的列，类型为文本，可以为空，用于存储 AI 的回复。
    response = db.Column(db.Text, nullable=True)
    #定义一个名为 sender 的列，类型为字符串，最大长度为 20，默认值为 'user'，表示消息的发送者（用户、助手或系统）。
    sender = db.Column(db.String(20), default='user')  # user/assistant/system
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'message': self.message,
            'response': self.response,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    def __repr__(self):
        return f"<ChatMessage {self.message}>"