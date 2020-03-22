from rest_framework import serializers

from .models import Project, ProApprove


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目管理
    """

    class Meta:
        model = Project
        fields = '__all__'


class ProApproveSerializer(serializers.ModelSerializer):
    """
    审核
    """
    class Meta:
        model = ProApprove
        fields = '__all__'
