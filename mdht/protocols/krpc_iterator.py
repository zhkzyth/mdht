#!/usr/bin/env python
# encoding: utf-8
"""
@author Greg Skoczek

Module containing an iterative KRPC protocol along with auxilary classes

"""
from zope.interface import implements
from twisted.internet import defer
from twisted.python import log

from mdht.protocols.krpc_responder import KRPC_Responder, IKRPC_Responder
from mdht.protocols.errors import TimeoutError, KRPCError


class IterationError(Exception):
    """
    Error indicating a fault has occured in the KRPC_Iterator

    Possible reasons for this can be:
        * There are no nodes in the routing table and no nodes
            were provided as arguments into the iterator
        * All outbound queries timed out

    The reason can be accessed as a string in the 'reason' attribute

    """
    def __init__(self, reason):
        """
        @param reason: a string describing the interation error
        """
        self.reason = reason


class IKRPC_Iterator(IKRPC_Responder):
    """
    KRPC_Iterator abstracts the practice of iterating toward a target ID

    """
    def __init__(self, node_id=None):
        """
        Construct a KRPC_Iterator

        @arg node_id: The ID under which this KRPC_Iterator
            will contact the network

        """

    def find_iterate(self, target_id, nodes=None, timeout=None):
        """
        Run a find_node query on every node in a list and return the new nodes

        This function will send a find_node query to a collection of nodes.
        After all queries have either returned a response or timed out,
        all newly found nodes will be returned in a
        deferred callback. If nodes are supplied as an argument,
        no nodes will be taken from the routing table.

        @param nodes: the nodes to start the iteration from (if no nodes
            are provided, nodes will be taken from the routing table)
            This should be an iterable.
        @param timeout: @see the arguments to KRPC_Responder.timeout
        @returns a deferred that fires its callback with a set of
            all newly discovered nodes. The errback is fired with
            an IterationError if an error occurs in the iteration process.

        @see IterationError

        """

    def get_iterate(self, target_id, nodes=None, timeout=None):
        """
        Run a get_peers query on every node in a list and return new nodes/peers

        This function will send a get_peers query to a collection of nodes.
        After all queries have either returned a response or timed out,
        all newly found nodes and peers will be returned in a
        deferred callback. If nodes are supplied as an argument,
        no nodes will be taken from the routing table.

        @param nodes: the nodes to start the iteration from (if no nodes
            are provided, nodes will be taken from the routing table)
            This should be an iterable.
        @param timeout: @see the arguments to KRPC_Responder.timeout
        @returns a deferred that fires its callback with a tuple (peers, nodes)
            where
                peers: a set of all newly discovered peers (if any)
                nodes: a set of all newly discovered nodes (if the queried
                    node did not have any peers, it returns nodes instead)
            The errback is fired with an IterationError if an error occurs
            in the iteration process.

        @see IterationError

        """


class KRPC_Iterator(KRPC_Responder):

    implements(IKRPC_Iterator)

    def __init__(self, node_id=None, _reactor=None):
        KRPC_Responder.__init__(self, node_id=node_id, _reactor=_reactor)

    def find_iterate(self, target_id, nodes=None, timeout=None):
        d = self._iterate(self.find_node, target_id, nodes)
        d.addCallback(lambda (nodes, peers): nodes)
        return d

    def get_iterate(self, target_id, nodes=None, timeout=None):
        #TODO not yet test
        d = self._iterate(self.get_peers, target_id, nodes)
        return d

    def _iterate(self, iterate_func, target_id, nodes=None, timeout=None):
        # Prepare the seed nodes
        if nodes is None:
            # If no nodes are supplied, we have to
            # get some from the routing table
            seed_nodes = self.routing_table.get_closest_nodes(target_id)
            if len(seed_nodes) == 0:
                return defer.fail(
                    IterationError("No nodes were supplied and no nodes "
                                   + "were found in the routing table"))
        else:
            seed_nodes = nodes

        log.msg("do one iteration to %s" % target_id)
        # Don't send duplicate queries
        seed_nodes = set(seed_nodes)

        # Send a query to each node and collect all
        # the deferred results
        deferreds = []
        for node in seed_nodes:
            d = iterate_func(node.address, target_id, timeout)
            if iterate_func == self.find_node:
                d.addCallback(self._reconsturct_data, node)
                d.addErrback(self._logerror)
            deferreds.append(d)

        # Create a meta-object that fires when
        # all deferred results fire
        # and set consumeErrors to True cause iterate_func timeout
        # error is ok.
        dl = defer.DeferredList(deferreds, consumeErrors=True)
        # Make sure at least one query succeeds
        # and collect the resulting nodes/peers
        dl.addCallback(self._check_query_success_callback)
        dl.addCallback(self._collect_nodes_and_peers_callback)
        return dl

    def _reconsturct_data(self, result, seed_node):
        """
        Get result nodes from find_node search,
        and we do some reconstruction to be with seed_node.
        """
        # TODO in case of getting a None
        nodes = result.nodes or []
        result.nodes = (seed_node, nodes)
        return result

    def _logerror(self, failure):
        ## BUG?
        log.msg("find_node timeout")
        return failure

    def _check_query_success_callback(self, results):
        """
        Ensure that atleast one outbound query succeeded

        Throw an IterationError otherwise

        """
        for (success, result) in results:
            # If atleast one succeeded, we will
            # not throw an exception, so we can
            # pass the results on for further processing
            if success:
                return results
        # It is erroneous behavior for all of the
        # queries to have failed (Let the user know)
        raise IterationError("All outbound queries timed out")

    def _collect_nodes_and_peers_callback(self, results):
        """
        Extract all the nodes/peers from the query results

        @returns a tuple of iterables (new_nodes, new_peers)
        """
        new_nodes = []
        new_peers = set()

        # result is a list of (success, result) tuples,
        # where success is a boolean, and result is
        # the callback value of the deferred
        for (was_successful, result) in results:
            if was_successful:
                response = result
                if response.nodes is not None:
                    new_nodes.append(response.nodes)
                if response.peers is not None:
                    new_peers.update(response.peers)
            else:
                # A failed query provides no new
                # peers/nodes. Silently drop any such queries
                failure = result
                self._silence_error(failure)

        # return outcome
        return (new_nodes, new_peers)

    def _silence_error(self, failure):
        """
        Trap sendQuery errors

        @see mdht.protocols.krpc_sender.sendQuery

        """
        failure.trap(TimeoutError, KRPCError)
