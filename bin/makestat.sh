#!/bin/bash
#
# $Id: makestat.sh,v 1.2 2008/01/16 11:04:28 dima Exp $
#

#
# An example script which fetches HTB statistics and feed it to other one to
# be processes and stored.
#

#
# This will fetch from remote host:
#ssh -l user -i ~user/.ssh/id_dsa host '/sbin/tc -s -d class show dev eth1' \
#        | /usr/bin/statsfill.py --path /var/www/rrdbases/htbstat/eth1
#ssh -l user -i ~user/.ssh/id_dsa host '/sbin/tc -s -d class show dev eth2' \
#        | /usr/bin/statsfill.py --path /var/www/rrdbases/htbstat/eth2

PATH_HTBSTAT=/path/to/htbstat

# This will grab locally:
#/sbin/tc -s class show dev eth0 | ${PATH_HTBSTAT}/bin/statsfill.py --path ${PATH_HTBSTAT}/data/eth0
/sbin/tc -s class show dev eth1 | ${PATH_HTBSTAT}/bin/statsfill.py --path ${PATH_HTBSTAT}/data/eth1

# Note that the --path arg to statsfill.py must agree with the rrd(ONE|TWO)path in etc/htbstats.cgi

#
# Note again: pathes are just pathes. One could write:
#/sbin/tc -s class show dev eth0 | /usr/bin/statsfill.py --path /tmp/eth0
#/sbin/tc -s class show dev ppp0 | /usr/bin/statsfill.py --path /tmp/ppp0
