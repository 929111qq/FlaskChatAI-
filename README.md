# AI 聊天服务器（支持MySQL、OpenAI、WebSocket）

## 1. 环境准备

- Python 3.8+
- MySQL 5.7+/8.0+
- 推荐使用虚拟环境

## 2. 安装依赖
```bash
pip install -r requirements.txt
```

## 3. 数据库配置

1. 创建数据库（如：chat）
2. 修改 `.env` 或环境变量，配置数据库连接：
```
DATABASE_URL=mysql+pymysql://用户名:密码@localhost/chat
SECRET_KEY=your-secret-key
OPENAI_API_KEY=你的OpenAI密钥（如需AI功能）
```

3. 首次运行会自动建表：
```bash
python app.py
```

## 4. 启动服务
```bash
python app.py
```
或
```bash
bash run.sh
```

浏览器访问：http://localhost:5000

## 5. 主要API说明

### 用户相关
- `POST /api/auth/register` 注册
- `POST /api/auth/login` 登录
- `POST /api/auth/logout` 登出
- `GET /api/auth/profile` 获取当前用户信息

### 聊天相关
- `POST /api/chat/send` 发送消息（需登录）
- `GET /api/chat/history/?session_id=xxx` 获取历史消息
- `GET /api/chat/sessions` 获取会话列表

### 会话自定义（需登录）
- `GET/POST/DELETE /api/chat/session/<session_id>/feedback` 反馈增查删
- `GET/POST/DELETE /api/chat/session/<session_id>/topic` 主题增查删
- `GET/POST/DELETE /api/chat/session/<session_id>/context` 上下文增查删

## 6. 常见问题
- **数据库连接失败**：检查MySQL是否启动、账号密码是否正确、端口是否开放。
- **AI不可用**：请配置有效的OPENAI_API_KEY。
- **依赖缺失**：请确保已执行 `pip install -r requirements.txt`。

## 7. 其他
- 支持WebSocket实时聊天（需前端配合）。
- 支持自定义会话反馈、主题、上下文。
- 可扩展接入其他AI大模型。

---
如有问题欢迎提issue或联系作者。