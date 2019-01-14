"""
Django settings for makerspaceleiden project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6mh_k^thni&-6)!sfz#7i_6i@(6jesl&lrxba)#&nemt-dc0d7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [ '10.11.0.158', '*' ]

# Allow users to create their own entitlement as a one off
# bootstrapping thing.
#
GRAND_AMNESTY = True

# Application definition

INSTALLED_APPS = [
    'import_export',
    'simple_history',
    'qrcode',

    'storage.apps.StorageConfig',
    'memberbox.apps.MemberboxConfig',
    'members.apps.UserConfig',
    'acl.apps.AclConfig',
    'selfservice.apps.SelfserviceConfig',
    'ufo.apps.UfoConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
#    'autocomplete_light',
    'django.contrib.sites',
]

SITE_ID = 1

MIDDLEWARE = [
    'simple_history.middleware.HistoryRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'makerspaceleiden.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

SETTINGS_EXPORT = [ 'GRAND_AMNESTY', ]

WSGI_APPLICATION = 'makerspaceleiden.wsgi.application'

MAILINGLIST='deelnemers@makerspaceleiden.nl'
FROM_EMAIL="noc@makerspaceleiden.nl"
BASE='https://makerspaceleiden.nl/crm'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# For DEVLOPMNET  - fake bacend

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [ ]

AUTH_USER_MODEL = 'members.User'

MEDIA_ROOT="/tmp"
# MEDIA_ROOT =  os.path.join(BASE_DIR, 'media') 
MEDIA_URL = '/media/'

MAX_ZIPFILE=48*1024*1024
MIN_IMAGE_SIZE=2*1024
MAX_IMAGE_SIZE=8*1024*1024
MAX_IMAGE_WIDTH=1280

UFO_DEADLINE_DAYS=14
UFO_DISPOSE_DAYS=7

