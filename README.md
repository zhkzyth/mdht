mdht
====

A library with protocols needed to run a Mainline DHT node (written with Twisted)

I fork it from [mdht][1],and hack a lot to fit my need.so it may not be good to make pull requests.

### TODO
- bt
  - info save to db
- node state monitor
  - kbucket heartbeat
  - how to find out if a node is in a dead nodes tree
- wiki
  - make a better look
  - structure pics
- test

### dev log
- `2013-12.15`
  - make a better distributed algorithm
- `2013-12.11`
  - add persitent stragety for routing table
- `2013-12.10`
  - change source info share with mongodb
  - delete master branch and repush a temp branch
- `2013-12.9`
  - change sharing with mem support,not mongodb
- `2013-11-24`
  - add  persitent layer to store resources
  - document wiki
- `2013-11-22`
  - store the node info to the database and reload it everytime we start the MDHT node
- `2013-11-20` add log support
- `2013-11-1`  Multi UDP port support
- `2013-10-30` fix example bug,and find out more bugs

[1]: https://github.com/gsko/mdht
