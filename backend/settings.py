from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Secret Key — Render environment variable se aayega ───────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-(hz8_j8o&+_gpn8zdk($7@1qqonsw+-t9qpx_2va5q(^sy+e+w'  # sirf local
)

# ── Debug — Render mein False hoga ───────────────────────────────────────────
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party
    'rest_framework',
    'corsheaders',
    # Our app
    'tannu_backend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # ← static files ke liye
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────────────
# Render par DATABASE_URL environment variable milega → PostgreSQL use hoga
# Local mein DATABASE_URL nahi hoga → SQLite use hoga
_DB_URL = os.environ.get('DATABASE_URL')
if _DB_URL:
    DATABASES = {
        'default': dj_database_url.parse(_DB_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static files — WhiteNoise serve karega ───────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Media files (uploaded certificate images) ─────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Certificate template path ─────────────────────────────────────────────────
CERTIFICATE_TEMPLATE_PATH = BASE_DIR / 'tannu_backend' / 'assets' / 'certificate_template.png'
CERTIFICATES_OUTPUT_DIR   = BASE_DIR / 'media' / 'certificates'

# ── Institute settings ────────────────────────────────────────────────────────
UDYAM_NO = os.environ.get('UDYAM_NO', 'UDYAM-GJ-XXXXXXXX')

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",           # local Vite dev server
    "http://localhost:3000",
    "https://tannu-frontend.netlify.app",  # ← tumhari Netlify site ✓
]
# Agar koi naya domain add karna ho to upar list mein add karo

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
