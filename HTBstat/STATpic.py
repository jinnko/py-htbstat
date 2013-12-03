#
# STAT picture class
# optimized for multiple pictures drawing.
#
#
# $Id: STATpic.py,v 1.7 2008/01/16 10:27:46 dima Exp $
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
import rrdtool

class STATpic:
    """A `picture' class, which draws png images from rrd bases.
    Can draw multiple images from multiple bases, for multiple timerages,
    of different data types (bytes, packets, tokens)."""
    
    __version__ = "$Revision: 1.7 $"
    # $Source: /var/local/cvs/py-htbstat/HTBstat/STATpic.py,v $

    def __init__(self):
        """Creates class instance with default values
        (no rrd bases for input, default time range)."""
        # some defaults, if not set explicitly:
        self.__units = [ 'bytes' ]
        self.__CF = 'AVERAGE'
        self.__needlimits = 'on'

        # default time range for picture drawing:
        self.__timerange = [ [ 118800, 0 ] ]

        # upper limit in ceil (kpps) quantities:
        self.__ceil_upperlim = 1
        self.__pkts_upperlim = 1
        self.__ceil_forcelim = 0
        self.__pkts_forcelim = 0

        # initial list of classes:
        self.__htbclasses = []

        # picture dimensions:
        self.__height = 130
        self.__width  = 500

        self.__do_sum = False

        return

    def rcsid(self):
        """Returns RSC id for this source file."""
        return '$Id: STATpic.py,v 1.7 2008/01/16 10:27:46 dima Exp $'

    def needlimits(self, val):
        """Takes an argument which defines should a picture have
        HLINEs at rate and ceil values."""
        self.__needlimits = val
        return

    def timerange(self, start, end=0):
        """Appends time range to timeranges list.
        A picture will be drawn for every timerange, in sequence."""
        self.__timerange = [ [start, end] ]
        return

    def units(self, val):
        """Sets (or returns) units for which a picture should be drawn.
        Possible are `bytes', `packets' or `tokens'."""
        self.__units = val
        return self.__units

    def picpath(self, path):
        """Specifies path on a filesystem where rrd bases are.
        All the rrd classes (bases actually) will be taken from there."""
        if path != '':
            self.__picpath = path
        return self.__picpath

    def addhtbclass(self, htbclass, rrdone, rrdtwo, comment = ''):
        """Adds rrd bases to list of classes to be processed."""
        # mask ':' in filenames:
        rrdone = rrdone.replace(':', '\:')
        # rrdtwo can be not set:
        rrdtwo = rrdtwo and rrdtwo.replace(':', '\:')
        self.__htbclasses.append([htbclass, rrdone, rrdtwo, comment])
        return

    def addtimerange(self, start, end=0):
        """Adds another timerange.
        Pictures will be drawn for every timerange in list, in sequence."""
        self.__timerange.append([start, end])
        return

    def CF(self, cf):
        """Specifies rrd's consolidation function (CF) for processing data."""
        if cf in ('MAX', 'MIN', 'AVERAGE'):
            self.__CF = cf
        return self.__CF

    def ceil_upperlim(self, upperlim):
        """Specifies the upper limit for graph."""
        if float(upperlim) != 0:
            self.__ceil_upperlim = float(upperlim)
        return self.__ceil_upperlim

    def ceil_forcelim(self, forcelim):
        """Specifies whether upper limit should be forced (rrdtool's -r option)."""
        if int(forcelim) not in (0, 1) :
            self.__ceil_forcelim = 0
        else:
            self.__ceil_forcelim = forcelim
        return self.__ceil_forcelim

    def pkts_upperlim(self, upperlim):
        """Specifies the upper limit for graph."""
        if float(upperlim) != 0:
            self.__pkts_upperlim = float(upperlim)
        return self.__pkts_upperlim

    def pkts_forcelim(self, forcelim):
        """Specifies whether upper limit should be forced (rrdtool's -r option)."""
        if int(forcelim) not in (0, 1) :
            self.__pkts_forcelim = 0
        else:
            self.__pkts_forcelim = forcelim
        return self.__pkts_forcelim

    def do_sum(self, do_sum=False):
      self.__do_sum = do_sum
      return self.__do_sum

    #
    #
    def draw(self, picname):
      """Draws pictures, for every class, every timerange,
      every unit specified.
        
      Takes as argument picture name `suffix'. Pictures will be named
      <picno>-<classno>-<suffix>, where
      <picno> is a picture number,
      <classno> is a class number in self.__htbclasses list.
        
      Returns list of picture names."""

      piclist = []
      # for every timerange:
      if not self.__do_sum:
        for num, (htb, rrdone, rrdtwo, comment) in enumerate(self.__htbclasses):
          if rrdone == None:
            rrdone = rrdtwo
            rrdtwo = None

          #
          # for every htbclass in list:
          for (start, end) in self.__timerange:
            for unit in self.__units:
              timenum = len(piclist)

              picture = str(timenum)+'-'+str(num)+'-'+picname

              grapharg = [
                  '%s/%s' % (self.__picpath, picture),
                  '-s -'+str(start),
                  '-e -'+str(end),
                  '-b 1024',
                  '-l 0',
                  '-h '+str(self.__height),
                  '-w '+str(self.__width),
                  # '--alt-y-mrtg',
                ]
              if unit == 'packets':
                grapharg.extend([
                    '-v bits per sec',
                    '-u '+str(self.__pkts_upperlim),
                  ])
                #
                # force upper limit, if needed:
                if self.__pkts_forcelim == 1:
                  grapharg.extend([ '-r' ])

                grapharg.extend([
                    '-v pkts per sec',
                    '-t class '+str(htb.clid())+' - '+comment+' - packects ('+self.__CF+')',
                    'DEF:pkts='+rrdone+':packets:'+self.__CF, 
                    'DEF:drop='+rrdone+':dropped:'+self.__CF, 
                    'DEF:lend='+rrdone+':lended:'+self.__CF,
                    'DEF:borr='+rrdone+':borrowed:'+self.__CF,
                    'DEF:back='+rrdone+':backlog:'+self.__CF,
                    'AREA:back#CFCFCF:backlog',
                    'LINE1:pkts#55CC55:pkts',
                    'LINE1:drop#DD3333:drops',
                    'LINE1:lend#000000:lend',
                    'LINE1:borr#5555CC:borrow',
                  ])
              elif unit == 'tokens':
                grapharg.extend([
                    '-v toks per sec',
                    '-t class '+str(htb.clid())+' - '+comment+' - tokens ('+self.__CF+')',
                    'DEF:toks='+rrdone+':tokens:'+self.__CF, 
                    'DEF:ctoks='+rrdone+':ctokens:'+self.__CF, 
                    'HRULE:0#000000',
                    'LINE1:toks#55CC55:tokens',
                    'LINE1:ctoks#DD3333:ctokens',
                  ])
              else:        # if bytes:
                grapharg.extend([
                    '-v bits per sec',
                    '-u '+str(self.__ceil_upperlim * htb.ceil()),
                    '-t class '+str(htb.clid())+' - '+comment+' - bps ('+self.__CF+')',
                  ])
                #
                # force upper limit, if needed:
                if self.__ceil_forcelim == 1:
                  grapharg.extend([ '-r' ])

                if rrdtwo != None:
                  grapharg.extend([
                      'DEF:twobytes='+rrdtwo+':bytes:'+self.__CF,
                      'CDEF:twobits=twobytes,8,*',
                      'AREA:twobits#55CC55:received',
                    ])
                grapharg.extend([
                    'DEF:onebytes='+rrdone+':bytes:'+self.__CF,
                    'CDEF:onebits=onebytes,8,*',
                    'LINE1:onebits#5555CC:transmitted',
                  ])

                if self.__needlimits == 'on':
                  grapharg.extend([
                      'DEF:onerate='+rrdone+':rate:'+self.__CF,
                      'DEF:oneceil='+rrdone+':ceil:'+self.__CF,
                    ])
                  grapharg.extend([
                      'CDEF:oneratek=onerate,1.024,*',
                      'CDEF:oneceilk=oneceil,1.024,*',
                      'LINE1:oneratek#000000:irate',
                      'LINE1:oneceilk#DD3333:iceil',
                    ])

              rrdtool.graph(*grapharg)
              piclist.append(picture)


      else:
        # GRAPH SUM of those:
        """
        for num, (htb, rrdone, rrdtwo, comment) in enumerate(self.__htbclasses):
          if rrdone == None:
            rrdone = rrdtwo
            rrdtwo = None
        """

        #
        # for every htbclass in list:
        for (start, end) in self.__timerange:
          for unit in self.__units:
            timenum = len(piclist)

            picture = str(timenum)+'--sum--'+picname

            grapharg = [
                '%s/%s' % (self.__picpath, picture),
                '-s -'+str(start),
                '-e -'+str(end),
                '-b 1024',
                '-l 0',
                '-h '+str(self.__height),
                '-w '+str(self.__width),
                # '--alt-y-mrtg',
              ]


            if unit == 'packets':
              grapharg.extend([
                  '-v pkts per sec',
                  # '-t class '+str(htb.clid())+' - '+comment+' - packects ('+self.__CF+')',
                  '-u '+str(self.__pkts_upperlim),
                ])
              #
              # force upper limit, if needed:
              if self.__pkts_forcelim == 1:
                grapharg.extend([ '-r' ])

            elif unit == 'tokens':
              grapharg.extend([
                  '-v toks per sec',
                  # '-t class '+str(htb.clid())+' - '+comment+' - tokens ('+self.__CF+')',
                ])

            else:        # if bytes:
              grapharg.extend([
                  '-v bits per sec',
                  # '-u '+str(self.__ceil_upperlim), # * htb.ceil()),
                  # '-t class '+str(htb.clid())+' - '+comment+' - bps ('+self.__CF+')',
                ])
              #
              # force upper limit, if needed:
              if self.__ceil_forcelim == 1:
                grapharg.extend([ '-r' ])


            maxceil = 0
            vardefs_one = dict()
            vardefs_two = dict()

            for num, (htb, rrdone, rrdtwo, comment) in enumerate(self.__htbclasses):
              if rrdone == None:
                rrdone = rrdtwo
                rrdtwo = None

              # FIXME? root id removing hardcoded (root id is now "1:")
              # print '%s<br/>' % htb.clid()[2:]

              if unit == 'packets':
                # FIXME: that's because we cannot draw packets or tokens now:
                pass
                """
                grapharg.extend([
                    'DEF:pkts='+rrdone+':packets:'+self.__CF, 
                    'DEF:drop='+rrdone+':dropped:'+self.__CF, 
                    'DEF:lend='+rrdone+':lended:'+self.__CF,
                    'DEF:borr='+rrdone+':borrowed:'+self.__CF,
                    'DEF:back='+rrdone+':backlog:'+self.__CF,
                    'AREA:back#CFCFCF:backlog',
                    'LINE1:pkts#55CC55:pkts',
                    'LINE1:drop#DD3333:drops',
                    'LINE1:lend#000000:lend',
                    'LINE1:borr#5555CC:borrow',
                  ])
                """
              elif unit == 'tokens':
                # FIXME: that's because we cannot draw packets or tokens now:
                pass
                """
                grapharg.extend([
                    'DEF:toks='+rrdone+':tokens:'+self.__CF, 
                    'DEF:ctoks='+rrdone+':ctokens:'+self.__CF, 
                    'HRULE:0#000000',
                    'LINE1:toks#55CC55:tokens',
                    'LINE1:ctoks#DD3333:ctokens',
                  ])
                """

              else:        # if bytes:
                if rrdtwo != None:
                  vardefs_two['%s-twobytes'%(htb.clid()[2:])] = '%s:bytes:%s' % (rrdtwo, self.__CF)

                vardefs_one['%s-onebytes'%(htb.clid()[2:])] = '%s:bytes:%s' % (rrdone, self.__CF)
                maxceil = max(maxceil, htb.ceil())

            # FIXME: that's because we cannot draw packets or tokens now:
            if not vardefs_two and not vardefs_one:
              return []


            if vardefs_two:
              for k, v in vardefs_two.items():
                grapharg.append( 'DEF:%s=%s' % (k, v) )

              grapharg.append('CDEF:twobytes=%s%s' % (
                      ','.join([
                            '%s,UN,0,%s,IF' % (k, k)
                                for k, v in vardefs_two.items()
                      ]),
                      len(vardefs_two.keys()) - 1 \
                        and ',+'*(len(vardefs_two.keys()) - 1) \
                        or ''
                    )
                )

              grapharg.extend([
                  'CDEF:twobits=twobytes,8,*',
                  'AREA:twobits#55CC55:received',
                ])

            for k, v in vardefs_one.items():
              grapharg.append( 'DEF:%s=%s' % (k, v) )

            grapharg.append('CDEF:onebytes=%s%s' % (
                    ','.join([
                          '%s,UN,0,%s,IF' % (k, k)
                              for k, v in vardefs_one.items()
                    ]),
                    len(vardefs_one.keys()) - 1 \
                      and ',+'*(len(vardefs_one.keys()) - 1) \
                      or ''
                  )
              )

            grapharg.extend([
                'CDEF:onebits=onebytes,8,*',
                'LINE1:onebits#5555CC:transmitted',
                '-u '+str(self.__ceil_upperlim * maxceil),
              ])


            rrdtool.graph(*grapharg)
            piclist.append(picture)


      return piclist

