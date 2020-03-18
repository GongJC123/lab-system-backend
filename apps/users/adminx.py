# encoding: utf-8

import xadmin
from xadmin import views
from .models import *


class RoleAdmin(object):
    list_display = ["name", "cname","create_time"]


class UrlAdmin(object):
    list_display = ["user_type", "url", "method"]


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "实验室管理系统"
    site_footer = "labsys@labsys"
    # menu_style = "accordion"


xadmin.site.register(Role, RoleAdmin)
xadmin.site.register(Url, UrlAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)