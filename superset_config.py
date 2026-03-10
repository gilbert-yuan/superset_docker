import os
import logging
from datetime import timedelta

# 启用 DEBUG 模式
DEBUG = True

# 配置日志级别
LOG_LEVEL = logging.DEBUG

# 配置飞书认证日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 禁用验证码（如果不需要 Google reCAPTCHA）
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""
RECAPTCHA_ENABLED = False

# 数据库配置
DATABASE_DB = os.getenv("DATABASE_DB", "superset")
DATABASE_HOST = os.getenv("DATABASE_HOST", "db")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "superset")
DATABASE_USER = os.getenv("DATABASE_USER", "superset")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_DIALECT = os.getenv("DATABASE_DIALECT", "postgresql")

SQLALCHEMY_DATABASE_URI = f"{DATABASE_DIALECT}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis 缓存配置
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")
REDIS_FILTER_DB = os.getenv("REDIS_FILTER_DB", "2")
REDIS_EXPLORE_DB = os.getenv("REDIS_EXPLORE_DB", "3")

REDIS_BASE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# 缓存配置
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": f"{REDIS_BASE_URL}/{REDIS_FILTER_DB}",
}

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_data_",
    "CACHE_REDIS_URL": f"{REDIS_BASE_URL}/{REDIS_RESULTS_DB}",
}

FILTER_STATE_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_filter_",
    "CACHE_REDIS_URL": f"{REDIS_BASE_URL}/{REDIS_FILTER_DB}",
}

EXPLORE_FORM_DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_explore_",
    "CACHE_REDIS_URL": f"{REDIS_BASE_URL}/{REDIS_EXPLORE_DB}",
}
# Celery 配置
class CeleryConfig:
    broker_url = f"{REDIS_BASE_URL}/{REDIS_CELERY_DB}"
    result_backend = f"{REDIS_BASE_URL}/{REDIS_RESULTS_DB}"

    worker_prefetch_multiplier = 10
    task_acks_late = True

    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": 600,
            "soft_time_limit": 600,
        },
    }

    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": timedelta(seconds=60),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": timedelta(seconds=600),
        },
    }

CELERY_CONFIG = CeleryConfig
# 密钥配置（必须修改）
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "CHANGE_ME_TO_A_RANDOM_STRING")

# 上传文件配置
UPLOAD_FOLDER = "/app/uploads"
IMG_UPLOAD_FOLDER = "/app/uploads/images"
IMG_UPLOAD_URL = "/static/uploads/"

# 数据目录
DATA_DIR = "/app/superset_home"

# 功能开关
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "DASHBOARD_RBAC": True,
    "EMBEDDED_SUPERSET": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ALLOW_ADHOC_SUBQUERY": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_DRILL_DOWN": True,
    "DASHBOARD_DRILL_TO_DETAIL": True,
    "DRILL_TO_DETAIL": True,
    "HORIZONTAL_FILTER_BAR": True,
}

# 地图配置
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY", "")

# 时区配置
DRUID_IS_ACTIVE = False
PREFERRED_DATABASES = [
    "PostgreSQL",
    "Presto",
    "Trino",
    "MySQL",
    "ClickHouse",
    "DuckDB",
]

# SQL Lab 配置
SQLLAB_ASYNC_TIME_LIMIT_SEC = 60 * 60 * 6  # 6 hours
SQLLAB_TIMEOUT = 300

# 图表数据行限制
ROW_LIMIT = 50000

# 会话配置
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# 跨域配置（如需）
ENABLE_CORS = False
CORS_OPTIONS = {}

# 日志配置
LOG_LEVEL = logging.DEBUG

# 中文支持配置
BABEL_DEFAULT_LOCALE = "zh"
BABEL_DEFAULT_FOLDER = "/app/superset/translations"
LANGUAGES = {
    "zh": {"flag": "cn", "name": "简体中文"},
    "en": {"flag": "us", "name": "English"},
}

# 确保语言包目录存在
import os
if not os.path.exists(BABEL_DEFAULT_FOLDER):
    os.makedirs(BABEL_DEFAULT_FOLDER, exist_ok=True)

# 默认时区设置为东八区（中国标准时间）
DEFAULT_TIMEZONE = "Asia/Shanghai"

# 日期时间格式本地化
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 数字格式（中国习惯：千分位逗号，小数点）
D3_FORMAT = {
    "decimal": ".",
    "thousands": ",",
    "grouping": [3],
    "currency": ["¥", ""],
}

# CSV 导出编码设置为 UTF-8 with BOM，确保 Excel 中文不乱码
CSV_EXPORT = {
    "encoding": "utf-8-sig",
}

# 启用中文分词支持（如使用中文标签）
TAGGING_SYSTEM = True 
from flask_appbuilder.security.manager import AUTH_OAUTH
from feishu_auth import CustomSsoSecurityManager
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        "name": "lark",
        "token_key": "access_token",  # Name of the token in the response of access_token_url
        "icon": "fa-dove",  # Icon for the provider
        "remote_app": {
            "client_id": os.getenv("FEISHU_APP_ID"),  # Client Id (Identify Superset application)
            "client_secret": os.getenv("FEISHU_APP_SECRET"),  # Secret for this Client Id (Identify Superset application)
            "access_token_method": "POST",  # HTTP Method to call access_token_url
            "api_base_url": "https://open.feishu.cn/open-apis/authen/v1/",
            "access_token_url": "https://open.feishu.cn/open-apis/authen/v2/oauth/token",
            "authorize_url": "https://accounts.feishu.cn/open-apis/authen/v1/authorize",
        },
    }
]
# Map Authlib roles to superset roles
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'
# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True
# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Gamma"
CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

 