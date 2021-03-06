"""
Django settings for lab_system_backend project.

Generated by 'django-admin startproject' using Django 2.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import datetime
import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@n%2ohhob3qj+ze&k&a44y+l0_oo(ayvs_!put=s@-k6$a8mig'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# 重载使UserProfile生效
AUTH_USER_MODEL = "users.UserProfile"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'rest_framework',
    'rest_framework.authtoken',
    'xadmin',
    'crispy_forms',
    'DjangoUeditor',
    'corsheaders',
    'django_filters',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #验证登录
    # 'apps.users.middleware.AuthMiddleware',
    #验证url是否有权限
    # 'apps.users.middleware.UrlCheckMiddleware',
]

ROOT_URLCONF = 'lab_system_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'lab_system_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'labsysdb',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        "OPTIONS": {"init_command": "SET default_storage_engine=INNODB;"}
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    # os.path.join(BASE_DIR, "../lab-system-frontend/dist/static"),
]

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# drf设置
REST_FRAMEWORK = {
    # #默认的分页功能
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # #每页显示的个数
    # 'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 删除settings中的全局认证，只需要在需要的时候局部认证
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    # 限速设置： 使用示例goods/views.py GoodsListViewSet
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',   # 未登录用户
        'rest_framework.throttling.UserRateThrottle'    # 登录用户
    ),
    'DEFAULT_THROTTLE_RATES': {
        # 'anon': '3/minute',         #每分钟可以请求两次
        # 'user': '5/minute',         #每分钟可以请求五次
        'anon': '100/day',
        'user': '1000/day'
    },
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    # 访问url：localhost：8000/docs/时报错，需要添加此条配置
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
}

# 与drf的jwt相关的设置
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=6000),   # 有效时间
    'JWT_AUTH_HEADER_PREFIX': 'JWT',                         # token前缀，需要与前端保持一致
    'JWT_ALLOW_REFRESH': True,
}

AUTHENTICATION_BACKENDS = (
    # 自定义用户验证/users/views.py
    # 'users.views.CustomBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# 跨域问题django-cors-headers配置
CORS_ORIGIN_ALLOW_ALL = True
# 白名单
# CORS_ORIGIN_WHITELIST = (
#     '127.0.0.1:3000'
# )

# # 缓存设置
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "PASSWORD": "mtianyanRedisRoot"
#         }
#     }
# }

# 缓存过期时间
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 15
}

