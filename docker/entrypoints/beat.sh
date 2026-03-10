#!/bin/bash
set -e

echo "Starting Superset beat scheduler..."

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

# 启动 Celery Beat
echo "Starting Celery beat scheduler..."
exec celery --app=superset.tasks.celery_app:app beat \
    --loglevel=INFO \
    --schedule=/app/superset_home/celerybeat-schedule
