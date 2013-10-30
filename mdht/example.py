import os
import sys
import inspect
import random

from twisted.internet import reactor, defer
# from twisted.python import log


# realpath() with make your script run, even if you symlink it :)
# print os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
cmd_folder = os.path.dirname(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from mdht.run import MDHT
from mdht import constants

def print_nodes(nodes):
    for node in nodes:
        print node

def log_errors(error):
    print "opps",repr(error)

def stop_loop(result):
    reactor.stop()

the_hobbit = long("D20E34D7C69C296B7CB7447532DF6AA4D2BE001C", 16)

def start_find_iterate(target_hash):
    d = dht.find_iterate(the_hobbit)
    d.addCallback(print_nodes)
    # d.addCallbacks(stop_loop,log_errors)

def sleep(timeout, result):
    def callbackDeferred():
        d.callback(result)

    d = defer.Deferred()
    reactor.callLater(timeout, callbackDeferred)
    return d

num = 0
_port = constants.dht_port

while  num<5:
    rand_id = random.getrandbits(160)
    dht = MDHT(rand_id,bootstrap_addresses=constants.bootstrap_addresses,port=_port)

    num += 1
    _port += 1

    hello_hobbit = sleep(2, the_hobbit)
    hello_hobbit.addCallback(start_find_iterate)

reactor.run()
