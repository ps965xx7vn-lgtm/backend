import os
import re
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
                "django.template.context_processors.i18n",  # Для доступа к LANGUAGE_CODE
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.footer_data",
                "core.context_processors.header_courses",
                "reviewers.context_processors.reviewers_context",
                "students.context_processors.student_profile",
            ],
        },
    },
]
# === APPS ===
INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "authentication",
    "core",
    "students",
    "courses",
    "certificates",
    "payments",
    "reviewers",
    "mentors",
    "managers",
    "notifications",
    "blog",
    "social_django",
    "ninja",
    "ninja_jwt",
    "ninja_extra",
    "phonenumber_field",
    "django_countries",
    "debug_toolbar",
    "markdownify",
    "corsheaders",
    "taggit",
    "django_celery_beat",
]

# === LOGGING ===
IGNORABLE_404_URLS = [
    re.compile(r"^/\.well-known/"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/robots\.txt$"),
    re.compile(r"^/apple-touch-icon"),
]

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

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
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "loguru_console": {
            "()": LoguruInterceptHandler,
            "level": 1,
            "filters": ["page_not_found_filter", "disallowed_host_filter"],
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["loguru_console"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["file", "loguru_console"],
            "level": "WARNING",
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
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "core.middleware.CoreRateLimitMiddleware",
    "core.middleware.CoreSecurityHeadersMiddleware",
    "blog.middleware.RateLimitMiddleware",
    "blog.middleware.BlogSecurityHeadersMiddleware",
    "managers.middleware.ManagerRateLimitMiddleware",
    "managers.middleware.ManagerSecurityHeadersMiddleware",
    "students.middleware.StudentsRateLimitMiddleware",
    "students.middleware.StudentsSecurityHeadersMiddleware",
    "students.middleware.ProgressCacheMiddleware",
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

PASSWORD_RESET_TIMEOUT = 86400

AUTHENTICATION_BACKENDS = [
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

# === SESSION SETTINGS ===
SESSION_ENGINE = (
    "django.contrib.sessions.backends.db" if DEBUG else "django.contrib.sessions.backends.cache"
)
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
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
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG
WHITENOISE_MAX_AGE = 0 if DEBUG else 86400
WHITENOISE_KEEP_ONLY_HASHED_FILES = not DEBUG

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === SOCIAL AUTH ===
SOCIAL_AUTH_JSONFIELD_ENABLED = env.bool("SOCIAL_AUTH_JSONFIELD_ENABLED", True)
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ["email"]
SOCIAL_AUTH_USER_MODEL = "authentication.User"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/authentication/signin/"
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_GITHUB_KEY = env.str("SOCIAL_AUTH_GITHUB_KEY", "")
SOCIAL_AUTH_GITHUB_SECRET = env.str("SOCIAL_AUTH_GITHUB_SECRET", "")
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

SOCIAL_AUTH_REDIRECT_BASE = env.str("SITE_URL", "http://127.0.0.1:8000")

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_LOGOUT_REDIRECT_URL = "/"
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/"
SOCIAL_AUTH_URL_NAMESPACE = "social"

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
REDIS_URL = env.str("REDIS_URL", "redis://localhost:6379/1")
DISABLE_CACHE = env.bool("DISABLE_CACHE", False)
_is_main_process = os.environ.get("RUN_MAIN") != "true"

if DISABLE_CACHE:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
    if _is_main_process:
        print("ℹ️  Cache disabled via DISABLE_CACHE setting")
else:
    import redis

    try:
        redis_client = redis.from_url(REDIS_URL, socket_connect_timeout=1)
        redis_client.ping()
        redis_client.close()
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": REDIS_URL,
                "KEY_PREFIX": "pyland",
                "TIMEOUT": 300,
                "OPTIONS": {"socket_connect_timeout": 2, "socket_timeout": 2},
            }
        }
        if _is_main_process:
            print("✅ Redis cache enabled at", REDIS_URL)
    except (redis.ConnectionError, redis.TimeoutError, Exception):
        CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
        if _is_main_process:
            print("⚠️  Redis unavailable, using dummy cache. Start Redis with: redis-server")

CACHE_TTL = {
    "article_list": 300,
    "article_detail": 900,
    "category_list": 1800,
    "tag_list": 1800,
    "stats": 600,
    "featured": 300,
}

# === MARKDOWNIFY ===
# Конфигурация для безопасного рендеринга Markdown в HTML
# Используется в шаблонах через фильтр |markdownify
MARKDOWNIFY = {
    "default": {
        # HTML теги разрешенные в Markdown контенте
        "WHITELIST_TAGS": [
            # Текстовое форматирование
            "p",
            "br",
            "hr",
            "strong",
            "b",
            "em",
            "i",
            "u",
            "s",
            "mark",
            "abbr",
            "acronym",
            "cite",
            "q",
            # Заголовки
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            # Ссылки и медиа
            "a",
            "img",
            "figure",
            "figcaption",
            # Списки
            "ul",
            "ol",
            "li",
            "dl",
            "dt",
            "dd",
            # Цитаты и код
            "blockquote",
            "pre",
            "code",
            # Таблицы
            "table",
            "thead",
            "tbody",
            "tfoot",
            "tr",
            "th",
            "td",
            "caption",
            # Структурные контейнеры
            "div",
            "span",
            "section",
            "article",
        ],
        # HTML атрибуты разрешенные в Markdown контенте
        "WHITELIST_ATTRS": [
            # Базовые атрибуты
            "id",
            "class",
            "title",
            # Ссылки
            "href",
            "target",
            "rel",
            # Изображения
            "src",
            "alt",
            "width",
            "height",
            # Таблицы
            "colspan",
            "rowspan",
            "align",
            # Кастомные data-* атрибуты
            "data-*",
        ],
        # Протоколы разрешенные в атрибутах src и href
        "WHITELIST_PROTOCOLS": [
            "http",
            "https",
            "mailto",
            "tel",
        ],
        # Расширения Markdown для расширенного синтаксиса
        "MARKDOWN_EXTENSIONS": [
            "markdown.extensions.extra",  # Meta-расширение (abbr, attr_list, def_list, fenced_code, footnotes, tables, md_in_html)
            "markdown.extensions.codehilite",  # Подсветка синтаксиса кода
            "markdown.extensions.toc",  # Оглавление с якорными ссылками
            "markdown.extensions.nl2br",  # Авто-перенос строк <br>
            "markdown.extensions.sane_lists",  # Улучшенная обработка списков
            "markdown.extensions.smarty",  # Типографика (умные кавычки, тире)
        ],
        # Детальная конфигурация расширений
        "MARKDOWN_EXTENSION_CONFIGS": {
            "markdown.extensions.codehilite": {
                "css_class": "highlight",  # CSS класс для блоков кода
                "use_pygments": True,  # Использовать Pygments для подсветки
                "guess_lang": True,  # Авто-определение языка
                "linenums": False,  # Отключить нумерацию строк по умолчанию
                "noclasses": False,  # Использовать CSS классы вместо inline стилей
            },
            "markdown.extensions.toc": {
                "anchorlink": True,  # Добавлять якорные ссылки к заголовкам
                "permalink": False,  # Не добавлять постоянные ссылки
                "baselevel": 1,  # Базовый уровень заголовков
                "toc_depth": 6,  # Максимальная глубина оглавления
            },
            "markdown.extensions.extra": {
                "footnotes": {
                    "UNIQUE_IDS": True,  # Уникальные ID для сносок
                },
            },
        },
        # Настройки безопасности
        "STRIP": True,  # Удалять запрещенные теги вместо escape
        "BLEACH": True,  # Использовать bleach для очистки HTML
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

# === PADDLE BILLING ===
PADDLE_API_KEY = env.str("PADDLE_API_KEY", "")
PADDLE_SANDBOX_API_KEY = env.str("PADDLE_SANDBOX_API_KEY", "")
PADDLE_ENVIRONMENT = env.str("PADDLE_ENVIRONMENT", "sandbox")  # 'sandbox' or 'production'
PADDLE_WEBHOOK_SECRET = env.str("PADDLE_WEBHOOK_SECRET", "")
PADDLE_NAME = env.str("PADDLE_NAME", "pyland-main")

# === CURRENCY EXCHANGE RATES ===
# API ключ для получения актуальных курсов валют (exchangerate-api.com)
# Без ключа используются статичные fallback курсы
EXCHANGE_RATE_API_KEY = env.str("EXCHANGE_RATE_API_KEY", "")
