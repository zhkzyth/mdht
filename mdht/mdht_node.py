#!/usr/bin/env python
# encoding: utf-8
"""
An interface to mdht that abstracts away Twisted details (like the reactor)
"""
import itertools
from twisted.internet import reactor, defer
from twisted.python import log

from mdht.protocols.krpc_iterator import IKRPC_Iterator, KRPC_Iterator, IterationError
from mdht.protocols.errors import TimeoutError
from config import constants, STARTUP_RETRIES


class DropNodeError(Exception):
    """
    Error indicating a fault has occured in the find_self

    Possible reasons for this can be:
        * All regenrated node_id just not work as expected

    The reason can be accessed as a string in the 'reason' attribute

    """
    def __init__(self, reason):
        """
        @param reason: a string describing the interation error
        """
        self.reason = reason


# TODO make node more stronger
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
        # how many time we have try to do find_self request
        self.retries = 0
        # nodes we have been quired
        self.queried = set()
        # nodes that responsed for our ping request
        self.alive = set()
        self.add_live = set()
        # nodes that we will search in the next iteration
        self.response_node = set()
        # the smallest distance value in the alive nodes
        self.min_alive_dist = float("+inf")

        # retry times for domain name resolve
        self.startup_retries = 0
        # retry times for find_self
        self.find_self_retries = 0

        # index value to find a better node_id position
        # see _regenrate_id funcs below
        self.node_id_index = 0

        # Let Twisted know about our MDHT node listening on a UDP port
        self.proto = KRPC_Iterator(node_id)
        reactor.listenUDP(port, self.proto)

        # Patch in some functions that are found on the protocol
        self._proxy_funcs()

        # Bootstrap our freshly created node and join the dht network
        d = self._bootstrap(bootstrap_addresses)
        d.addCallback(self.join)

    def _proxy_funcs(self):
        funcnames = filter(lambda name:
                        not (name.startswith("_") or name.endswith("Received")),
                    IKRPC_Iterator)

        for funcname in funcnames:
            log.msg(funcname)
            func = getattr(self.proto, funcname, None)
            assert func is not None
            setattr(self, funcname, func)

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
            d.addCallback(self._ping, port)
            d.addErrback(self._logerror, hostname)
            dl.append(d)

        return defer.DeferredList(dl, consumeErrors=True)

    def _ping(self, ip, port):
        """
        try to ping seed node
        """
        self.ping((ip, port), None)

    def _logerror(self, failure, hostname):
        log.err("%s unable to be resolved." % hostname)
        return None

    def join(self, results):
        """
        join the mdht network
        """
        joined = False

        for (success, result) in results:
            if success and not joined:
                joined = True
                self.response_node = self.proto.routing_table.get_closest_nodes(self.node_id)
                self.find_self()
                return

        # opps. we need to resolve again
        if self.startup_retries < STARTUP_RETRIES:
            log.err("startup: node %s doesn't startup successfully.Do try to startup again" % self.node_id)
            self.startup_retries += 1
            reactor.callLater(0, self._bootstrap)
        else:
            log.err("------------------- give up to start node %s ------------------------" % self.node_id)

    # join mdht network
    @defer.inlineCallbacks
    def find_self(self):
        log.msg("ready to query %s nodes in this query" % len(self.response_node))

        # the next nodes will be queried in this iteration, mark them
        add_queried = set(self.response_node)
        # the all quired nodes in this search
        self.queried = self.queried.union(add_queried)

        try:
            return_nodes = yield self.search_call(add_queried)
        except IterationError:
            if self.find_self_retries == constants.find_self_retries:
                self.clear_state()
                self.do_find_self_again()
            else:
                self.find_self_retries += 1
                log.err("find_self iteration error at %s times" % self.find_self_retries)
                # update our response_node set to do a better match
                self.response_node = self.proto.routing_table.get_closest_nodes(self.node_id)
                reactor.callLater(0, self.find_self)
        else:
            # filter out nodes that has responsed
            add_live = set()
            for return_node in return_nodes:
                add_live.add(return_node[0])

            self.alive = self.alive.union(add_live)

            # Accumulate all nodes from the successful responses.
            # Calculate the relative distance to all of these nodes
            # and keep the closest nodes which has not already been
            # queried in a previous iteration
            temp_dict = []
            for return_node in return_nodes:
                temp_dict.append(return_node[1])
            all_nodes = list(itertools.chain(*temp_dict))
            new_nodes = [node for node in all_nodes if node not in self.queried]

            # the next queried nodes are the closest nodes in the responsed nodes replied
            # from node queried in this search iteration.
            new_next = [ node for node in self.get_closest_nodes(self.node_id, new_nodes, search_width=constants.search_width)]

            # TODO how we calculate the min for our nodes????
            # Check if the closest node in the work queue is closer
            # to the target than the closest responsive node that was
            # found in this iteration.
            if len(self.alive) == 0:
                min_alive_dist = float("+inf")
            else:
                min_alive_dist =  self.find_live_node_min(add_live)

            if len(new_next) == 0:
                min_queue_dist = float("+inf")
            else:
                min_queue_dist = self.find_new_next_min(new_next)

            # update self.response_node for next iteration
            self.response_node = new_next
            new_next = None

            # Check if the closest node in the work queue is closer
            # to the infohash than the closest responsive node.
            if  min_queue_dist < min_alive_dist:
                self.retries = 0
            else:
                self.retries += 1

            if self.retries == constants.search_retries:
                log.msg("++++++++++++++++++++ cheers!we just join a node.++++++++++++++++")
                self.clear_state()
            else:
                reactor.callLater(0, self.find_self)

    def do_find_self_again(self):
        """
        try to disbute our node in the brother tree.
        """
        ##TODO think out a better algorithm
        log.err("------------------------ oops!drop this node.-----------------------")
        ## for now just raise an IterationError
        raise IterationError("just drop a node to avoid CPU waste")

    ##TODO may use this algorithm for a better node distribution
    def _regenrate_id(self):
        """
        See wiki for a regenerate algorithm.
        """
        if 2**self.node_id_index > constants.piece:
            raise DropNodeError
        else:
            self.node_id_index += constants.step
            node_id = list(bin(self.node_id).lstrip("0b"))
            if node_id[self.node_id_index] == 0:
                node_id[self.node_id_index] = 1
            else:
                node_id[self.node_id_index] = 0
            self.node_id = long("".join(node_id),2)

    def find_live_node_min(self, nodes):
        sorted_list = sorted(nodes, key=(lambda node: node.distance(self.node_id)))
        new_min_dist = sorted_list[0].distance(self.node_id)
        if self.min_alive_dist < new_min_dist:
            self.min_alive_dist = new_min_dist

    def find_new_next_min(self, nodes):
        sorted_list = sorted(nodes, key=(lambda node: node.distance(self.node_id)))
        return sorted_list[0].distance(self.node_id)

    @defer.inlineCallbacks
    def search_call(self, nodes):
        # result structure like below:
        # [(success, (source_node, response_nodes),...]
        result = yield self.find_iterate(self.node_id, nodes=nodes)
        defer.returnValue(result)

    def clear_state(self):
        """
        reduce the mem use
        """
        log.msg("clear iterating state")
        self.retries = 0
        self.queried = set()
        self.alive = set()
        self.add_live = set()
        self.response_node = set()
        self.min_alive_dist = float("+inf")

    def get_closest_nodes(self, target, nodes, search_width):

        sorted(nodes, key=(lambda node: node.distance(target)))

        result = nodes[:search_width]

        return result
