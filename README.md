# Apache Superset 5.0 Docker Compose 部署

本项目提供 Apache Superset 5.0 版本的 Docker Compose 部署配置，支持数据本地化存储。

## 项目结构

```
.
├── docker-compose.yml          # Docker Compose 配置文件
├── Dockerfile                  # Superset 镜像构建文件
├── superset_config.py          # Superset 配置文件
├── .env                        # 环境变量配置
├── .dockerignore               # Docker 构建忽略文件
├── docker/
│   └── entrypoints/
│       ├── run-server.sh       # 服务器启动脚本
│       ├── init.sh             # 初始化脚本
│       ├── worker.sh           # Celery Worker 启动脚本
│       └── beat.sh             # Celery Beat 启动脚本
└── data/                       # 数据本地化目录（自动创建）
    ├── postgres/               # PostgreSQL 数据
    ├── redis/                  # Redis 数据
    ├── superset/               # Superset 应用数据
    └── uploads/                # 上传文件目录
```

## 数据本地化说明

所有数据都存储在本地 `./data` 目录下：

| 服务 | 本地路径 | 容器路径 | 说明 |
|------|----------|----------|------|
| PostgreSQL | `./data/postgres` | `/var/lib/postgresql/data` | 数据库文件 |
| Redis | `./data/redis` | `/data` | 缓存数据 |
| Superset | `./data/superset` | `/app/superset_home` | 应用配置和会话 |
| Uploads | `./data/uploads` | `/app/uploads` | 上传的文件和图片 |

## 快速开始

### 1. 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存

### 2. 配置环境变量

编辑 `.env` 文件，修改以下配置：

```bash
# 必须修改的安全密钥（使用随机字符串）
SUPERSET_SECRET_KEY=your-super-secret-key-change-this-in-production

# Mapbox API 密钥（可选，用于地图可视化）
MAPBOX_API_KEY=your-mapbox-api-key
```

生成随机密钥：
```bash
# Linux/Mac
openssl rand -base64 42

# Windows PowerShell
[Convert]::ToBase64String((1..42 | ForEach-Object { Get-Random -Maximum 256 } | ForEach-Object { [byte]$_ }))
```

### 3. 启动服务

#### 首次部署（需要初始化）

```bash
# 创建数据目录
mkdir -p data/postgres data/redis data/superset data/uploads

# 启动数据库和 Redis
docker-compose up -d db redis

# 等待数据库就绪（约 10-30 秒）
sleep 30

# 初始化 Superset
docker-compose --profile init run --rm superset-init

# 启动所有服务
docker-compose up -d
```

#### 后续启动

```bash
docker-compose up -d
```

### 4. 访问 Superset

- 地址：http://localhost:8088
- 默认用户名：`admin`
- 默认密码：`admin`

### 5. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f superset
docker-compose logs -f superset-worker
```

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps
```

### 数据库管理

```bash
# 进入数据库容器
docker-compose exec db psql -U superset -d superset

# 备份数据库
docker-compose exec db pg_dump -U superset superset > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U superset -d superset < backup.sql
```

### Superset 管理

```bash
# 进入 Superset 容器
docker-compose exec superset bash

# 升级数据库
superset db upgrade

# 创建管理员用户
superset fab create-admin

# 初始化 Superset
superset init

# 加载示例数据
superset load-examples

# 更新权限
superset init
```

## 配置说明

### 数据库驱动

默认已安装的数据库驱动：
- PostgreSQL (`psycopg2-binary`)
- MySQL (`pymysql`)
- BigQuery (`sqlalchemy-bigquery`)
- Trino (`trino`)
- Hive (`pyhive`, `impyla`)
- ClickHouse (`clickhouse-connect`)
- DuckDB (`duckdb-engine`)

如需添加其他驱动，请修改 `Dockerfile`。

### 缓存配置

Redis 被配置为多个用途：
- **DB 0**: Celery Broker
- **DB 1**: Celery Results / Data Cache
- **DB 2**: Filter State Cache
- **DB 3**: Explore Form Data Cache

### 功能开关

在 `superset_config.py` 中可启用/禁用功能：

```python
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,           # 告警和报告
    "DASHBOARD_RBAC": True,          # 仪表板 RBAC
    "EMBEDDED_SUPERSET": True,       # 嵌入式 Superset
    "ENABLE_TEMPLATE_PROCESSING": True,  # Jinja2 模板
    "DASHBOARD_CROSS_FILTERS": True, # 跨图表筛选
    "DASHBOARD_NATIVE_FILTERS": True, # 原生筛选器
}
```

## 备份与恢复

### 完整备份

```bash
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T db pg_dump -U superset superset > $BACKUP_DIR/database.sql

# 备份 Superset 数据
cp -r ./data/superset $BACKUP_DIR/superset

# 备份上传文件
cp -r ./data/uploads $BACKUP_DIR/uploads

echo "Backup completed: $BACKUP_DIR"
```

### 完整恢复

```bash
#!/bin/bash
BACKUP_DIR="./backups/20240101_120000"

# 停止服务
docker-compose down

# 恢复数据库
docker-compose up -d db
sleep 10
docker-compose exec -T db psql -U superset -d superset < $BACKUP_DIR/database.sql

# 恢复数据文件
cp -r $BACKUP_DIR/superset/* ./data/superset/
cp -r $BACKUP_DIR/uploads/* ./data/uploads/

# 启动服务
docker-compose up -d
```

## 故障排除

### 1. 数据库连接失败

```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重置数据库（会丢失数据）
docker-compose down -v
rm -rf ./data/postgres
mkdir -p ./data/postgres
docker-compose up -d
```

### 2. 权限问题

```bash
# 修复数据目录权限
sudo chown -R 1000:1000 ./data
```

### 3. 内存不足

如果服务因内存不足崩溃，请增加 Docker 内存限制（建议至少 4GB）。

### 4. 密钥错误

如果出现 `SECRET_KEY` 相关错误，请确保：
1. 修改了 `.env` 文件中的 `SUPERSET_SECRET_KEY`
2. 密钥长度至少 16 个字符
3. 重启服务：`docker-compose restart`

## 安全建议

1. **修改默认密码**：首次登录后立即修改 admin 密码
2. **使用强密钥**：生成足够长度的随机字符串作为 `SUPERSET_SECRET_KEY`
3. **启用 HTTPS**：生产环境应配置反向代理（Nginx/Traefik）并启用 HTTPS
4. **限制访问**：配置防火墙规则，仅允许必要端口访问
5. **定期备份**：设置定时任务备份数据库和数据目录

## 升级指南

### 升级到 Superset 新版本

1. 备份数据
2. 修改 `Dockerfile` 中的版本号
3. 重新构建镜像：`docker-compose build --no-cache`
4. 升级数据库：`docker-compose run --rm superset superset db upgrade`
5. 重启服务：`docker-compose up -d`

## 参考文档

- [Apache Superset 官方文档](https://superset.apache.org/docs/intro)
- [Superset GitHub](https://github.com/apache/superset)
- [Docker Compose 文档](https://docs.docker.com/compose/)
