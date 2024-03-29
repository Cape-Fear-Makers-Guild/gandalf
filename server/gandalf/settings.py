"""
Django settings for gandalf project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import json
import locale

os.umask(2)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO: read https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/


def getEnvStrOrDefault(name: str, default: str) -> str:
    val = os.getenv(name)
    if not val:
        print("Missing {} env var, falling back to default: {}".format(name, default))
        return default
    return val


def getEnvStrOrRaise(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError("Missing {} env var".format(name))
    return val


def getEnvBoolOrDefault(name: str, default: bool) -> bool:
    env_val = getEnvStrOrDefault(name, json.dumps(default))
    return json.loads(env_val.lower())


SECRET_KEY = getEnvStrOrDefault("DJANGO_SECRET_KEY", "TODO")
UT_BEARER_SECRET = getEnvStrOrDefault("GANDALF_BEARER_SECRET", "Foo")
GRANT_AMNESTY = getEnvBoolOrDefault("GANDALF_GRANT_AMNESTY", True)
DEBUG = getEnvBoolOrDefault("DJANGO_DEBUG", True)

# TODO: verify these settings are what we want and actually work
if getEnvBoolOrDefault("DJANGO_ENABLE_SECURE_SETTINGS", False):
    SECURE_HSTS_SECONDS = 120
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


ALLOWED_HOSTS = ["127.0.0.1", "gandalf.cfmakers.net"]
env_allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS")
if env_allowed_hosts:
    ALLOWED_HOSTS.append(env_allowed_hosts)

# Application definition

INSTALLED_APPS = [
    "import_export",
    "simple_history",
    "search_admin_autocomplete",
    "gandalf",
    "members.apps.UserConfig",
    "acl.apps.AclConfig",
    "selfservice.apps.SelfserviceConfig",
    "unknowntags.apps.UnknowntagsConfig",
    "servicelog.apps.ServicelogConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

SITE_ID = 1

MIDDLEWARE = [
    "allow_cidr.middleware.AllowCIDRMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

env_allowed_cidr = os.getenv("DJANGO_ALLOWED_CIDR")
ALLOWED_CIDR_NETS = ["192.168.86.0/24"]
if env_allowed_cidr:
    ALLOWED_CIDR_NETS.append(env_allowed_cidr)

ROOT_URLCONF = "gandalf.urls"

TEMPLATE_LOADERS = ("django.template.loaders.app_directories.load_template_source",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_settings_export.settings_export",
            ],
        },
    },
]

SETTINGS_EXPORT = [
    "GRANT_AMNESTY",
]

WSGI_APPLICATION = "gandalf.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

db_engine = getEnvStrOrDefault("DJANGO_DB_ENGINE", "sqlite")
if db_engine in ["sqlite", "sqlite3", "django.db.backends.sqlite3"]:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": getEnvStrOrRaise("DJANGO_DB_ENGINE"),
            "NAME": getEnvStrOrRaise("DJANGO_DB_NAME"),
            "USER": getEnvStrOrRaise("DJANGO_DB_USER"),
            "PASSWORD": getEnvStrOrRaise("DJANGO_DB_PASSWORD"),
            "HOST": getEnvStrOrRaise("DJANGO_DB_HOST"),
            "PORT": getEnvStrOrRaise("DJANGO_DB_PORT"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

env_TZ = os.getenv("TZ")
TIME_ZONE = "America/New_York" if not env_TZ else env_TZ

USE_I18N = True

USE_TZ = True

# -- START - Custom formatting of date/time and numbers ----
USE_L10N = False

DATETIME_FORMAT = "D Y-m-d G:i:s"
TIME_FORMAT = "G:i:s"
DATE_FORMAT = "D Y-m-d"
SHORT_DATE_FORMAT = "Y-m-d"

YEAR_MONTH_FORMAT = r"Y-m"
MONTH_DAY_FORMAT = r"m-d"
SHORT_DATETIME_FORMAT = "Y-m-d G:i"
FIRST_DAY_OF_WEEK = 0  # Sunday

DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."
NUMBER_GROUPING = 3
# -- END - Custom formatting of date/time and numbers ----


LOGIN_URL = "/login/"
# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = []

AUTH_USER_MODEL = "members.User"
MEDIA_URL = "/media/"

MAX_ZIPFILE = 48 * 1024 * 1024
MIN_IMAGE_SIZE = 2 * 1024
MAX_IMAGE_SIZE = 8 * 1024 * 1024
MAX_IMAGE_WIDTH = 1280

from stdimage.validators import MinSizeValidator, MaxSizeValidator

IMG_VALIDATORS = [MinSizeValidator(100, 100), MaxSizeValidator(8000, 8000)]

# Note: the labels are effectively 'hardcoded' in the templates
# and code; the sizes are free to edit.
#
IMG_VARIATIONS = {
    "thumbnail": (100, 100, True),
    "medium": (300, 200),
    "large": (600, 400),
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "qr-code": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "qr-code-cache",
        "TIMEOUT": 3600,
    },
}

# Only show the past 7 days of unknown tags. And up to 10.
#
UT_DAYS_CUTOFF = 7
UT_COUNT_CUTOFF = 10

# Extact spelling as created in 'group' through the /admin/ interface.
NETADMIN_USER_GROUP = "network admins"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
