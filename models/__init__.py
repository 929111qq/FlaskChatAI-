from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
#创建一个 LoginManager 实例，用于处理用户认证和会话管理。Flask-Login 是一个扩展库，帮助管理用户登录状态。
login_manager = LoginManager()
#初始化函数
def init_app(app):
    #将 SQLAlchemy 实例与 Flask 应用程序关联。通过这个调用，SQLAlchemy 将能够访问应用的配置，并且可以使用应用的上下文来执行数据库操作。。
    db.init_app(app)
    #将 LoginManager 实例与 Flask 应用程序关联。这使得 Flask-Login 能够处理用户会话和认证相关的功能。定在每个请求结束后执行 self._update_remember_cookie 方法。
    # 这通常用于处理 cookie 或其他响应的后续操作。
    login_manager.init_app(app)
    #指定登录视图的端点名称为 'login'。这意味着，当用户尝试访问需要登录的页面时，如果他们尚未登录，Flask-Login 会将他们重定向到这个 'login' 路由。
    login_manager.login_view = 'login'