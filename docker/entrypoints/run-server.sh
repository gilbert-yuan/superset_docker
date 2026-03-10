#!/bin/bash
set -e

echo "Starting Superset server..."

# 确保目录权限正确
echo "Setting directory permissions..."
# 尝试创建必要的子目录
mkdir -p /app/superset_home/.superset /app/superset_home/uploads 2>/dev/null || echo "Cannot create subdirectories, but continuing..."
# 只尝试修改文件权限，不修改目录权限
find /app/superset_home -type f -exec chmod 644 {} \; 2>/dev/null || echo "Cannot change file permissions, but continuing..."
echo "Permission setup completed (some errors may be ignored)"

# 等待数据库就绪
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# 等待 Redis 就绪
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# 升级数据库（如果需要）
echo "Upgrading database..."
superset db upgrade

# 初始化 Superset（仅在首次运行时）
echo "Checking if Superset is initialized..."
# 尝试获取用户列表，如果失败则初始化
if ! superset fab list-users > /dev/null 2>&1; then
    echo "Initializing Superset..."
    superset fab create-admin \
        --username admin \
        --firstname Admin \
        --lastname User \
        --email admin@example.com \
        --password admin || true
    
    superset init
    
echo "Superset initialization completed!"
else
    echo "Superset is already initialized."
fi

# 启动服务器
echo "Starting Superset server on port 8088..."
exec gunicorn \
    --bind "0.0.0.0:8088" \
    --access-logfile "-" \
    --error-logfile "-" \
    --workers 4 \
    --worker-class gthread \
    --threads 4 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    "superset.app:create_app()"
