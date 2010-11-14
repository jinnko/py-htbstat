#!/usr/bin/python
#
#
# $Id: statsfill.py,v 1.3 2008/01/16 11:04:28 dima Exp $
#
#
# Copyright (c) 2005 Dmytro O. Redchuk
# Copyright (c) 2005 VOLZ Llc
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#


import sys
import getopt

import rrdtool

import pickle

import HTBstat

def usage():
    print 'Usage:'
    print '\t%s [options]\n' % sys.argv[0]
    print 'Options:'
    print '\t[-h | --help]\t-- print this help.'
    print '\t[-p | --path] /path/to/rrdbases\n\t\t\t-- use that path for output.'
    return

# config file:
execfile('/etc/htbstat/htbstat.conf')

# process cmdline options
# (this may overwrite `outputdir' variable):
try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:", ["help", "path="])
except getopt.GetoptError:
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit(0)
    if opt in ("-p", "--path"):
        outputdir = arg

##############################################################

def gen_input():
    longline = ''
    while 1:
        ln = sys.stdin.readline()
        if not ln:
            # yield longline if EOF:
            if longline != '':
                longline = longline.strip()
                yield longline
            # break on EOF:
            break
        ln = ln.strip()
        if ln == '':
            # yield longline if (next) empty string:
            if longline != '':
                longline = longline.strip()
                yield longline
                longline = ''
            continue
        longline = longline.strip()
        longline = longline + ' ' + ln.strip()

##############################################################


stats = []

for line in gen_input():
    stats.append(HTBstat.HTBstat(line))

for stat in stats:
    rrdfile = '%s/%s.rrd' % ( outputdir, stat.clid() )
    try:
        rrdbase = open(rrdfile, 'r')
    except:
        rrdtool.create(rrdfile, *rrdcreateparms)
    else:
        rrdbase.close()
    #
    # time to seed:
    #ustr = 'N:'+ \
    #        str(stat.rate()) + ':' + \
    #        str(stat.ceil()) + ':' + \
    #        str(stat.burst()) + ':' + \
    #        str(stat.cburst()) + ':' + \
    #        str(stat.bytes()) + ':' + \
    #        str(stat.packets()) + ':' + \
    #        str(stat.backlog()) + ':' + \
    #        str(stat.dropped()) + ':' + \
    #        str(stat.overlimits()) + ':' + \
    #        str(stat.lended()) + ':' + \
    #        str(stat.borrowed()) + ':' + \
    #        str(stat.tokens()) + ':' + \
    #        str(stat.ctokens())
    ustr = 'N:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s' % (
                stat.rate(),
                stat.ceil(),
                stat.burst(),
                stat.cburst(),
                stat.bytes(),
                stat.packets(),
                stat.backlog(),
                stat.dropped(),
                stat.overlimits(),
                stat.lended(),
                stat.borrowed(),
                stat.tokens(),
                stat.ctokens()
            )
    #
    # log = open('000log', 'a')
    # log.write(str(stat.clid())+' == '+ustr+'\n')
    # log.close()
    #
    rrdtool.update(rrdfile, ustr)
    #
    # dump class object to file:
    classfile = open('%s/%s.pickle' % ( outputdir, stat.clid()), 'w')
    pickled = pickle.Pickler(classfile)
    pickled.dump(stat)
    classfile.close()



