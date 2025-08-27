#AI处理工具（模型加载、请求处理、结果解析等）

from openai import OpenAI
import os
import logging

# 设置日志记录
logger = logging.getLogger(__name__)


class AIHandler:
    def __init__(self):
        self.api_key = os.environ.get('QIANFAN_API_KEY')
        self.appid = os.environ.get('QIANFAN_APPID')
        self.base_url = "https://qianfan.baidubce.com/v2"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={"appid": self.appid} if self.appid else None
        )

    def generate_response(self, message: str, chat_history: list = None) -> str:
        messages = []
        # 系统提示
        messages.append({'role': 'system', 'content': '你是一个智能助手，请用中文回答用户的问题。'})
        # 添加历史对话
        if chat_history:
            for chat in chat_history[-10:]:
                messages.append({"role": "user", "content": chat.get('message', '')})
                if chat.get('response'):
                    messages.append({"role": "assistant", "content": chat.get('response', '')})
        # 添加当前消息
        messages.append({'role': 'user', 'content': message})
        try:
            completion = self.client.chat.completions.create(
                model="ernie-4.0-turbo-8k",  # 可根据实际权限更换模型
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"千帆API调用失败: {str(e)}")
            return "抱歉，AI服务暂时不可用。"

    def generate_session_title(self, first_message: str) -> str:
        return first_message[:15] + ("..." if len(first_message) > 15 else "")

# 创建全局实例
ai_handler = AIHandler()