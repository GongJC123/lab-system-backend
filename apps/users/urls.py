from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'users', UsersViewSet, basename='users')
router.register(r'urls', UrlViewSet, basename='urls')
router.register(r'roles', RoleViewSet, basename='roles')

urlpatterns = router.urls