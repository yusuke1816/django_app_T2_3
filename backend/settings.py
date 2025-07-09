from pathlib import Path
from dotenv import load_dotenv
CORS_ALLOW_ALL_ORIGINS = True

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@gyghje2co6=7^tv@$7!r(@nd4003#q!744-()b9sd_g$#mq6@'
load_dotenv() 
DEBUG = True


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # これを一番上に
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'money-manager-ceec.onrender.com',  # ←これを追加！
    'django-app-t2-3.onrender.com',
    
]

# アプリケーション定義
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
  

    # 追加アプリ
    'rest_framework',
    'corsheaders',
    'main',
  
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


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

# データベース
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'money_manager_app',
#         'USER': 'tamurayusuke',
#         'PASSWORD': '',
#         'HOST': 'localhost',  # 本番なら DB のホスト名やURL
#         'PORT': '5432',
#     }
# }



import os
import dj_database_url
from decouple import config





from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moneyed',
        'USER': 'moneyed_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),  # 環境変数
        'HOST': 'dpg-d1n27kjuibrs73e283f0-a.oregon-postgres.render.com',
        'PORT': '5432',
        'OPTIONS': {
             'sslmode': 'require',
        },
    }
}

# settings.py
LANGUAGE_CODE = 'ja'

# タイムゾーンも日本にするのが一般的です
TIME_ZONE = 'Asia/Tokyo'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'money_manager_app',
#         'USER': 'money_manager_app_user',
#         'PASSWORD': os.environ.get('DB_PASSWORD'),  # 環境変数で管理推奨
#         'HOST': 'dpg-d1m1ij7diees738vp1rg-a.oregon-postgres.render.com',
#         'PORT': '5432',
#         'OPTIONS': {
#             'sslmode': 'require',  # これを追加
#         },
#     }
# }

BASE_DIR = Path(__file__).resolve().parent.parent

# 省略

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # ← 追加してください
# パスワードバリデーション
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

# 静的ファイル
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 追加: React連携用 ---
# CORS設定：フロントエンドのURLを許可
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.3.6:3000",
    "http://localhost:3000",
    "http://10.41.190.13:3000",  # 追加する
    "https://money-manager-ceec.onrender.com",
    "https://django-app-t2-3z-frontend.vercel.app",
    "https://money-manager-ceec.vercel.app",
    "http://10.96.31.30:3000",
    "https://django-app-t2-3.onrender.com"
]

from corsheaders.defaults import default_headers

# 開発中は全部許可もOK（セキュリティ注意）
# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
    'content-type',
]