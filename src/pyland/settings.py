import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import DisallowedHost
from environs import Env

from pyland.loguru_django import LoguruInterceptHandler

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env()

# === SECURITY ===
SECRET_KEY = env.str("SECRET_KEY", "replace_me")
DEBUG = env.bool("DEBUG", False)

# ALLOWED_HOSTS configuration
# In production, Django requires explicit host validation
# But for K8s health checks from pod IPs, we'll use '*' and rely on Ingress for security
ALLOWED_HOSTS = (
    ["*"]
    if not DEBUG and env.bool("K8S_DEPLOYMENT", default=False)
    else env.list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])
)

# Allow Kubernetes pod IPs for health checks
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# === LOCALIZATION ===
TIME_ZONE = "Asia/Tbilisi"
USE_I18N = True
USE_TZ = True

LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
    ("ka", "ქართული"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

PHONENUMBER_DEFAULT_REGION = "GE"

# === MODELTRANSLATION ===
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
MODELTRANSLATION_LANGUAGES = ("ru", "en", "ka")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("ru", "en")
MODELTRANSLATION_PREPOPULATE_LANGUAGE = "ru"

# === SITES / DOMAINS ===
SITE_ID = 1

# === CSRF ===
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY", default=True)
CSRF_COOKIE_SAMESITE = env.str("CSRF_COOKIE_SAMESITE", default="Lax")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
SESSION_COOKIE_HTTPONLY = env.bool("SESSION_COOKIE_HTTPONLY", default=True)
SESSION_COOKIE_SAMESITE = env.str("SESSION_COOKIE_SAMESITE", default="Lax")

# === TEMPLATES ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.footer_data",
                "core.context_processors.header_courses",
                "reviewers.context_processors.reviewers_context",
            ],
        },
    },
]
# === APPS ===
INSTALLED_APPS = [
    # Modeltranslation (MUST be before admin)
    "modeltranslation",
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Core apps
    "authentication",  # Аутентификация и управление пользователями
    "core",  # общее
    "students",  # Функционал для студентов
    "courses",  # курсы / уроки
    "certificates",  # сертификаты
    "payments",  # платежи
    "support",  # тикеты, саппорт
    "reviewers",  # отзывы
    "mentors",  # менторы
    "managers",  # менеджер
    "notifications",  # email/Telegram/SMS уведомления
    "blog",  # статьи, новости, контент для SEO
    # Third-party
    "ninja",
    "ninja_jwt",
    "ninja_extra",
    "phonenumber_field",
    "django_countries",
    "debug_toolbar",
    "markdownify",
    "corsheaders",
    "taggit",
    "django_celery_beat",  # Celery Beat scheduler
]

