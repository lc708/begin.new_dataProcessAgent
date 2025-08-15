#!/bin/bash
set -e

# 获取Railway分配的端口，默认为80
NGINX_PORT=${PORT:-80}

echo "=== 数据处理Agent启动 ==="
echo "Nginx将监听端口: $NGINX_PORT"

# 替换Nginx配置中的端口
sed "s/listen 80;/listen $NGINX_PORT;/g" /etc/nginx/nginx.conf > /tmp/nginx.conf
cp /tmp/nginx.conf /etc/nginx/nginx.conf

echo "Nginx配置已更新"

# 启动Supervisor管理所有服务
echo "启动Supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
