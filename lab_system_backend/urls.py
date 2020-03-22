"""lab_system_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework.authtoken import views
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

import xadmin
from lab_system_backend.settings import MEDIA_ROOT



urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    # 富文本编辑器
    path('ueditor/', include('DjangoUeditor.urls')),
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    path('media/<path:path>', serve, {'document_root': MEDIA_ROOT}),

    # 自动化文档
    path('docs/', include_docs_urls(title='实验室管理系统文档')),

    # rest_framework调试接口页面
    path('api-auth/', include('rest_framework.urls')),

    # drf自带的token授权登录,获取token需要向该地址post数据
    path('api-token-auth/', views.obtain_auth_token),

    # jwt的token认证接口
    path('login/', obtain_jwt_token),

    # router的path路径，view的配置的根路径
    # django运行后首页是所有api列表
    # re_path('^', include(router.urls)),

    # 首页
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    # app路由
    path('users/', include('users.urls')),

    path('projects/', include('project.urls'))

]

