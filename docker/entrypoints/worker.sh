#!/bin/bash
set -e

echo "Starting Superset worker..."

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

# 启动 Celery Worker
echo "Starting Celery worker..."
exec celery --app=superset.tasks.celery_app:app worker \
    --pool=prefork \
    --concurrency=4 \
    --loglevel=INFO \
    --queues=queries,sql_lab,email_reports,reports
