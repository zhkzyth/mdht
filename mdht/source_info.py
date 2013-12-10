#!/usr/bin/env python
#encoding: utf-8
from pymongo.errors import OperationFailure, DuplicateKeyError
from twisted.python import log

from mdht.database import database

class Source_Info(object):

    def __init__(self):
        self._datastore  = database["sources"]

    def get(self, source_id):
        result = self._datastore.find_one({"_id":str(source_id)})
        if result:
            peer_list = result["peer_list"]
        else:
            peer_list = list()
        return peer_list

    def add(self, source_id=None, peer=None):
        try:
            self._datastore.update({"_id":str(source_id)}, {"$addToSet":{"peer_list":peer}}, upsert=True)
        except (OperationFailure, DuplicateKeyError):
            log.error("can not add peer to peer_list.")
            return False
        return True

    @staticmethod
    def instance():
        """Return a global `Routing table` instance"""
        if not hasattr(Source_Info, "_instance"):
            Source_Info._instance = Source_Info()

        return Source_Info._instance
