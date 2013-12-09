#!/usr/bin/env python
#encoding: utf-8
from twisted.python import log
from collections import defaultdict

from mdht.database import database

class Source_Info(object):

    def __init__(self):
        self._datastore = defaultdict(set)

    def get_sources(self):
        return self._datastore

    def get(self, source_id):
        return self._datastore.get(source_id) or list()

    def add(self, source_id=None, peer=None):
        self._datastore[source_id].add(peer)

    @staticmethod
    def instance():
        """Return a global `Routing table` instance"""
        if not hasattr(Source_Info, "_instance"):
            Source_Info._instance = Source_Info()
            Source_Info._init_sources_dict()

        return Source_Info._instance

    @staticmethod
    def _init_sources_dict():
        resources_set = database["sources"].find()
        for resources in resources_set:
            peer_list = list(set([ (resource["ip"], resource["port"]) for resource in resources["peer_list"]]))
            Source_Info._instance._datastore[resources["_id"]] = peer_list

    @staticmethod
    def persist_sources_peers():
        """
        save sources info to db
        """
        if not hasattr(Source_Info, '_saved'):
            Source_Info._saved = True
            documents = []
            t_dict  = Source_Info._instance._datastore
            for target_id in t_dict:
                peer_list = []
                for peer in t_dict[target_id]:
                    peer_list.append({
                        "ip": peer[0],
                        "port": peer[1],
                    })
                documents.append({
                    "_id": str(target_id),
                    "peer_list": peer_list,
                })
            if documents:
                try:
                    ## TODO need to part update peer_list
                    database["sources"].insert(documents, continue_on_error=True)
                    log.msg("sources has saved to sources table: %s" % documents)
                except:
                    log.error("save to sources table break.")
