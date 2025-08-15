# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 复制配置文件
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start_with_nginx.sh /start_with_nginx.sh

# 创建必要的目录
RUN mkdir -p logs temp uploads /var/log/supervisor

# 设置权限
RUN chmod +x start_with_nginx.sh

# 健康检查 - 检查Nginx端口
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT:-80}/health || exit 1

# 暴露端口 - Railway分配的主端口用于Nginx
EXPOSE $PORT
EXPOSE 80

# 启动命令 - 使用启动脚本配置端口并启动所有服务
CMD ["/start_with_nginx.sh"]
