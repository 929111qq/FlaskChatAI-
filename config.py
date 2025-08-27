import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 应用的密钥，用于加密会话等
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    # 数据库连接字符串，默认使用 SQLite，便于本地开发
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chat.db'

    # 禁用对象修改追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API 密钥
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    WENXIN_API_KEY = os.environ.get('WENXIN_API_KEY')
    WENXIN_SECRET_KEY = os.environ.get('WENXIN_SECRET_KEY')

    # 最大上传文件大小限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # MySQL 连接池配置
    SQLALCHEMY_POOL_SIZE = 10  # 数据库连接池的大小
    SQLALCHEMY_MAX_OVERFLOW = 20  # 连接池允许的最大溢出连接数
    SQLALCHEMY_POOL_TIMEOUT = 30  # 连接池超时时间

    # AI 模型配置
    AI_MODEL = 'gpt-3.5-turbo'
    AI_MAX_TOKENS = 1000
    AI_TEMPERATURE = 0.7

    # 聊天配置
    MAX_CHAT_HISTORY = 50
    CHAT_TIMEOUT = 300  # 5分钟超时