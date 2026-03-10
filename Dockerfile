FROM apache/superset:latest

USER root
# 安装额外的数据库驱动（根据需要添加）
RUN python -m ensurepip --upgrade && \
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    psycopg2-binary \
    redis \
    pymysql \
    sqlalchemy-bigquery \
    Pillow \
    werkzeug==2.3.7 \
    flask==2.3.3 \
    Authlib>=1.0.0


# 安装 netcat 和中文语言支持
# 使用阿里云镜像源加速（仅当 sources.list 存在时）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    netcat-openbsd \
    tzdata \
    locales \
    nano \
    && ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && echo "zh_CN.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen zh_CN.UTF-8 \
    && update-locale LANG=zh_CN.UTF-8 LANGUAGE=zh_CN:zh LC_ALL=zh_CN.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# 设置中文环境变量
ENV LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8 \
    TZ=Asia/Shanghai

# 创建上传目录并设置权限
RUN mkdir -p /app/uploads /app/superset_home /app/pythonpath /app/docker/entrypoints \
    && chown -R superset:superset /app/uploads /app/superset_home /app/pythonpath /app/docker \
    && chmod 755 /app/superset_home

# 复制 entrypoint 脚本并设置权限
COPY --chown=superset:superset docker/entrypoints/*.sh /app/docker/entrypoints/
RUN chmod +x /app/docker/entrypoints/*.sh

# 复制自定义配置
COPY --chown=superset:superset feishu_auth.py /app/pythonpath/
COPY --chown=superset:superset superset_config.py /app/pythonpath/

USER superset

    
# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8088/health || exit 1
