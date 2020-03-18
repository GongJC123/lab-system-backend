import json
import os
from random import choice

from django.contrib.auth.backends import ModelBackend
from django.core import cache
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
# 但是当第三方模块根本不知道你的user model在哪里如何导入呢
from django.contrib.auth import get_user_model
# 这个方法会去setting中找AUTH_USER_MODEL
from import_export.admin import ImportMixin, ExportMixin
from rest_framework.decorators import action
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler, JSONWebTokenSerializer

from rest_framework.response import Response
from rest_framework import mixins, permissions, authentication
from rest_framework import viewsets, status

from users.filters import UrlFilter, UsersFilter
from users.models import Role, Url
from users.resources import UserResource
from users.serializers import UserRegSerializer, UserDetailSerializer, UserUpdateSerializer, \
    AvatarSerializer, PasswordSerializer, EmailResetPasswordSerializer, ResetPasswordSerializer, \
    EmailCodeSerializer, RoleSerializer, RoleUserSerializer, UrlSerializer, UserSerializer, \
    GetUsersSerializer
from users.util import get_ip_address, login_set_cookie, logout_del_cookie
from utils.base_view import BaseGenericViewSet, BaseModelViewSet
from utils.util import Token, send_html_mail, request_get, random_char_list

from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login

User = get_user_model()
# 发送验证码是创建model中一条记录的操作
from rest_framework.mixins import CreateModelMixin
# Create your views here.


