#!/bin/bash
set -e

echo "Initializing Superset..."

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

# 升级数据库
echo "Upgrading database..."
superset db upgrade

# 创建管理员用户
echo "Creating admin user..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password admin || echo "Admin user already exists"

# 初始化 Superset
echo "Initializing Superset..."
superset init

# 加载示例数据（可选）
if [ "$SUPERSET_LOAD_EXAMPLES" = "yes" ]; then
    echo "Loading examples..."
    superset load-examples
fi

echo "Superset initialization complete!"
