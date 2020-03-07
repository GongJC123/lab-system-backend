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
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework.authtoken import views
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

import xadmin
from goods.views import GoodsListViewSet, CategoryViewset, BannerViewset, IndexCategoryViewset, HotSearchsViewset
from lab_system_backend.settings import MEDIA_ROOT
from user_operation.views import UserFavViewset, LeavingMessageViewset, AddressViewset
from users.views import UserViewset

router = DefaultRouter()

#配置goods的url
router.register(r'goods', GoodsListViewSet, basename='goods')

# 配置Category的url
router.register(r'categories', CategoryViewset, basename='categories')

# 配置users的url
router.register(r'users', UserViewset, basename="users")

# 配置用户收藏的url
router.register(r'userfavs', UserFavViewset, basename="userfavs")

# 配置用户留言的url
router.register(r'messages', LeavingMessageViewset, basename="messages")

# 收货地址
router.register(r'address', AddressViewset, basename="address")

# 首页banner轮播图url
router.register(r'banners', BannerViewset, basename="banners")

# 首页系列商品展示url
router.register(r'indexgoods', IndexCategoryViewset, basename="indexgoods")

# 热搜词
router.register(r'hotsearchs', HotSearchsViewset, basename="hotsearchs")

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
    re_path('^', include(router.urls)),

    # 首页
    path('index/', TemplateView.as_view(template_name='index.html'), name='index'),
]
