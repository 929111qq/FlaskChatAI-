from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db


#用户模型类定义
#定义一个名为 User 的类，继承自 UserMixin 和 db.Model。
# 这意味着 User 类将具备用户认证的所有功能（来自 UserMixin）以及数据库模型的功能（来自 db.Model）。
#
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)#一列
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    #定义一个名为 created_at 的列，类型为日期时间。默认值为当前 UTC 时间，表示用户创建的时间。,
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#定义一个方法 to_dict，将用户实例转换为字典格式,
# 返回一个字典，包含用户的 id、username、email 和 created_at 字段。如果 created_at 存在，则以 ISO 格式返回。
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }