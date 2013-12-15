#!/usr/bin/env python
# encoding: utf-8
import sys
import random
from logging import DEBUG
from twisted.internet import reactor

from logger import Logger
from mdht.mdht_node import MDHT
from config import ROOT_PATH, NODES_NUM, constants

#add project path
sys.path.append(ROOT_PATH)


def main():
    #啟動500個節點監聽請求
    num = 0
    node_id_list = []
    _port = constants.dht_port

    Logger.basicConfig(level=DEBUG)
    # Logger.basicConfig(level=DEBUG, filename=ROOT_PATH+"/log/mdht.log")

    # distribute 500 nodes
    max_node_id = long(2**160)
    piece = max_node_id/NODES_NUM
    while  num<NODES_NUM:
        node_id = random.randint(0,piece) + num*piece
        node_id_list.append(node_id)
        MDHT(node_id, bootstrap_addresses=constants.bootstrap_addresses, port=_port)
        num += 1
        _port += 1

    reactor.run()

if __name__ == "__main__":
    main()