class UserViewSet(mixins.CreateModelMixin, BaseGenericViewSet):
    """
    个人中心
    """
    queryset = []

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegSerializer
        elif self.action == 'modify':
            return UserUpdateSerializer
        elif self.action == 'upload_avatar':
            return AvatarSerializer
        elif self.action == 'change_password':
            return PasswordSerializer
        elif self.action == 'email_reset_password':
            return EmailResetPasswordSerializer
        elif self.action == 'reset_password':
            return ResetPasswordSerializer
        elif self.action == 'send_email_code':
            return EmailCodeSerializer
        elif self.action == 'login':
            return JSONWebTokenSerializer
        return UserDetailSerializer

    # def get_permissions(self):
    #     action_list = ['create', 'send_sms_code', 'email_reset_password', 'reset_password', 'login', 'phone_login',
    #                    'logout', 'ssologin']
    #     if self.action in action_list: return []
    #     return super().get_permissions()

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        instance = serializer.save()

    @action(methods=['put'], detail=False)
    def modify(self, request):
        """
        修改用户信息
        """
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'status': 'ok'})

    @action(methods=['put'], detail=False)
    def change_password(self, request):
        """
        修改密码
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data["old_password"]
        password = serializer.validated_data["password"]
        if user.check_password(old_password):
            user.set_password(password)
            user.save()
            return Response({'status': 'ok'})
        else:
            return Response({'detail': ['旧密码错误']}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def email_reset_password(self, request):
        """
        通过邮箱重置密码
        """
        # todo: 此接口暂时不需要
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user_obj = User.objects.get(email=email)
            token_obj = Token()
            token = token_obj.generate_validate_token(email)
            reset_url = '{}/#/resetpwd?token={}'.format(os.environ.get('PROJECT_URL'), token)
            subject = '重置您的密码'
            content = '<br>{}，您好：<br><br>    点击以下链接重置您的密码： {} <br><br>如果您没有请求重置密码，请忽略该邮件。'.format(
                user_obj.username, reset_url)
            send_html_mail(user_obj.email, subject, content)
        except Exception as e:
            return Response({'detail': ['邮箱不存在']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'ok'})

    @action(methods=['post'], detail=False)
    def reset_password(self, request):
        """
        重置密码
        """
        # todo: 此处token为空？？？
        token = request.query_params.get('token', None)
        if token is None: return Response({'detail': ['参数错误']}, status=status.HTTP_400_BAD_REQUEST)
        token_obj = Token()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data["password"]
        try:
            email = token_obj.confirm_validate_token(token, expiration=600)
            user_obj = User.objects.get(email=email)
            user_obj.set_password(password)
            user_obj.save()
        except Exception as e:
            return Response({'detail': ['token错误']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'ok'})

    @action(methods=['get'], detail=False)
    def info(self, request):
        """
        用户详情
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def sso_user_info(self, request):
        """
        用户
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def urls(self, request):
        """
        用户有权限
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        '''
        账号密码登录
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.object.get('user') or request.user
        token = serializer.object.get('token')
        auth_login(request, user)
        # 记录登录IP、统计登录次数
        user.login_count += 1
        ip = get_ip_address(request)
        if ip:
            user.last_login_ip = ip
            user.save()
        response = Response({'username': user.username, 'token': token})
        # domain = re.search(r'(?<=\.)\w+\.\w+$', request.META['HTTP_HOST'].split(':')[0]).group()
        # response = login_set_cookie(response, token, domain=domain, logged_in=logged_in)
        response = login_set_cookie(response, token, logged_in='yes')
        return response

    @action(methods=['post'], detail=False)
    def phone_login(self, request):
        """
        手机验证码登录view.py
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        try:
            user = User.objects.get(phone=phone)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            # 记录登录IP、统计登录次数
            user.login_count += 1
            ip = get_ip_address(request)
            if ip:
                user.last_login_ip = ip
                user.save()
            # domain = re.search(r'(?<=\.)\w+\.\w+$', request.META['HTTP_HOST'].split(':')[0]).group()
            response = Response({'username': user.username, 'token': token})
            # response = login_set_cookie(response, token, domain, logged_in=logged_in)
            response = login_set_cookie(response, token, logged_in='yes')
            return response
        except Exception as e:
            return Response({"detail": e[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=False)
    def logout(self, request, *args, **kwargs):
        '''
        退出登录
        '''
        auth_logout(request)
        # domain = re.search(r'(?<=\.)\w+\.\w+$', request.META['HTTP_HOST'].split(':')[0]).group()
        redirect = request.query_params.get('redirect', '/')
        # if settings.SSO_CLIENT_ENABLE:
        #     redirect = 'http://sso.siku.cn/auth-web/?redirectUrl={}#/logout'.format(settings.PROJECT_URL)
        response = HttpResponseRedirect(redirect)
        # response = logout_del_cookie(response, domain)
        response = logout_del_cookie(response)
        #if tokenKey:
        #   sso_logout_url = 'https://flying.siku.cn/auth/login/logout?tokenKey={}'.format(tokenKey)
        #   r, err = request_get(sso_logout_url)
        #   if err: return Response({"detail": err}, status=status.HTTP_400_BAD_REQUEST)
        #response.delete_cookie('tokenKey', domain=domain)
        return response

    @action(methods=['put'], detail=False)
    def upload_avatar(self, request):
        """
        上传头像
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(self.get_object(), self.request.data)
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def send_email_code(self, request):
        """
        发送邮箱验证码
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        char_list = map(str, random_char_list(4))
        code = ''.join(char_list)
        try:
            cache.set(email, code, 3 * 60)
            subject = content = '您的验证码是: %s ,该验证码有效期3分钟, 如非本人操作请忽略此邮件!' % code
            send_html_mail(email, subject, content)
        except Exception as e:
            return Response({"detail": e[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"email": email}, status=status.HTTP_201_CREATED)




class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.order_by('-id')
    serializer_class = RoleSerializer
    ordering_fields = ('id', 'name')
    search_fields = ('name', 'cname')

    def get_serializer_class(self):
       if self.action == 'add_user' or self.action == 'remove_user' or self.action == 'add_users':
           return RoleUserSerializer
       else:
           return self.serializer_class

    @action(methods=['post'], detail=True)
    def add_user(self, request, pk):
        """
        添加用户
        """
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.data["users"]
        users = User.objects.filter(pk__in=user_ids)
        for add_user in users:
            add_user.roles.add(instance)
        return Response({'status': 'ok'})

    @action(methods=['post'], detail=True)
    def remove_user(self, request, pk):
        """
        移除用户
        """
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.data["users"]
        users = User.objects.filter(pk__in=user_ids)
        for del_user in users:
            del_user.roles.remove(instance)
        return Response({'status': 'ok'})

class UrlViewSet(BaseModelViewSet):
    queryset = Url.objects.order_by('-id')
    serializer_class = UrlSerializer
    ordering_fields = ('id', 'url')
    search_fields = ('user_type', 'url', 'method')
    filterset_class = UrlFilter


class UsersViewSet(ImportMixin, ExportMixin, BaseModelViewSet):
    # queryset = User.objects.filter(is_active=True).order_by('-id')
    queryset = User.objects.order_by('-id')
    serializer_class = UserSerializer
    ordering_fields = ('id', 'username')
    search_fields = ('username', 'cname', 'phone', 'email')
    filterset_class = UsersFilter
    resource_class = UserResource

    def get_serializer_class(self):
        if self.action == 'get_users':
            return GetUsersSerializer
        elif self.action == 'import_data':
            return self.import_data_serializer_class
        else:
            return self.serializer_class

    @action(methods=['get'], detail=False)
    def get_users(self, request):
        """
        获取用户列表，登录用户有权限,用于选择用户下拉框
        """
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(methods=['delete'], detail=True)
    def leaved(self, request, pk):
        """
        离职
        """
        instance = self.get_object()
        if instance.is_active:
            instance.username = 'leaved_{}'.format(instance.username)
            instance.email = 'leaved_{}'.format(instance.email)
            instance.roles.clear()
            instance.is_active = False
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

