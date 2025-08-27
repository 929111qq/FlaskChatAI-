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
3. 首次运行会自动建表
## 4. 启动服务
```bash
python app.py
```
或
```bash
bash run.sh
```
浏览器访问：http://localhost:5000

## 5. 常见问题

- **数据库连接失败**：检查MySQL是否启动、账号密码是否正确、端口是否开放。
- **AI不可用**：请配置有效的OPENAI_API_KEY。
- **依赖缺失**：请确保已执行 `pip install -r requirements.txt`。

## 6. 其他
- 支持WebSocket实时聊天（需前端配合）。
- 支持自定义会话反馈、主题、上下文。
- 可扩展接入其他AI大模型。

---
