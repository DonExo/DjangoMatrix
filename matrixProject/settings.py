from pathlib import Path
import os
import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = env("DEBUG", default=False)

SENTRY_DSN = env("SENTRY_DSN", default=None)
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="dev")

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]  # For local development
else:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=1.0,
        send_default_pii=True  # sends user info if available
    )

GITHUB_TOKEN = env("GITHUB_TOKEN", default=None)
SECRET_KEY = env("SECRET_KEY", default="django-insecure-xnv5ffvt@8)6%8*3j4f6&5qt#cj(z^=)dri)lgrbg_&ha2t-p5")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

PACKAGES_PER_PAGE_DEFAULT = 25
PACKAGES_PER_PAGE_OPTIONS = [10, 25, 50, 100]
DAYS_UNMAINTAINED = 3 * 365  # 3 years

USE_THOUSAND_SEPARATOR = True

ADMIN_URL_PATH = env('DJANGO_ADMIN_PATH', default='admin/')

FORMS_URLFIELD_ASSUME_HTTPS=True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'django_tables2',
    'django_extensions',

    # Local apps
    'matrix',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'matrixProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'matrixProject.wsgi.application'

DATABASES = {
    'default': env.db(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

CACHES = {
    "default": {
        "BACKEND": env("CACHE_BACKEND", default="django.core.cache.backends.dummy.DummyCache"),
        "LOCATION": env("CACHE_LOCATION", default=""),  # Empty for DummyCache
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

