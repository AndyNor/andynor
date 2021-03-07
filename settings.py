import os

from this_env import this_env
this_env()


THIS_ENVIRONMENT = os.environ['THIS_ENV'] # "PROD" / "TEST" / "DEV"

if THIS_ENVIRONMENT == "PROD":
    SITE_URL = "https://andynor.net"
    ALLOWED_HOSTS = ['.andynor.net']
    DEBUG = False
    from secrets_prod import load_secrets
    load_secrets()
if THIS_ENVIRONMENT == "DEV":
    SITE_URL = "localhost:8001"
    ALLOWED_HOSTS = ['localhost',]
    DEBUG = True
    from secrets_dev import load_secrets
    load_secrets()

WSGI_APPLICATION = 'wsgi.application'
ROOT_URLCONF = 'mysite.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'drf_yasg',
    'mysite',
    'money',
    'power',
    'blog',
    'databases',
    'calc',
    'stocks',
    'conan',
)


REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        #'rest_framework.authentication.BasicAuthentication',
	),
}

SECRET_KEY = os.environ['SECRET_KEY']
SECURE_BROWSER_XSS_FILTER = True

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"

if THIS_ENVIRONMENT == "PROD":
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
if THIS_ENVIRONMENT == "DEV":
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = None

LOGIN_URL = '/login/'

if THIS_ENVIRONMENT == "PROD":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/home/andynor/webapps/django225/myproject/db.sqlite3',
        }
    }

if THIS_ENVIRONMENT == "DEV":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb-NO'
SITE_ID = 1
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = False
USE_I18N = True


if THIS_ENVIRONMENT == "PROD":
    MEDIA_ROOT = '/home/andynor/webapps/static_media/'
    MEDIA_URL = '/media/'
    FILE_ROOT = '/home/andynor/webapps/static_media/fileupload/'
    FILE_URL = '/media/fileuploads/'
    STATIC_ROOT = '/home/andynor/webapps/static/'
    STATIC_URL = '/static/'

if THIS_ENVIRONMENT == "DEV":
    MEDIA_ROOT = '_media/'
    MEDIA_URL = '/media/'
    FILE_ROOT = '_media/fileuploads/'
    FILE_URL = '/media/fileuploads/'
    STATIC_ROOT = '_static/'
    STATIC_URL = '/static/'


STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mysite.middleware.HTTPSRedirect',
    'mysite.middleware.CountVisitor',
    'mysite.middleware.SessionCleanup',
    'mysite.middleware.SecurityHeaders',
    'csp.middleware.CSPMiddleware',
)

# Security headers
# CSP reqires "CSPMiddleware"
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", 'https://www.youtube.com', 'https://s.ytimg.com', 'https://www.youtube-nocookie.com')
CSP_FRAME_SRC = ("'self'", 'https://www.youtube.com', 'https://www.youtube-nocookie.com')
CSP_STYLE_SRC = ("'unsafe-inline'", "'self'")
CSP_IMG_SRC = ("'self' data:")
CSP_INCLUDE_NONCE_IN = ['script-src']
SECURE_CONTENT_TYPE_NOSNIFF = True  # requires "SecurityMiddleware"

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "/home/andynor/webapps/django/myproject/templates/"
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            #only on development
            #'debug': DEBUG,
        },
    },
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
