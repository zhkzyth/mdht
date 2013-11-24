#!/usr/bin/env python
# encoding: utf-8
"""
An interface to mdht that abstracts away Twisted details (like the reactor)
"""
from twisted.internet import reactor, defer
from twisted.python import log

from mdht import constants
from mdht.protocols.krpc_iterator import IKRPC_Iterator, KRPC_Iterator
from config import HOOK_ITERATE

class MDHT(object):

    proto = None

    def __init__(self, node_id,
                 port=constants.dht_port, bootstrap_addresses=None,
                 db=None
    ):
        """
        Prepares the MDHT client

        Note!! This function can only be called once!

        node_id: the ID under which the MDHT node will run
        port: the UDP port on which to run the MDHT node
        bootstrap_addresses: an iterable of nodes on
            which to bootstrap this MDHT client

        """
        self.node_id = node_id

        # Let Twisted know about our MDHT node listening on a UDP port
        self.proto = KRPC_Iterator(node_id)
        reactor.listenUDP(port, self.proto)

        # Patch in some functions that are found on the protocol
        self._proxy_funcs()

        # Bootstrap our freshly created node
        d = self._bootstrap(bootstrap_addresses)
        d.addCallback(self.broadcast_node, hook_iterate=HOOK_ITERATE)

    def _proxy_funcs(self):
        funcnames = filter(lambda name:
                        not (name.startswith("_") or name.endswith("Received")),
                    IKRPC_Iterator)

        for funcname in funcnames:
            log.msg(funcname)
            func = getattr(self.proto, funcname, None)
            assert func is not None
            setattr(self, funcname, func)

    def run(self):
        """
        Starts the MDHT loop

        This function will block until MDHT.halt() is called

       """
        pass

    def _bootstrap(self, addresses=constants.bootstrap_addresses):
        """
        Bootstrap the MDHT node into the DHT network

        addresses: an iterable containing tuples of hostnames/ip,port

        """
        addresses = set(addresses)

        # make ping request
        dl = []
        for hostname, port in addresses:
            d = reactor.resolve(hostname)
            d.addCallback(self.save_init_node, port)
            dl.append(d)

        return defer.DeferredList(dl)

    def ping_success(self, result):
        log.msg("ping success, and the response node is: %s" % result)
        return result

    ## TODO log the timeout,so we need to do another reconnect
    ## or change another bootstrap address
    def ping_fail(self, error):
        log.msg(repr(error))
        return None

    def save_init_node(self, ip_address=None, port=None):
        log.msg(ip_address, port)
        d = self.ping((ip_address,port))
        d.addCallbacks(self.ping_success, self.ping_fail)
        return None

    def schedule(self, delay, func, *args, **kwargs):
        """
        Run the specified function 'func' in 'delay' seconds

        delay: number of seconds to wait (float)
        func: the function to run, NOTE! this function must be nonblocking
        args: positional arguments for the function
        kwargs: keyword arguments for the function

        """
        reactor.callLater(delay, func)

    def halt(self,result):
        """
        Terminates the MDHT client

        Note!! This function can only be called once!

        """
        pass

    def get_nodes_num(self):
        """

        Return the size of our routing_table size

        """
        return len(self.proto.routing_table.nodes_dict)

    def broadcast_node(self, bootstrap_node=None, hook_iterate=HOOK_ITERATE):
        """
        broadcast node to make it better to hide in the network
        """
        d = self.find_iterate(hook_iterate)
        d.addCallback(self._broadcast_node)

    def _broadcast_node(self, nodes):
        log.msg("broadcast_node %s successful.\n and response nodes are %s.\n we need to do ping requests and save it to routing table. " % (self.node_id, nodes))
        #change format to do ping request.LOL
        for node in nodes:
            self.save_init_node(**{"ip_address": node.address[0],
                                   "port": node.address[1]})
