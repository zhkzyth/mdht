import os
import sys
import inspect
import random

from twisted.internet import reactor, defer
from twisted.python import log


# realpath() with make your script run, even if you symlink it :)
# print os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
cmd_folder = os.path.dirname(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from mdht.run import MDHT
from mdht import constants

rand_id = random.getrandbits(160)
dht = MDHT(rand_id,bootstrap_addresses=constants.bootstrap_addresses)

def print_nodes(nodes):
    for node in nodes:
        print node

def print_error(error):
    print repr(error)

the_hobbit = long("D20E34D7C69C296B7CB7447532DF6AA4D2BE001C", 16)

def start_find_iterate(target_hash):

    log.msg("Test")

    d = dht.find_iterate(the_hobbit)
    d.addCallback(print_nodes)
    d.addCallback(dht.halt)
    d.addErrback(print_error)

def sleep(timeout, result):
    def callbackDeferred():
        d.callback(result)

    d = defer.Deferred()
    reactor.callLater(timeout, callbackDeferred)
    return d


## TOOD read more about defer
hello_hobbit = sleep(2, the_hobbit)
hello_hobbit.addCallback(start_find_iterate)


dht.run()

print "done!"


## BUG bug trace
# response received.
# _query_success_callback, and result is  <Response: _transaction_id=642969215 _from=317154048389466424130106923644138888755455657603 nodes=[node: id=1237768010472453021273499451851168531972067718074 address=ip=194.187.148.17 port=51413 last_updated=1383114999 successcount=0 failcount=0, node: id=1438499372565149450789185444319057953281065000455 address=ip=92.25.141.105 port=18755 last_updated=1383114999 successcount=0 failcount=0, node: id=882067139100962798206090797926336505744279906868 address=ip=83.149.48.32 port=17413 last_updated=1383114999 successcount=0 failcount=0, node: id=877394684277294150896812061505496098807789183787 address=ip=94.249.190.25 port=51415 last_updated=1383114999 successcount=0 failcount=0, node: id=812387264967793207610708650157609580050957085101 address=ip=188.255.68.180 port=6881 last_updated=1383114999 successcount=0 failcount=0, node: id=1011333876748459310938717608074819939239256096833 address=ip=109.205.253.164 port=40175 last_updated=1383114999 successcount=0 failcount=0, node: id=1051630343474261319612491142148523219018536535494 address=ip=198.105.217.100 port=21791 last_updated=1383114999 successcount=0 failcount=0, node: id=504851263122777398160297008733021089954271914546 address=ip=85.26.184.74 port=56822 last_updated=1383114999 successcount=0 failcount=0]>
# node: id=1051630343474261319612491142148523219018536535494 address=ip=198.105.217.100 port=21791
# node: id=1237768010472453021273499451851168531972067718074 address=ip=194.187.148.17 port=51413
# node: id=504851263122777398160297008733021089954271914546 address=ip=85.26.184.74 port=56822
# node: id=877394684277294150896812061505496098807789183787 address=ip=94.249.190.25 port=51415
# node: id=1011333876748459310938717608074819939239256096833 address=ip=109.205.253.164 port=40175
# node: id=812387264967793207610708650157609580050957085101 address=ip=188.255.68.180 port=6881
# node: id=882067139100962798206090797926336505744279906868 address=ip=83.149.48.32 port=17413
# node: id=1438499372565149450789185444319057953281065000455 address=ip=92.25.141.105 port=18755
# <twisted.python.failure.Failure <type 'exceptions.TypeError'>>
