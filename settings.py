import os

from this_env import this_env
this_env()


THIS_ENVIRONMENT = os.environ['THIS_ENV'] # "PROD" / "TEST" / "DEV"

if THIS_ENVIRONMENT == "DO_PROD":
	SITE_URL = "https://andynor.net"
	CSRF_TRUSTED_ORIGINS = [SITE_URL]
	ALLOWED_HOSTS = ['.andynor.net']#, '161.35.216.174']
	DEBUG = False
	# When running behind a reverse proxy/ingress that terminates TLS,
	# Django must trust X-Forwarded-Proto to avoid HTTPS redirect loops.
	SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
	USE_X_FORWARDED_HOST = True
	# Nginx already redirects HTTP→HTTPS; skip Django HTTPSRedirect to avoid
	# ERR_TOO_MANY_REDIRECTS if proxy headers do not reach the app unchanged.
	FORCE_HTTPS_REDIRECT_IN_DJANGO = False
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
	'mysite',
	'money',
	'power',
	'blog',
	'databases',
	'calc',
	'stocks',
)

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

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


if THIS_ENVIRONMENT == "DO_PROD":
	CSRF_COOKIE_SECURE = True
	CSRF_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SECURE = True

if THIS_ENVIRONMENT == "DEV":
	CSRF_COOKIE_SECURE = True
	CSRF_COOKIE_HTTPONLY = False
	SESSION_COOKIE_SECURE = False

LOGIN_URL = '/login/'


if THIS_ENVIRONMENT == "DO_PROD":
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': '/home/django/django_project/andynor/db.sqlite3',
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
USE_THOUSAND_SEPARATOR = False
USE_TZ = False
USE_I18N = True


if THIS_ENVIRONMENT == "DO_PROD":
	MEDIA_ROOT = '/home/django/django_project/andynor/media/'
	MEDIA_URL = '/media/'
	FILE_ROOT = '/home/django/django_project/andynor/media/fileuploads/'
	FILE_URL = '/media/fileuploads/'
	STATIC_ROOT = '/home/django/django_project/andynor/static/'
	STATIC_URL = '/static/'

	# 500 tracebacks: django.request logs to stderr, but gunicorn_error.log is easy to miss
	# or interleave; a dedicated file gives reliable exc_info / stack traces.
	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'formatters': {
			'detail': {
				'format': '{levelname} {asctime} {name} {pathname}:{lineno}\n{message}',
				'style': '{',
			},
		},
		'handlers': {
			'django_error_file': {
				'level': 'ERROR',
				'class': 'logging.handlers.RotatingFileHandler',
				'filename': '/home/django/django_project/andynor/django_error.log',
				'maxBytes': 5 * 1024 * 1024,
				'backupCount': 5,
				'formatter': 'detail',
			},
			'console': {
				'level': 'ERROR',
				'class': 'logging.StreamHandler',
				'formatter': 'detail',
			},
		},
		'loggers': {
			'django.request': {
				'handlers': ['django_error_file', 'console'],
				'level': 'ERROR',
				'propagate': False,
			},
		},
	}

if THIS_ENVIRONMENT == "DEV":
	MEDIA_ROOT = '_media/'
	MEDIA_URL = '/media/'
	FILE_ROOT = '_media/fileuploads/'
	FILE_URL = '/media/fileuploads/'
	STATIC_ROOT = '_static/'
	STATIC_URL = '/static/'

# Defining STORAGES replaces Django's built-in defaults; ``default`` is required
# for FileField/ImageField (media). ``staticfiles`` uses the manifest backend.
# Requires running `collectstatic` after changes to static assets.
STORAGES = {
	"default": {
		"BACKEND": "django.core.files.storage.FileSystemStorage",
	},
	"staticfiles": {
		"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
	},
}


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
CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = ("'self'", 'https://www.youtube.com', 'https://s.ytimg.com', 'https://www.youtube-nocookie.com')
CSP_FRAME_SRC = ("'self'", 'https://www.youtube.com', 'https://www.youtube-nocookie.com')
CSP_STYLE_SRC = ("'self'")
CSP_IMG_SRC = ("'self' data:")
CSP_STYLE_SRC = (
    "'self'", 
    "https://cdnjs.cloudflare.com",
    "'sha256-hMEnt2qMHAmQZgCjWJ4hweKuzi+3YEdUo00f8k/ebMo='", # jQuery's inline style
    # tablesorter "resizable" widget injects <style>...</style> via JS at runtime (no nonce possible)
    "'sha256-8SUl9xHjYV2TArOfAnCQwB7/lPW4lKCyVf7o9IF6gs8='",
    # Allow specific inline style attributes (hash-gated).
)
CSP_FONT_SRC = ("'self'", "https://cdnjs.cloudflare.com")
CSP_CONNECT_SRC = ("'self'", "https://andynor.net")
CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
CSP_MEDIA_SRC = ("'self'", "https://andynor.net", "http://localhost:8001")
SECURE_CONTENT_TYPE_NOSNIFF = True  # requires "SecurityMiddleware"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.contrib.auth.context_processors.auth',
				'django.template.context_processors.csrf',
				'django.template.context_processors.debug',
				'django.template.context_processors.i18n',
				'django.template.context_processors.media',
				'django.template.context_processors.static',
				'django.template.context_processors.tz',
				'django.contrib.messages.context_processors.messages',
				'django.template.context_processors.request',
			],
		},
	},
]