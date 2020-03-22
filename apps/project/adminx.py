# encoding: utf-8

import xadmin
from xadmin import views
from .models import *


class ProjectAdmin(object):
    list_display = ["name", "leader", "date"]


class ProApproveAdmin(object):
    list_display = ["project", "user", "status"]


xadmin.site.register(Project, ProjectAdmin)
xadmin.site.register(ProApprove, ProApproveAdmin)
