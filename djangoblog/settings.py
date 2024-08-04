"""
Django settings for djangoblog project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import os
import sys
from django.utils.translation import gettext_lazy as _


# _("name") 将会被翻译成用户界面语言中的 "名字" 或者等效的词汇，
# 但这个翻译会在实际渲染模型字段或其帮助文本时才发生，而不是在模块加载时
# gettext_lazy 的工作原理是在第一次访问时执行实际的翻译，然后缓存结果，
# 以便后续访问时直接使用缓存的翻译结果。这有助于提高性能，避免每次访问时都重新执行翻译操作


def env_to_bool(env, default):
    """
    将环境变量的值转换为布尔值。

    该函数旨在处理环境变量的字符串值，并根据该值的是否存在及其内容，将其转换为Python布尔值。
    如果环境变量不存在，或者其值不是'True'（不区分大小写），则返回默认值。

    参数:
    - env (str): 环境变量的名称。
    - default (bool): 如果环境变量不存在或其值不是'True'时的默认布尔值。

    返回:
    - bool: 环境变量的布尔值或默认值。
    """
    # 从环境变量中获取字符串值，如果环境变量不存在，则返回None
    # Windows中: $Env:DJANGO_MYSQL_DATABASE = 'bolg'
    # Linux中: export DJANGO_MYSQL_DATABASE = 'bolg'
    # 在终端环境中设置环境变量，即可在os.environ.get(env)中进行获取到配置数据
    # 可使用单个脚本文件将配置数据写入环境变量中然后在执行项目
    str_val = os.environ.get(env)
    # 如果环境变量值为None，返回默认值；否则，检查其是否为'True'（不区分大小写）
    return default if str_val is None else str_val.lower() == 'true'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# 获取当前文件的绝对路径, 依次获取绝对路径的父级路径
# 相当于:
# from pathlib import Path
# BASE_DIR_ANO = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

"""
print("BASE_DIR: %s" % BASE_DIR)
print("BASE_DIR_ANO: %s" % BASE_DIR_ANO)
print("======================================")
print(Path(__file__))
print(Path(__file__).resolve())
print(Path(__file__).resolve().parent)
print("======================================")
"""

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY') or 'n9ceqv38)#&mwuat@(mjb_p%em$e8$qyr#fw9ot!=ba6lijx-6'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_to_bool('DJANGO_DEBUG', True)
# DEBUG = False
"""
数据库设置：
Django会使用DATABASES['default']['TEST']中的设置来创建一个测试数据库。这通常是与生产或开发数据库隔离的，以防止测试对实际数据造成影响。
在测试开始前，Django会创建一个测试数据库；在测试结束后，会删除这个数据库，确保测试的隔离性。
在DATABASES中设置
'TEST': {
       'NAME': 'mydatabase_test',
   },
静态文件和媒体文件：
Django可能会禁用静态文件和媒体文件的收集和处理，因为在测试中通常不需要这些功能。
邮件发送：
测试模式下，Django可能不会真正发送电子邮件，而是将邮件信息存储起来供测试检查。
缓存：
测试模式可能使用一个简单的内存缓存，而不是生产环境中的缓存后端，以避免测试之间的缓存污染。
模板渲染：
Django可能使用更快的模板引擎设置，如禁用模板缓存，以加快测试速度。
中间件：
可能会有一些中间件在测试模式下被禁用，特别是那些依赖于生产环境才需要的功能。
信号：
Django可能禁用一些信号处理器，以避免不必要的副作用。
性能优化：
在测试模式下，Django可能会禁用一些耗时的操作，如模型字段的验证，以加速测试运行。
日志记录：
日志级别可能会调整，以减少测试期间的日志输出。
安全性：
一些安全相关的设置可能会暂时放宽，例如CSRF保护，通常不推荐，除非有特定的测试需求。
"""
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*', '127.0.0.1', 'example.com']

"""
当用户提交表单时，服务器会检查请求的来源是否在可信列表中，以确保请求的合法性。
只有来自 'http://example.com' 的请求会被视为可信
通常用于跨站请求伪造（CSRF）保护
但此种为白名单机制，可在中间件中自定义黑名单机制

class OriginBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # 黑名单设置
        self.blacklisted_origins = {'http://bad.example.com'}

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        if origin in self.blacklisted_origins:
            # 如果来源在黑名单中，返回403错误
            return HttpResponseForbidden('Your origin is blacklisted.')
        response = self.get_response(request)
        return response

