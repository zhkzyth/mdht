#!/usr/bin/env python
# encoding: utf-8
"""
persitent layer for twisted
"""
import redis
import pymongo
from twisted.python import log

from config import MONGO_SETTING, REDIS_SETTING


class MongoDb(object):

    def __init__(self, host=MONGO_SETTING['host'], port=MONGO_SETTING['port'], db=MONGO_SETTING['db']):

        connection = pymongo.Connection(host=host, port=port)
        self.db = connection[db]

    def save_routing_table(self, routing_table=None):
        """
        Datastructure:
        routing_table =[ {
                         '_id':node_id,
                         'ip':127.0.0.1,
                         'port':2031
                         },{...},...]
        """
        drop_ok = self.db["routing_table"].drop(safe=True)
        if drop_ok:
            result = self.db["routing_table"].insert(routing_table)
        else:
            log.err("drop collection routing_table error.retry?")
            result = None
        return result

    def get_routing_table(self):
        """
        return routing_table nodes list
        """
        result = self.db["routing_table"].find()
        return result

    def save_source(self, param):
        """
        datastructure:
        source = {
                  'magnet':url,
                  'node_list':[node1, node2, node3...],
                  }
        bt_source = [source1, source2, ...]
        """
        result = self.db['bt_sources'].update(param, safe=True, upsert=True)
        return result

    def get_source(self, param):
        result = self.db['bt_sources'].find_one(param)
        return result


# a cache layer
class RedisCache(object):

    def __init__(self, host=REDIS_SETTING['redis']['host'], port=REDIS_SETTING['redis']['port'], db=REDIS_SETTING['redis']['db']):
        self.r_db = redis.Connection(host=host, port=port, db=db)


# the best awesome singleton??
database = MongoDb().db
