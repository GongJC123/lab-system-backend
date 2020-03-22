from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from project.models import Project, ProApprove
from project.serializers import ProjectSerializer, ProApproveSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'pagesize'
    page_query_param = 'page'
    max_page_size = 1000


class ProJectViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list:
        项目列表
    retrieve:
        获取项目详情
    create:
        创建项目
    """
    # permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = Project.objects.all()
    pagination_class = DefaultPagination
    serializer_class = ProjectSerializer



class ProApproveViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    项目和成员对应表
    """
    queryset = ProApprove.objects.all()
    serializer_class = ProApproveSerializer