# === LOGGING ===
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "disallowed_host_filter": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: not (
                record.exc_info and record.exc_info[0] is DisallowedHost
            ),
        },
        "page_not_found_filter": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: ("Not Found" not in record.getMessage()) or DEBUG,
        },
    },
    "handlers": {
        "loguru_console": {
            "()": LoguruInterceptHandler,
            "level": 1,
            "filters": ["page_not_found_filter", "disallowed_host_filter"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["loguru_console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["loguru_console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["loguru_console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["loguru_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["loguru_console"],
    },
}
# === MIDDLEWARE ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files serving
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # Core middleware
    "core.middleware.CoreRateLimitMiddleware",
    "core.middleware.CoreSecurityHeadersMiddleware",
    # Blog middleware
    "blog.middleware.RateLimitMiddleware",
    "blog.middleware.BlogSecurityHeadersMiddleware",
    # Managers middleware
    "managers.middleware.ManagerRateLimitMiddleware",
    "managers.middleware.ManagerSecurityHeadersMiddleware",
    # Students middleware
    "students.middleware.StudentsRateLimitMiddleware",
    "students.middleware.StudentsSecurityHeadersMiddleware",
    "students.middleware.ProgressCacheMiddleware",
    # "students.middleware.CacheHitCounterMiddleware",  # Отключен - заменяет глобальные методы cache
]

# === URL / WSGI ===
ROOT_URLCONF = "pyland.urls"
WSGI_APPLICATION = "pyland.wsgi.application"
LOGIN_URL = "/authentication/signin/"

# === DATABASE ===
DATABASES = {
    "default": env.dj_db_url("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# === AUTH ===
AUTH_USER_MODEL = "authentication.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Время действия ссылки для сброса пароля (в секундах)
# 86400 секунд = 24 часа (соответствует тексту в email-шаблоне)
PASSWORD_RESET_TIMEOUT = 86400

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.google.GoogleOAuth2",
)

# === SESSION SETTINGS ===
# Сессия истекает при закрытии браузера, если не выбран "Запомнить меня"
SESSION_COOKIE_AGE = 1209600  # 2 недели (в секундах)
SESSION_SAVE_EVERY_REQUEST = False  # Сохраняем сессию только при изменениях
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only в продакшене
SESSION_COOKIE_HTTPONLY = True  # Защита от XSS
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF защита
# === JWT AUTH ===
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# === STATIC & MEDIA ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise configuration for production static files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MANIFEST_STRICT = False  # Don't fail on missing files
WHITENOISE_AUTOREFRESH = DEBUG  # Auto-refresh in development

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === SOCIAL ===
SOCIAL_AUTH_JSONFIELD_ENABLED = env.bool("SOCIAL_AUTH_JSONFIELD_ENABLED", True)
SOCIAL_AUTH_GITHUB_KEY = env.str("SOCIAL_AUTH_GITHUB_KEY", "")
SOCIAL_AUTH_GITHUB_SECRET = env.str("SOCIAL_AUTH_GITHUB_SECRET", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = env.str(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI",
    "http://127.0.0.1:8080/google-auth/complete/google-oauth2/",
)

# === SITE URL ===
SITE_URL = env.str("SITE_URL", "http://127.0.0.1:8000")

# === EMAIL ===
EMAIL_BACKEND = env.str("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env.str("EMAIL_HOST", "smtp.gmail.com")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = env.int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", "noreply@example.com")

# === CORS ===
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", True)

# === DEBUG TOOLBAR ===
INTERNAL_IPS = ["127.0.0.1"]

# === CELERY ===
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Short task timeout for development
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 420  # 7 minutes

# === REDIS CACHING ===
# Поддержка кэширования Redis с автоматическим fallback на dummy cache
# Установите DISABLE_CACHE=true для принудительного отключения кэша
REDIS_URL = env.str("REDIS_URL", "redis://localhost:6379/1")
DISABLE_CACHE = env.bool("DISABLE_CACHE", False)

# Флаг для предотвращения повторных сообщений при перезагрузке autoreloader
_is_main_process = os.environ.get("RUN_MAIN") != "true"

if DISABLE_CACHE:
    # Кэш принудительно отключен
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
    if _is_main_process:
        print("ℹ️  Cache disabled via DISABLE_CACHE setting")
else:
    # Проверяем доступность Redis и используем fallback на dummy cache
    import redis

    try:
        # Попытка подключения к Redis с таймаутом
        redis_client = redis.from_url(REDIS_URL, socket_connect_timeout=1)
        redis_client.ping()
        redis_client.close()

        # Redis доступен - используем его
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": REDIS_URL,
                "KEY_PREFIX": "pyland",
                "TIMEOUT": 300,  # 5 минут по умолчанию
                "OPTIONS": {
                    "socket_connect_timeout": 2,
                    "socket_timeout": 2,
                },
            }
        }
        if _is_main_process:
            print("✅ Redis cache enabled at", REDIS_URL)
    except (redis.ConnectionError, redis.TimeoutError, Exception):
        # Redis недоступен - используем dummy cache
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            }
        }
        if _is_main_process:
            print("⚠️  Redis unavailable, using dummy cache. Start Redis with: redis-server")

# Cache timeouts для разных типов данных
CACHE_TTL = {
    "article_list": 60 * 5,  # 5 минут
    "article_detail": 60 * 15,  # 15 минут
    "category_list": 60 * 30,  # 30 минут
    "tag_list": 60 * 30,  # 30 минут
    "stats": 60 * 10,  # 10 минут
    "featured": 60 * 5,  # 5 минут
}

# === LOGGING ===
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django.log",
            "formatter": "verbose",
        },
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django": {"handlers": ["file", "console"], "level": "WARNING", "propagate": True},
    },
}

# Markdownify settings
MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "em",
            "i",
            "li",
            "ol",
            "p",
            "strong",
            "ul",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "pre",
            "code",
            "br",
            "hr",
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
            "span",
            "div",
        ],
        "WHITELIST_ATTRS": ["href", "src", "alt", "title", "class", "id"],
        "MARKDOWN_EXTENSIONS": [
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.toc",
            "markdown.extensions.nl2br",
            "markdown.extensions.attr_list",
        ],
        "MARKDOWN_EXTENSION_CONFIGS": {
            "markdown.extensions.codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
                "guess_lang": True,
                "linenums": False,
            },
            "markdown.extensions.toc": {
                "anchorlink": True,
            },
        },
    }
}

# === SENTRY MONITORING ===
SENTRY_DSN = env.str("SENTRY_DSN", None)
SENTRY_ENVIRONMENT = env.str("SENTRY_ENVIRONMENT", "development")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=0.1 if SENTRY_ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1 if SENTRY_ENVIRONMENT == "production" else 1.0,
        send_default_pii=False,
        before_send=lambda event, hint: event if not DEBUG else None,
    )
