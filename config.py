#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import inspect, os

#LOGIC constants
ROOT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

MONGO_SETTING = {
    'host': 'localhost',
    'port': 27017,
    'db': 'bt_tornado',
}

REDIS_SETTING = {
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    },
}

# nodes num for opening
NODES_NUM = 50

#
HOOK_ITERATE = long("D20E34D7C69C296B7CB7447532DF6AA4D2BE001C", 16)

# constants used by mdht lib
class constants(object):
    pass

# k as used in Kademlia
constants.k = 8

# The size of the identification number used for resources and
# nodes in the Kademlia network (bits)
constants.id_size = 160

# Time after which an RPC will timeout and fail (seconds)
constants.rpctimeout = 60

# Time after which a high level query (as used in the SimpleNodeProtocol)
# should timeout (seconds)
constants.query_timeout = 60           # 1 minute

# Quarantine timeout: time after which a node is removed from the quarantine
# (seconds)
constants.quarantine_timeout = 180    # 3 minutes

# Peer timeout
# Time after which a peer that has been announced for a torrent will be
# removed from the torrent dictionary (unless reset by being reannounced)
# (seconds)
constants.peer_timeout = 43200        # 12 hours

# Time after which a node is considered stale (seconds)
constants.node_timeout = 900         # 15 minutes

# Time between each call to the NICE routing table update algorithm (seconds)
constants.NICEinterval = 6

# This interval determines how often the DHT's state data will be
# saved into a file on disk (seconds)
constants.DUMPinterval = 3 * 60 # 3 minutes

# Size of the token (bits)
constants.tokensize = 32

# Time in seconds after which an offered token (in response to get_peers)
# will be terminated
constants.token_timeout = 60 * 10         # 10 minutes

# Transaction ID size (bits)
constants.transaction_id_size = 32

# Failcount threshold: The number of KRPCs a node can fail before being
# being remove from the routing table (int)
constants.failcount_threshold = 3

# Closeness threshold: The notion that determines whether we are close
# enough to a node to announce_peer() for example
# Number of common prefix bits (number in range 0 to 160)
#closeness_threshold = 130

# Bootstrap node
constants.bootstrap_addresses = [("67.18.187.143", 1337),
                       ("dht.transmissionbt.com", 6881),
                       ("router.utorrent.com", 6881)]

# bootstrap_addresses = [("dht.transmissionbt.com", 6881)]


# Global outgoing bandwidth limit (bytes / second)
constants.global_bandwidth_rate = 20 * 1024   # 20 kilobytes

# Outgoing bandwidth limit per host (bytes / second)
constants.host_bandwidth_rate = 5 * 1024      # 5 kilobytes


# The default port on which DHTBot will run
constants.dht_port = 6900

###
### Internal use
###

# Time for which the secret used for token
# generation is changed (this should be greater than or
# equal to the token_timeout
#
# Note: For proper functionality, token_timeout should
# be a multiple of _secret_timeout
constants._secret_timeout = 5 * 60    # 5 minutes


## search width for closest nodes
constants.search_width = 32

## search retries for iteration funcs like find_node or whatever
constants.search_retries = 4

try:
    from local_settings import *
except:
    pass
