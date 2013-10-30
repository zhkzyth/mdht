"""
An interface to mdht that abstracts away Twisted details (like the reactor)

"""
import sys


from twisted.internet import reactor, defer

from mdht import constants
from mdht.protocols.krpc_iterator import IKRPC_Iterator, KRPC_Iterator



class MDHT(object):

    proto = None

    def __init__(self, node_id,
            port=constants.dht_port, bootstrap_addresses=None):
        """
        Prepares the MDHT client

        Note!! This function can only be called once!

        node_id: the ID under which the MDHT node will run
        port: the UDP port on which to run the MDHT node
        bootstrap_addresses: an iterable of nodes on
            which to bootstrap this MDHT client

        """
        # Let Twisted know about our MDHT node listening on a UDP port
        self.proto = KRPC_Iterator(node_id)
        reactor.listenUDP(port, self.proto)

        # Patch in some functions that are found on the protocol
        self._proxy_funcs()

        # Bootstrap our freshly created node
        self._bootstrap(bootstrap_addresses)

    def _proxy_funcs(self):
        funcnames = filter(lambda name:
                        not (name.startswith("_") or name.endswith("Received")),
                    IKRPC_Iterator)

        for funcname in funcnames:
            # print funcname
            func = getattr(self.proto, funcname, None)
            assert func is not None
            setattr(self, funcname, func)

    def run(self):
        """
        Starts the MDHT loop

        This function will block until MDHT.halt() is called

        """
        reactor.run()

    def _bootstrap(self, addresses=None):
        """
        Bootstrap the MDHT node into the DHT network

        addresses: an iterable containing tuples of hostnames/ip,port

        """
        if addresses is None:
            addresses = set()
        else:
            addresses = set(addresses)
            addresses.update(constants.bootstrap_addresses)

        def ping_success(result):
            print "ok,we finally got it"
            return result

        ## log the timeout,so we need to do another reconnect
        ## or change another bootstrap address
        def ping_fail(error):
            print >> sys.stderr,error
            return None

        def temp_fun(ip_address,self,port):
            print ip_address,port
            d = self.ping((ip_address,port))
            d.addCallbacks(ping_success,ping_fail)
            return None

        dl = defer.DeferredList([])

        # make ping request
        for hostname, port in addresses:
            d = reactor.resolve(hostname)
            d.addCallback(temp_fun,self,port)
            # dl.append(d)

        return dl

    def schedule(self, delay, func, *args, **kwargs):
        """
        Run the specified function 'func' in 'delay' seconds

        delay: number of seconds to wait (float)
        func: the function to run, NOTE! this function must be nonblocking
        args: positional arguments for the function
        kwargs: keyword arguments for the function

        """
        reactor.callLater(delay, func)

    def halt(self):
        """
        Terminates the MDHT client

        Note!! This function can only be called once!

        """
        reactor.stop()

    def get_nodes_num(self):
        """

        Return the size of our routing_table size

        """
        return len(self.proto.routing_table.nodes_dict)
