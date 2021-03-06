#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: alishtory
@site: https://github.com/alishtory/xsadmin
@time: 2017/2/27 14:20
@desc: 工具类
'''
import uuid, hashlib, random
from django.db.utils import ProgrammingError
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import reverse
from django.http import HttpRequest
from django.utils.cache import get_cache_key
import logging

logger = logging.getLogger('xsadminloger')


def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()

def gen_passwd():
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',10))

def gen_val_code():
    return ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ',8))

def gen_api_key():
    return md5(uuid.uuid4().__str__())

def gen_api_secret():
    return md5(uuid.uuid4().__str__())

def gen_invite_code():
    return md5(uuid.uuid4().__str__())

def refush_node_app_keyset(node_cls = None):
    '''更新缓存中的app_key,app_secret集合
    '''
    try:
        if not node_cls:
            from .models import Node
            node_cls = Node
        nodes_info = node_cls.objects.filter(~Q(status__iexact='OUT')).values_list('api_key', 'api_secret', 'id','traffic_rate')
        nodes_dict = {}
        for node in nodes_info:
            nodes_dict[node[0]] = (node[1], node[2], node[3])
        logger.info('nodes_info is :%s' % nodes_dict)
        cache.set('node_api_key_set', nodes_dict, timeout=None)  # 永不过期的缓存
        return nodes_dict
    except ProgrammingError:
        return {}


def expire_page_cache(viewname, curreq, args=None, key_prefix=None):
    """
    Removes cache created by cache_page functionality.
    Parameters are used as they are in reverse()
    """
    if args is None:
        path = reverse(viewname)
    else:
        path = reverse(viewname, args=args)

    http_host = curreq.META.get("HTTP_HOST", "")
    if len(http_host.split(":")) == 1:
        server_name, server_port = http_host, "80"
    else:
        server_name, server_port = http_host.split(":")

    request = HttpRequest()
    request.META = {'SERVER_NAME': server_name, 'SERVER_PORT': server_port}
    request.META.update(dict((header, value) for (header, value) in
                             curreq.META.items() if header.startswith('HTTP_')))
    request.path = path
    key = get_cache_key(request, key_prefix=key_prefix)
    if key and cache.get(key):
        cache.set(key, None, 0)

if __name__ == '__main__':
    print ('md5',md5('123'))
    print('passwd',gen_passwd())
    print('val_code',gen_val_code())
    print('api_key',gen_api_key())
    print('api_secret',gen_api_secret())
    print('invite_code',gen_invite_code())