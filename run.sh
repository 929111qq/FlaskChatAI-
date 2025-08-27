#!/bin/bash

# 1. 加载 .env 环境变量
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# 2. 激活 Anaconda 虚拟环境
source activate chat_server

# 3. 启动服务（开发环境用 python app.py，生产环境用 gunicorn）
# 开发环境（推荐本地调试）
# python app.py

# 生产环境（推荐部署上线）
gunicorn --config gunicorn_config.py app:app