# encoding: utf-8
from django.db.models import Q
from rest_framework.validators import UniqueValidator

from utils.util import is_valid_mobile_phone, is_safe_password

import re
from users.models import Url, Role
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.cache import cache


User = get_user_model()


# todo： 修改
class UrlSerializer(serializers.ModelSerializer):
    """
    Url权限
    """
    class Meta:
        model = Url
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):

    urls = serializers.PrimaryKeyRelatedField(label="url白名单", help_text="url白名单", many=True, required=False, queryset=Url.objects.filter(user_type='customuser'))

    class Meta:
        model = Role
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['users'] = [{'id': row.id, 'username': row.username, 'cname': row.cname} for row in instance.userprofile_set.all()]
        return ret


class RoleUserSerializer(serializers.Serializer):

    users = serializers.PrimaryKeyRelatedField(label="用户", help_text="用户", many=True, queryset=User.objects.filter(is_active=True).order_by('-id'))


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情
    """
    roles = RoleSerializer(many=True)
    last_login = serializers.DateTimeField(label="最后登录时间", help_text="最后登录时间", read_only=True, format='%Y-%m-%d %H:%M:%S')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # print("instance %s" % ret)
        role_list = instance.roles.all()
        urls = Url.objects.filter(Q(user_type='customuser', role__in=role_list)|Q(user_type='authenticated'))
        urls_serializer = UrlSerializer(urls, many=True)
        ret['urls'] = urls_serializer.data
        return ret

    class Meta:
        model = User
        fields = ('id', 'username', 'cname', 'email', 'phone', 'last_login', 'last_login_ip', 'avatar', 'login_count', 'roles')
        read_only_fields = fields

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新
    """
    class Meta:
        model = User
        fields = ('cname', 'email', 'phone')

class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册
    """
    # todo: 手机验证码字段暂时需要删除？？？
    # password = serializers.CharField(style={'input_type': 'password'},help_text="密码", label="密码", write_only=True)
    sms_code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4,label="验证码",
                                 help_text="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 })

    def validate(self, attrs):
        email = attrs["email"]
        phone = attrs["phone"]
        sms_code = attrs["sms_code"]
        if not re.search('({})'.format('*'), email): raise serializers.ValidationError(
            "邮箱填写错误，只允许{}后缀的邮箱".format('*'))
        if not is_valid_mobile_phone(phone): raise serializers.ValidationError("手机号非法")
        if not cache.get(phone): raise serializers.ValidationError("验证码已过期")
        if sms_code != cache.get(phone): serializers.ValidationError("验证码错误")
        if User.objects.filter(email=email).count(): raise serializers.ValidationError("邮箱已经存在")
        if User.objects.filter(phone=phone).count(): raise serializers.ValidationError("手机号已经存在")
        username = attrs["username"] = email.split('@')[0]
        #if User.objects.filter(username=username).count(): raise serializers.ValidationError("用户名已经存在")
        del attrs["sms_code"]
        return attrs

    class Meta:
        model = User
        fields = ("email", "cname", "phone", "sms_code", "avatar")


class PasswordSerializer(serializers.Serializer):
    """
    修改密码
    """
    old_password = serializers.CharField(label="旧密码",help_text="旧密码",required=True,
                                         style={'input_type': 'password'}, trim_whitespace=False)
    password = serializers.CharField(label='新密码',help_text="新密码", required=True,
                                         style={'input_type': 'password'},trim_whitespace=False)
    confirm_password = serializers.CharField(label='确认密码',help_text="确认密码", required=True,
                                             style={'input_type': 'password'},trim_whitespace=False)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password: raise serializers.ValidationError("二次密码不相同")
        if password == old_password: raise serializers.ValidationError("新密码和旧密码相同")
        if not is_safe_password(password): raise serializers.ValidationError("密码安全强度不符合，密码要求包含大小写字母和数字,密码长度至少8位")
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    重置密码
    """
    password = serializers.CharField(label='新密码',help_text="新密码", required=True,
                                         style={'input_type': 'password'},trim_whitespace=False)
    confirm_password = serializers.CharField(label='确认密码',help_text="确认密码", required=True,
                                             style={'input_type': 'password'},trim_whitespace=False)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password: raise serializers.ValidationError("二次密码不相同")
        if not is_safe_password(password): raise serializers.ValidationError("密码安全强度不符合，密码要求包含大小写字母和数字,密码长度至少8位")
        return attrs


class EmailResetPasswordSerializer(serializers.Serializer):
    """
    邮箱重置密码
    """
    email = serializers.EmailField(label="邮箱", help_text="邮箱", required=True)


class AvatarSerializer(serializers.ModelSerializer):
    """
    上传头像
    """
    class Meta:
        model = User
        fields = ("avatar",)


class EmailCodeSerializer(serializers.Serializer):
    """
    邮箱验证码
    """
    def validate_email(self, email):
        """
        验证邮箱
        """
        # 是否注册
        if User.objects.filter(email=email).count(): raise serializers.ValidationError("邮箱已经存在")
        # 发送频率
        if cache.get(email): raise serializers.ValidationError("上一次发送的验证码未过期")
        return email


class UserSerializer(serializers.ModelSerializer):
    """
    用户
    """
    def validate(self, attrs):
        username = attrs["username"]
        email = attrs["email"]
        phone = attrs["phone"]
        if not re.search('({})'.format('*'), email): raise serializers.ValidationError(
            "邮箱填写错误，只允许{}后缀的邮箱".format('*'))
        if not is_valid_mobile_phone(phone): raise serializers.ValidationError("手机号非法")
        if User.objects.filter(email=email).exclude(username=username).count(): raise serializers.ValidationError("邮箱已经存在")
        return attrs

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'cname', 'phone', 'roles', 'date_joined', 'is_active')
        #read_only_fields = ['date_joined']

class GetUsersSerializer(serializers.ModelSerializer):
    """
    用户
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'cname')
