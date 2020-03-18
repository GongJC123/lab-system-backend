import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from utils.base_model import BaseModel
from utils.util import deal_fields_Table


def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    # filename = '{}.{}'.format(uuid.uuid4().hex[:8], ext)
    filename = '{}.{}'.format('avatar', ext)
    return os.path.join('avatar', instance.username, filename)


class Url(models.Model):
    """
     白名单url
    """
    USER_TYPE = (
        ('customuser', '自定义用户'),
        ('anonymous', '匿名用户'),
        ('authenticated', '已认证用户'),
        # ('is_superuser', '超级管理员'),
    )
    METHOD_TYPE = [
        ('ALL', 'all'),
        ('GET', 'list/read'),
        ('POST', 'create'),
        ('PUT', 'update'),
        ('DELETE', 'delete'),
    ]
    url = models.CharField(verbose_name="URL", help_text="URL", max_length=128)
    user_type = models.CharField(verbose_name="用户类型", help_text="用户类型", max_length=16, choices=USER_TYPE,
                                 default=USER_TYPE[2])
    method = models.CharField(verbose_name='方法类型', help_text='方法类型', choices=METHOD_TYPE, max_length=10, default='ALL')
    create_time = models.DateTimeField(verbose_name='创建时间', help_text='创建时间', auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', help_text='更新时间', auto_now=True, null=True, blank=True)
    remark = models.TextField(verbose_name='备注', help_text='备注', null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.method, self.url)

    class Meta:
        unique_together = ('url', 'method',)
        verbose_name = verbose_name_plural = '白名单URL'

    @classmethod
    def get_url_by_request_url(cls, url):
        return dict(menu=Url.objects.get(url=url))

    def get_fields(self):
        """
        获取字段信息
        """
        field_dict = {}
        for field in self._meta.fields:
            field_dict[field.name] = field.verbose_name
        return field_dict

    def get_table_info(self):
        """
        获取table表
        """
        data = deal_fields_Table(self._meta.fields, True, True, 3, None, None, None)
        return data


class Role(BaseModel):
    description = models.CharField(verbose_name='角色描述', help_text='角色描述', max_length=500, blank=True)
    urls = models.ManyToManyField("Url", verbose_name="url权限", help_text='url权限', blank=True)

    class Meta:
        unique_together = ('name',)
        verbose_name = verbose_name_plural = '用户角色'

    def get_fields(self):
        """
        获取字段信息
        """
        field_dict = {}
        for field in self._meta.fields:
            field_dict[field.name] = field.verbose_name
        return field_dict

    def get_table_info(self):
        """
        获取table表
        """
        m2mField = [{"field_name": "urls", "verbose_name": "url权限", "required": False, "show": True}]
        data = deal_fields_Table(self._meta.fields, True, True, 2, m2mField, None, None)
        data['field_select_kv'].append(
            {"urls": [[row.id, row.url] for row in Url.objects.filter(user_type='customuser')]})
        data['fields']["users"] = "用户列表"
        data['field_add_novis'] = ['users','id']
        data['field_show_order'].append("users")
        return data


class UserProfile(AbstractUser):
    """
    用户表，新增字段如下
    """
    GENDER_CHOICES = (
        ("male", u"男"),
        ("female", u"女")
    )

    stuId = models.IntegerField(verbose_name='学号', help_text='学号', null=True, blank=True)

    # 用户注册时我们要新建user_profile 但是我们只有手机号
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    cname = models.CharField(verbose_name="姓名", help_text='姓名', max_length=30, null=True, blank=True)
    # 保存出生日期，年龄通过出生日期推算
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="female", verbose_name="性别")
    # mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    phone = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话", help_text="电话号码")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    last_login_ip = models.GenericIPAddressField(verbose_name='上次登录IP', help_text='上次登录IP', null=True, blank=True)
    login_count = models.IntegerField(verbose_name='登录次数', help_text='登录次数', default=0, null=True, blank=True)

    roles = models.ManyToManyField('Role', verbose_name='角色', help_text='角色', blank=True)
    avatar = ProcessedImageField(verbose_name="头像", help_text='头像', upload_to=user_avatar_path,
                                 default='avatar/default.jpg', processors=[ResizeToFill(120, 120)],
                                 format='JPEG', options={'quality': 60}, null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'cname', 'phone']


    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_fields(self):
        """
        获取字段信息
        """
        field_dict = {}
        for field in self._meta.fields:
            field_dict[field.name] = field.verbose_name
        return field_dict

    def get_table_info(self):
        """
        获取table表
        """
        m2mField = [{"field_name": "roles", "verbose_name": "角色", "required": True, "show": False}]
        force_fields = ['id', 'username', 'name', 'email', 'phone', 'roles', 'date_joined', 'is_active']
        data = deal_fields_Table(self._meta.fields, True, True, 2, m2mField, force_fields, None)
        data['field_select_kv'].append({"roles": [[row.id, row.cname] for row in Role.objects.order_by("-id")]})
        return data




