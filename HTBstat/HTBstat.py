#
# $Id: HTBstat.py,v 1.6 2008/01/15 14:57:30 dima Exp $
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

import re

from STATpic import STATpic

class HTBstat:
    """HTB class, which contains all the needed HTB attributes
    like rate, ceil, parent, quantum etc."""

    __version__ = "$Revision: 1.6 $"
    # $Source: /var/local/cvs/py-htbstat/HTBstat/HTBstat.py,v $

    def __init__(self, line):
        """Creates HTB class from an input line,
        which should be taken from `tc class show ...' command."""

        line = line.lower()

        #
        # these may be used to analyze HTB classes hierarchy:
        self.__kidsrate = 0
        self.__kidsceil = 0

        ro = re.compile('root')
        cl = re.compile('class htb ([0-9a-f]+:[0-9a-f]+) ')
        pa = re.compile('parent ([0-9a-f]+:[0-9a-f]+) ')
        ra = re.compile('rate ([0-9]+)([km]{0,1})(bps|bit)')
        ce = re.compile('ceil ([0-9]+)([km]{0,1})(bps|bit)')
        by = re.compile('sent ([0-9]+) bytes')
        pk = re.compile('bytes ([0-9]+) pkts*')
        dr = re.compile('dropped ([0-9]+), ')
        ol = re.compile('overlimits ([0-9]+)')
        le = re.compile('lended: ([0-9]+)')
        bo = re.compile('borrowed: ([0-9]+)')
        to = re.compile('tokens: ([-]*[0-9]+)')
        ct = re.compile('ctokens: ([-]*[0-9]+)')
        bu = re.compile('burst ([0-9]+)([k]*b)')
        cb = re.compile('cburst ([0-9]+)([k]*b)')
        ba = re.compile('backlog ([0-9]+b)* ([0-9])+p')

        # will raise and exception when forced to init
        # with malformed `line':
        try:
            # self.__parent:
            root = ro.search(line)
            parn = pa.search(line)
            if not root:
                self.__parent = parn.group(1)
            else:
                # self.__parent = root.group(0)
                self.__parent = 0
            # self.__class:
            clas = cl.search(line)
            self.__class = clas.group(1)
            #
            # self.__rate:
            rate = ra.search(line)
            self.__rate = int(rate.group(1))
            mult = rate.group(2)
            suff = rate.group(3)
            #
            if suff == 'bit':
                if mult == 'k':
                    self.__rate *= 1024
                elif mult == 'm':
                    self.__rate *= 1048576  # 1024 * 1024
            #
            elif suff == 'bps':
                self.__rate *= 8
                if mult == 'k':
                    self.__rate *= 1024
                elif mult == 'm':
                    self.__rate *= 1048576  # 1024 * 1024
            #
            # self.__ceil:
            ceil = ce.search(line)
            self.__ceil = int(ceil.group(1))
            mult = ceil.group(2)
            suff = ceil.group(3)
            #
            if suff == 'bit':
                if mult == 'k':
                    self.__ceil *= 1024
                elif mult == 'm':
                    self.__ceil *= 1048576  # 1024 * 1024
            #
            elif suff == 'bps':
                self.__ceil *= 8
                if mult == 'k':
                    self.__ceil *= 1024
                elif mult == 'm':
                    self.__ceil *= 1048576  # 1024 * 1024
            #
            # self.__burst:
            burst = bu.search(line)
            suff = burst.group(2)
            if suff == 'kb':
                self.__burst = 1024 * int(burst.group(1))
            elif suff == 'mb':
                self.__burst = 1024 * 1024 * int(burst.group(1))
            else:
                self.__burst = int(burst.group(1))
            # self.__cburst:
            cburst = cb.search(line)
            self.__cburst = int(cburst.group(1))
            # self.__bytes:
            bytes = by.search(line)
            self.__bytes = int(bytes.group(1))
            # self.__packets:
            packets = pk.search(line)
            self.__packets = int(packets.group(1))
            # self.__dropped:
            drop = dr.search(line)
            self.__dropped = int(drop.group(1))
            # self.__overlimits:
            ovlim = ol.search(line)
            self.__overlimits = int(ovlim.group(1))
            # self.__lended:
            lend = le.search(line)
            self.__lended = int(lend.group(1))
            # self.__borrowed:
            borr = bo.search(line)
            self.__borrowed = int(borr.group(1))
            # self.__tokens:
            tok = to.search(line)
	    self.__tokens = int(tok.group(1))
            # self.__ctokens:
            ctok = ct.search(line)
            self.__ctokens = int(ctok.group(1))
            # self.__backlog:
            blog = ba.search(line)
            if not blog:
                self.__backlog = 0
            else:
                self.__backlog = int(blog.group(2))
            #
        except AttributeError:
            print '\n  ** AttributeError: \
                    malformed data fed to constructor. **'
            print   '  ** (should be output of \
                    `tc -s class show dev <dev>\') **\n'
            raise
        return

    def __cmp__(self, other):
        """HTB classes can be sorted by class id with __cmp__"""
        return cmp(self.__class, other.__class)

    def rcsid(self):
        """Returns RSC id of HTBstat.py source file."""
        return '$Id: HTBstat.py,v 1.6 2008/01/15 14:57:30 dima Exp $'

    def dump(self):
        """Produces an output,
        similar to `tc class show ...' command."""
        dump = 'class htb ' + self.__class
        if self.__parent == 0:
            dump = dump + ' root '
        else:
            dump = dump + ' parent ' + self.__parent

        dump = dump + ' rate ' + str(self.__rate) + 'bit' + \
                ' ceil ' + str(self.__ceil) + 'bit' + \
                ' burst ' + str(self.__burst) + \
                'b/8 cburst ' + str(self.__cburst) + 'b/8' + \
                '\n Sent ' + str(self.__bytes) + ' bytes ' + \
                str(self.__packets) + ' pkts (dropped ' + \
                str(self.__dropped) + ' overlimits ' + \
                str(self.__overlimits) + ')\n' + \
                '   backlog ' + str(self.__backlog) + 'p\n' + \
                ' lended: ' + str(self.__lended) + \
                ' borrowed: ' + str(self.__borrowed) + '\n' + \
                ' tokens: ' + str(self.__tokens) + \
                ' ctokens: ' + str(self.__ctokens)
        return dump

    #
    def clid(self):
        """Returns HTB class id."""
        return self.__class
    def bytes(self):
        """Returns HTB `bytes sent' counter."""
        return self.__bytes
    def packets(self):
        """Returns HTB `packets sent' counter."""
        return self.__packets
    def dropped(self):
        """Returns HTB `packets dropped' counter."""
        return self.__dropped
    def overlimits(self):
        """Returns HTB `overlimits' counter."""
        return self.__overlimits
    def lended(self):
        """Returns HTB `lended' counter."""
        return self.__lended
    def borrowed(self):
        """Returns HTB `borrowed' counter."""
        return self.__borrowed
    def tokens(self):
        """Returns HTB `tokens' counter."""
        return self.__tokens
    def ctokens(self):
        """Returns HTB `ctokens' counter."""
        return self.__ctokens
    def parent(self):
        """Returns HTB class' parent id."""
        return self.__parent
    def rate(self):
        """Returns HTB class rate value."""
        return self.__rate
    def ceil(self):
        """Returns HTB class ceil value."""
        return self.__ceil
    def burst(self):
        """Returns HTB class burst value."""
        return self.__burst
    def cburst(self):
        """Returns HTB class cburst value."""
        return self.__cburst
    def backlog(self):
        """Returns HTB class backlog value."""
        return self.__backlog
    def kidsrate(self, rate=None):
        """Returns sum of children's rates.
        May be used to analyze HTB classes hierarchy."""
        if rate:
            self.__kidsrate = rate
        return self.__kidsrate
    def kidsceil(self, ceil=None):
        """Returns sum of children's ceils.
        May be used to analyze HTB classes hierarchy."""
        if ceil:
            self.__kidsceil = ceil
        return self.__kidsceil

##############################################################
