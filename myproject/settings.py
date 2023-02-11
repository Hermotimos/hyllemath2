import io
import os
from urllib.parse import urlparse

import environ
from django.conf.locale.pl import formats as pl_formats
from google.cloud import secretmanager
from google.oauth2 import service_account


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IS_LOCAL_ENVIRON = True if os.environ.get('COMPUTERNAME') else False



# -----------------------------------------------------------------------------
# gaestd_py_django_secret_config

env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, ".env")

if os.path.isfile(env_file):
    # Use a local secret file, if provided
    env.read_env(env_file)
elif os.getenv("TRAMPOLINE_CI", None):
    # Create local settings if running with CI, for unit testing
    placeholder = (
        f"SECRET_KEY=a\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")



# -----------------------------------------------------------------------------


SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
DEBUG = True



# -----------------------------------------------------------------------------
#  gaestd_py_django_csrf

# SECURITY WARNING: It's recommended that you use this when running in production.
# The URL will be known once you first deploy to App Engine.
# This code takes the URL and converts it to both these settings formats.

APPENGINE_URL = env("APPENGINE_URL", default=None)
if APPENGINE_URL:
    # Ensure a scheme is present in the URL before it's processed.
    if not urlparse(APPENGINE_URL).scheme:
        APPENGINE_URL = f"https://{APPENGINE_URL}"

    # ALLOWED_HOSTS = [urlparse(APPENGINE_URL).netloc]
    # For enabling older app versions to host site
    ALLOWED_HOSTS = ['*']

    CSRF_TRUSTED_ORIGINS = [APPENGINE_URL]
    SECURE_SSL_REDIRECT = True

    # For get_absolute_url methods
    SERVER_ADDRESS = "https://hyllemath2.lm.r.appspot.com"

else:
    CSRF_TRUSTED_ORIGINS = [
        'https://8000-cs-570532252862-default.cs-europe-west4-bhnf.cloudshell.dev'
    ]
    ALLOWED_HOSTS = [
        '127.0.0.1',
    ]

    # For get_absolute_url methods
    SERVER_ADDRESS = '127.0.0.1:8000'



# -----------------------------------------------------------------------------


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # imported
    # 'crispy_forms',
    'debug_toolbar',
    # 'django_filters',

    # own
    # "polls"
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            'libraries': {
                'custom_filters': 'templatetags.custom_filters',
            },
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"



# -----------------------------------------------------------------------------
# Database

if os.getenv('GAE_ENV', '').startswith('standard'):
    # Requires DATABASE_URL environmental variable to be set
    DATABASES = {
        "default": env.db()
    }
elif IS_LOCAL_ENVIRON:
    DATABASES = {
        'default': {
            'ENGINE': env('LOCAL_DB_ENGINE'),
            'NAME': env('LOCAL_DB_DBNAME'),
            'USER': env('LOCAL_DB_USER'),
            'PASSWORD': env('LOCAL_DB_PASSWORD'),
            'HOST': env('LOCAL_DB_HOST'),
            'PORT': env('LOCAL_DB_PORT'),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'



# -----------------------------------------------------------------------------
# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: 501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: 501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: 501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: 501
    },
]



# -----------------------------------------------------------------------------
# Internationalization

# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'pl'
pl_formats.DATE_FORMAT = "Y-m-d"
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True



# -----------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)

if os.getenv('GAE_ENV', '').startswith('standard'):
    # https://medium.com/@umeshsaruk/upload-to-google-cloud-storage-using-django-storages-72ddec2f0d05

    # For media storage in the bucket
    GOOGLE_APPLICATION_CREDENTIALS = env("GOOGLE_APPLICATION_CREDENTIALS")
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS)
    # This might be needed to access Cloud Storage without credentials,
    # which should by possible from App Engine
    # https://pnote.eu/notes/django-app-engine-user-uploaded-files/

    GS_DEFAULT_ACL = 'publicRead'

    # TODO check if only one is needed: GS_CREDENTIALS or GS_DEFAULT_ACL

    DEFAULT_FILE_STORAGE = 'myproject.storages.GoogleCloudMediaFileStorage'
    STATICFILES_STORAGE = 'myproject.storages.GoogleCloudStaticFileStorage'

    GS_PROJECT_ID = 'hyllemath2'
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")

    STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/static/"
    STATIC_ROOT = "static/"

    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"
    MEDIA_ROOT = "media/"

else:
    # Use these settings to run "python manage.py collectstatic"
    # STATIC_ROOT = "static"
    # STATIC_URL = "/static/"
    # STATICFILES_DIRS = []

    # STATIC_ROOT necessary only in production (but also needed for collectstatic)
    STATIC_URL = 'static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

    MEDIA_ROOT = 'media'
    MEDIA_URL = 'media/'


# -----------------------------------------------------------------------------
# debug-toolbar

INTERNAL_IPS = ['127.0.0.1', ]
# debug-toolbar not rendering problem:
# https://www.taricorp.net/2020/windows-mime-pitfalls/
# https://stackoverflow.com/questions/16303098/django-development-server-and-mime-types/64055514#64055514
# After editing registry - restart local server for changes to take effect




# Default 1000 is too low for large inlines in admin
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
