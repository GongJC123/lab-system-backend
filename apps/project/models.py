from django.db import models

from users.models import UserProfile


class Project(models.Model):
    '''项目团队'''
    name = models.CharField('项目名称', max_length=128)
    introduction = models.TextField('项目介绍', blank=True)
    users = models.ManyToManyField(UserProfile, verbose_name='项目成员', blank=True, through='ProApprove') #反查参加的项目
    is_full = models.BooleanField('人员名额已满', default=False)
    is_finish = models.BooleanField('已完成', default=False)
    plan = models.IntegerField('进度', default=0)
    date = models.DateTimeField('创建时间', auto_now_add=True)
    start_t = models.DateField('开始时间', blank=True, null=True)
    end_t = models.DateField('结束时间', blank=True, null=True)
    leader = models.ForeignKey(UserProfile, verbose_name='项目负责人', on_delete=models.CASCADE, blank=True, null=True, related_name='lead_project')
    is_active = models.BooleanField('激活状态', default=True) #是否显示，删除直接讲这个字段改为false

    class Meta:
        ordering = ['-date']
        verbose_name = '项目信息'
        verbose_name_plural = '项目信息'
        permissions = (
            ("apply_project", "可以申请项目"),
        )

    @property
    def member_num(self):
        return self.users.count() #返回团队的总人数

    @property
    def teachers(self):
        users = self.users.all()
        return [user for user in users if user.role == 'teacher']

    @property
    def students(self):
        users = self.users.all()
        return [user for user in users if user.role == 'student']

    @property
    def money(self):
        finds = self.finding_set.all()
        return sum([find.num for find in finds])

    def __str__(self):
        return self.name


class ProApprove(models.Model):
    """
    审核状态
    """
    project = models.ForeignKey(Project, verbose_name='项目', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(UserProfile, verbose_name='成员', on_delete=models.CASCADE)
    status = models.IntegerField('状态', default=2, choices=((0, u'不通过'), (1, u'通过'), (2, u'等待'),))

    class Meta:
        verbose_name_plural = verbose_name = '审核状态'