"""
# django 4.0新增配置
CSRF_TRUSTED_ORIGINS = ['http://example.com']
# Application definition

"""
注册 django.contrib.admin 的影响：
启用完整的Django Admin站点。
自动为你的模型生成管理界面。
包含Admin站点的所有静态文件和模板。
提供标准的登录页面、索引页面、以及模型列表和详情页面。

注册 SimpleAdminConfig 的影响：
只注册Admin应用的核心部分，即模型注册和管理功能。
不包含Admin站点的标准模板和静态文件。
你必须自己处理Admin站点的外观和行为，例如，使用自定义模板和静态资源。
"""
INSTALLED_APPS = [
    # 启用整个Django Admin应用，包括其所有特性、模板、静态文件、以及对模型的自动管理界面
    # 'django.contrib.admin',
    # 更轻量级的配置选项，它主要用来注册Django Admin应用的基本部分，但不包含那些额外的特性，如模板和静态文件的加载路径
    'django.contrib.admin.apps.SimpleAdminConfig',
    # 作用：提供了用户认证和授权的功能，包括用户账户、密码管理、会话管理和权限系统。
    # 影响：使你能够轻松地添加用户登录、注销、权限检查等功能到你的应用中。
    'django.contrib.auth',
    # 作用：允许模型之间的通用关系，例如标签或注释，而不必知道具体的模型类型。
    # 影响：可以让你在不同类型的模型上使用相同的通用字段和方法，比如评论或评分。
    'django.contrib.contenttypes',
    # 作用：实现了会话框架，用于保存用户的临时数据，比如购物车中的商品或用户偏好。
    # 影响：使得在用户的不同请求之间保持状态成为可能。
    'django.contrib.sessions',
    # 作用：提供了一种存储和检索非持久性消息的框架，用于向用户显示临时反馈信息。
    # 影响：可以向用户显示警告、成功或其他类型的临时通知。
    'django.contrib.messages',
    # 作用：处理静态文件的收集和提供，如CSS、JavaScript和图像文件。
    # 影响：简化了在开发和部署环境中管理静态资产的过程。
    'django.contrib.staticfiles',
    # 作用：允许你在同一Django实例中运行多个网站，并为每个网站提供独立的配置。
    # 影响：对于多租户或多域名应用非常有用。
    'django.contrib.sites',
    # 作用：帮助生成站点地图XML文件，用于搜索引擎优化，便于爬虫抓取网站内容。
    # 影响：改善了搜索引擎对网站的索引效果，有助于提高网站的可见性和SEO排名。
    'django.contrib.sitemaps',
    # Markdown编辑器插件，用于在Django应用中集成Markdown编辑功能。它提供了一个富文本编辑器，用户可以使用Markdown语法输入文本，同时提供实时预览功能
    'mdeditor',
    # 用于在Django项目中实现全文搜索功能的库。它支持多种搜索引擎，如Elasticsearch、Solr、Whoosh等，为开发者提供了一个统一的API来处理搜索功能
    'haystack',
    # 用于压缩和合并前端资源，如CSS和JavaScript文件。它可以提高网站性能，减少网络传输时间和加载时间，特别是在大型项目中，可以有效管理多个静态文件
    'compressor',
    # 自定义应用
    'blog.apps.BlogConfig',
    'accounts.apps.AccountsConfig',
    'comments.apps.CommentsConfig',
    'oauth.apps.OauthConfig',
    'servermanager.apps.ServermanagerConfig',
    'owntracks.apps.OwntracksConfig',
]
# 按照列表中的顺序依次执行
MIDDLEWARE = [
    # 提供安全相关的功能，如设置安全的HTTP头部，如X-Content-Type-Options、X-XSS-Protection和X-Frame-Options，以及阻止不安全的HTTP方法
    'django.middleware.security.SecurityMiddleware',
    # 管理会话数据，允许你跟踪用户状态，如登录状态，从一个页面到另一个页面
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 根据用户的浏览器设置或用户的偏好选择正确的语言环境。
    'django.middleware.locale.LocaleMiddleware',  #
    # 对响应内容进行gzip压缩，减少传输的数据量，提高网页加载速度。
    'django.middleware.gzip.GZipMiddleware',  #
    # 'django.middleware.cache.UpdateCacheMiddleware',  # 在响应生成后更新缓存
    # 提供一些常见的功能，如处理Etag、Last-Modified头信息，以及实现条件GET请求。
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',  # 尝试从缓存中获取响应，以减少数据库查询
    # 将用户认证信息添加到请求中，使得视图可以访问request.user
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 实现跨站请求伪造（CSRF）保护，防止恶意网站通过用户浏览器发起的未经用户同意的请求
    'django.middleware.csrf.CsrfViewMiddleware',
    # 提供消息框架，允许你存储消息并在后续请求中显示它们，通常用于向用户展示一次性通知
    'django.contrib.messages.middleware.MessageMiddleware',
    # 设置X-Frame-Options头，防止点击劫持攻击，控制页面是否可以在<frame>、<iframe>等标签中显示
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 实现HTTP条件GET请求，如果资源未改变，则返回304 Not Modified响应，节省带宽
    'django.middleware.http.ConditionalGetMiddleware',  #
    # 这个中间件可能用于追踪在线用户，例如记录用户访问时间和活跃状态。
    'blog.middleware.OnlineMiddleware'  #
]

ROOT_URLCONF = 'djangoblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 添加一个布尔值 debug 到上下文中，表示当前是否处于调试模式
                'django.template.context_processors.debug',
                # 把整个 HttpRequest 对象添加到上下文中，使得模板可以直接访问请求对象
                'django.template.context_processors.request',
                # 添加与认证相关的信息，如用户是否登录、权限等
                'django.contrib.auth.context_processors.auth',
                # 添加消息框架中的消息到上下文中，用于在模板中显示一次性通知
                'django.contrib.messages.context_processors.messages',
                # 自定义的上下文处理器，添加 SEO 相关的数据，比如网站标题、描述等
                'blog.context_processors.seo_processor'  #
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoblog.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DJANGO_MYSQL_DATABASE') or 'blog',
        'USER': os.environ.get('DJANGO_MYSQL_USER') or 'root',
        'PASSWORD': os.environ.get('DJANGO_MYSQL_PASSWORD') or '12345678',
        'HOST': os.environ.get('DJANGO_MYSQL_HOST') or '127.0.0.1',
        'PORT': int(
            os.environ.get('DJANGO_MYSQL_PORT') or 3306),
        'OPTIONS': {
            'charset': 'utf8mb3'},
        'TEST': {
            'NAME': 'blogtest',
        },
    }}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

"""
多语言支持：它允许Django识别并处理多种语言版本的文本，这对于国际化（i18n）和本地化（l10n）非常重要。
管理界面和前端界面的语言切换：Django的管理后台和其他界面可以根据这个设置动态切换显示的语言。
URL中的语言前缀：如果你使用了Django的i18n_patterns来处理URL，那么LANGUAGES定义了哪些语言前缀会被接受。
翻译系统：当你使用Django的翻译框架时，如gettext，LANGUAGES告诉系统应该为哪些语言生成翻译文件
"""
LANGUAGES = (
    ('en', _('English')),
    ('zh-hans', _('Simplified Chinese')),
    ('zh-hant', _('Traditional Chinese')),
)

# 本地化语言文件存放地址
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

# 国际化（i18n）和本地化（l10n）
USE_I18N = True

USE_L10N = True

USE_TZ = True


# ELASTICSEARCH_DSL = {
#     'default': {
#         'hosts': '127.0.0.1:9200',
#     },
# }
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# 用于配置搜索引擎的连接信息。其中 'default' 是连接的名称，'ENGINE' 是搜索引擎的类路径，'PATH' 是搜索索引的存储路径
HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'djangoblog.whoosh_cn_backend.WhooshEngine',
            'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
        },
}

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'djangoblog.elasticsearch_backend.ElasticSearchEngine',
#         'URL': 'http://localhost:9200/',
#         'INDEX_NAME': 'haystackTest',
#         'TIMEOUT': 60,
#     },
# }

# Automatically update searching index
# 用于配置信号处理器的类路径。这里配置的是实时信号处理器，可以实现在模型发生变化时自动更新搜索索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# Allow user login with username and password
# 用于配置认证后端。这里配置的是一个自定义的认证后端，允许用户使用用户名或电子邮件地址进行登录认证
AUTHENTICATION_BACKENDS = [
    'accounts.user_login_backend.EmailOrUsernameModelBackend']

STATIC_ROOT = os.path.join(BASE_DIR, 'collectedstatic')

STATIC_URL = '/static/'
STATICFILES = os.path.join(BASE_DIR, 'static')

AUTH_USER_MODEL = 'accounts.BlogUser'
LOGIN_URL = '/login/'

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_TIME_FORMAT = '%Y-%m-%d'

# bootstrap color styles
BOOTSTRAP_COLOR_TYPES = [
    'default', 'primary', 'success', 'info', 'warning', 'danger'
]

# paginate 分页的页大小为10
PAGINATE_BY = 10
# http cache timeout HTTP缓存的最长有效期为2592000秒（30天）
CACHE_CONTROL_MAX_AGE = 2592000
# cache setting
# 缓存配置。其中，'default'键指定了默认的缓存后端为django.core.cache.backends.locmem.LocMemCache，
# 超时时间为10800秒（3小时），位置为'unique-snowflake'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 10800,
        'LOCATION': 'unique-snowflake',
    }
}
# 使用redis作为缓存
DJANGO_REDIS_URL = 'redis://:@localhost:6379/0'
# if os.environ.get("DJANGO_REDIS_URL"):
#     CACHES = {
#         'default': {
#             'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#             'LOCATION': f'redis://{os.environ.get("DJANGO_REDIS_URL")}',
#         }
#     }
#
# if DJANGO_REDIS_URL:
#     CACHES = {
#         'default': {
#             'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#             'LOCATION': DJANGO_REDIS_URL,
#         }
#     }

"""
这个URL是用于向百度搜索引擎主动推送网站更新信息的接口地址。具体来说：
http://data.zz.baidu.com/urls 是百度站长平台提供的链接提交API的入口。
site=https://www.lylinux.net 参数指定了网站的域名，这里是https://www.lylinux.net，百度会将接收到的链接与这个域名关联起来。
token=1uAOGrMsUm5syDGn 是百度为特定网站生成的一个验证令牌，用于证明推送链接请求的合法性。每个网站的令牌都是唯一的，需要在百度站长工具中注册并获取。
当你的网站有新的内容发布时，通过调用这个URL，可以将新发布的网页URL提交给百度，加速百度对该页面的抓取和索引，从而提高网站在百度搜索结果中的可见性。
这种方式特别适用于那些希望快速被搜索引擎收录的新建站点或更新频繁的站点。
"""
SITE_ID = 1
BAIDU_NOTIFY_URL = os.environ.get('DJANGO_BAIDU_NOTIFY_URL') \
                   or 'http://data.zz.baidu.com/urls?site=https://www.lylinux.net&token=1uAOGrMsUm5syDGn'

# Email:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = env_to_bool('DJANGO_EMAIL_TLS', False)
EMAIL_USE_SSL = env_to_bool('DJANGO_EMAIL_SSL', True)
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST') or 'smtp.qq.com'
EMAIL_PORT = int(os.environ.get('DJANGO_EMAIL_PORT') or 465)
EMAIL_HOST_USER = '1303625378@qq.com'  #os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = 'pteunvxgdluthdfi'  #os.environ.get('DJANGO_EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
# Setting debug=false did NOT handle except email notifications
ADMINS = [('admin', os.environ.get('DJANGO_ADMIN_EMAIL') or '1303625378@qq.com')]
# WX ADMIN password(Two times md5)
WXADMIN = os.environ.get(
    'DJANGO_WXADMIN_PASSWORD') or '995F03AC401D6CABABAEF756FC4D43C7'

LOG_PATH = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)
LOGGING_CONFIG = 'logging.config.dictConfig'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'log_file'],
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d %(module)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'djangoblog.log'),
            'when': 'D',
            'formatter': 'verbose',
            'interval': 1,
            'delay': True,
            'backupCount': 5,
            'encoding': 'utf-8'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'djangoblog': {
            'handlers': ['log_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

STATICFILES_FINDERS = (
    # 按照指定的路径列表，从文件系统中查找静态文件
    'django.contrib.staticfiles.finders.FileSystemFinder',
    # 在每个Django应用的static目录下查找静态文件
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other 用于找到需要进行压缩和合并的静态文件，并对其进行处理
    'compressor.finders.CompressorFinder',
)
COMPRESS_ENABLED = True  # 对静态文件进行压缩和优化。这包括去除不必要的空白符、注释以及可能的其他优化措施，以减少文件大小，从而提高网页加载速度
# COMPRESS_OFFLINE = True  # 静态文件会被提前压缩并存储在磁盘上，之后直接提供给客户端，而无需在服务器端进行实时压缩
# 配置一个额外的文件来记录压缩后的文件映射，例如COMPRESS_OFFLINE_MANIFEST


COMPRESS_CSS_FILTERS = [
    # creates absolute urls from relative ones
    'compressor.filters.css_default.CssAbsoluteFilter',
    # css minimizer
    'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter'
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/media/'
# 用于指示浏览器是否允许页面被嵌入到其他站点的框架中。
# 'SAMEORIGIN'值表示只允许页面在同源的页面中被嵌入，
# 即页面的URL协议、域名和端口必须与包含它的页面完全相同。
# 这样可以防止点击劫持攻击，增加安全性
X_FRAME_OPTIONS = 'SAMEORIGIN'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
