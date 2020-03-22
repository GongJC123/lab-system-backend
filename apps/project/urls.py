from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'project', ProJectViewset, basename='project')
router.register(r'proapprove', ProApproveViewSet, basename='proapprove')

urlpatterns = router.urls
