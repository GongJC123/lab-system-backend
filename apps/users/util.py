# -*- coding: utf-8 -*-
#  工具类
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from ipware import get_client_ip

def get_ip_address(request):
    """
    返回request里的IP地址
    提示：
        为了开发方便，这个函数会返回类似127.0.0.1之类无法在公网被路由的地址，
        在生产环境中，类似地址不会被返回
    """
    ip, is_routable = get_client_ip(request)
    if settings.DEBUG:
        return ip
    else:
        if ip is not None and is_routable:
            return ip
    return None

def login_set_cookie(response, token, domain=None, logged_in='no'):
    response.set_cookie('logged_in', logged_in, max_age=api_settings.JWT_EXPIRATION_DELTA.total_seconds(),domain=domain)
    response.set_cookie('Ssotoken', token, max_age=api_settings.JWT_EXPIRATION_DELTA.total_seconds(),domain=domain)
    response.set_cookie('token_name', 'Ssotoken', max_age=api_settings.JWT_EXPIRATION_DELTA.total_seconds(),domain=domain)
    return response

def logout_del_cookie(response, domain=None):
    response.delete_cookie('logged_in', domain=domain)
    response.delete_cookie('Ssotoken', domain=domain)
    response.delete_cookie('token_name', domain=domain)
    return response
