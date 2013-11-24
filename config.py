#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import inspect, os

ROOT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

MONGO_SETTING = {
    'host': 'localhost',
    'port': 27017,
    'db': 'test',
}

REDIS_SETTING = {
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    },
}

ROUTING_TIME = 30# per second

HOOK_ITERATE = long("D20E34D7C69C296B7CB7447532DF6AA4D2BE001C", 16)

try:
    from local_settings import *
except:
    pass
