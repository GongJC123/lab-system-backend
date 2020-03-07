from random import choice

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
# 但是当第三方模块根本不知道你的user model在哪里如何导入呢
from django.contrib.auth import get_user_model
# 这个方法会去setting中找AUTH_USER_MODEL
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from rest_framework.response import Response
from rest_framework import mixins, permissions, authentication
from rest_framework import viewsets, status
from users.serializers import UserRegSerializer, UserDetailSerializer

User = get_user_model()
# 发送验证码是创建model中一条记录的操作
from rest_framework.mixins import CreateModelMixin
# Create your views here.

# todo：此方法待验证
# class CustomBackend(ModelBackend):
#     """
#     自定义用户验证规则
#     """
#     def authenticate(self, username=None, password=None, **kwargs):
#         try:
#             # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因
#             # 后期可以添加邮箱验证
#             user = User.objects.get(
#                 Q(username=username) | Q(mobile=username))
#             # django的后台中密码加密：所以不能password==password
#             # UserProfile继承的AbstractUser中有def check_password(self,
#             # raw_password):
#             if user.check_password(password):
#                 return user
#         except Exception as e:
#             return None


class UserViewset(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    # 这里需要动态选择用哪个序列化方式
    # 1.UserRegSerializer（用户注册），只返回username和mobile，会员中心页面需要显示更多字段，所以要创建一个UserDetailSerializer
    # 2.问题又来了，如果注册的使用userdetailSerializer，又会导致验证失败，所以需要动态的使用serializer
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer

    # 这里需要动态权限配置
    # 1.用户注册的时候不应该有权限限制
    # 2.当想获取用户详情信息的时候，必须登录才行
    # permission_classes = (permissions.IsAuthenticated, )
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []

        return []


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 虽然继承了Retrieve可以获取用户详情，但是并不知道用户的id，所有要重写get_object方法
    # 重写get_object方法，就知道是哪个用户了
    # 重写该方法，不管传什么id，都只返回当前用户
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()
