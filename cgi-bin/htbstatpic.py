#!/usr/bin/python
#
#
# $Id: htbstatpic.py,v 1.5 2008/01/16 10:27:46 dima Exp $
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

rcsid = '$Id: htbstatpic.py,v 1.5 2008/01/16 10:27:46 dima Exp $'

import cgi

import rrdtool
import os

import sys

import re
import glob

import pickle
import md5

import time

import HTBstat

# config file:
execfile('/etc/htbstat/htbstat.cgi')

remaddr = os.getenv("REMOTE_ADDR")

######################################################################

keys = { 'parent': 'Parent is ',
     'classid': 'Class ID is ' }

units = { 'packets': 'Packets',
      'bytes': 'Bytes',
      'tokens': 'Tokens' }

timeranges = { '0014400': 'last 2 hours',
        #'0118800': 'last 33 hours',
        #'0831600': 'last 9 days',
        #'3564000': 'last 41 days'
        }

######################################################################

# remove old pictures:
oldpics = glob.glob ( '%s/*%s*.png' % ( picpath, remaddr ) )
for oldpic in oldpics:
    os.remove(oldpic)

#
# Make a lists of rrdbases:
#
if devone != disabled:
    irrdlist = glob.glob('%s/*.rrd' % rrdONEpath)
    irrdhash = {}

    for it in irrdlist:
        namepat = re.search('([0-9]+).rrd', it)
        namestr = namepat.group(1)
        irrdhash[namestr] = namestr

    iclfiles = glob.glob('%s/*.pickle' % rrdONEpath)
    iclasses = []

    for cls in iclfiles:
        classfile = open(cls, 'r')
        iclass = pickle.load(classfile)
        iclasses.append(iclass)

# the same for devout:
if devtwo != disabled:
    orrdlist = glob.glob('%s/*.rrd' % rrdTWOpath)
    orrdhash = {}
    
    for it in orrdlist:
        namepat = re.search('([0-9]+).rrd', it)
        namestr = namepat.group(1)
        orrdhash[namestr] = namestr
    
    oclfiles = glob.glob('%s/*.pickle' % rrdTWOpath)
    oclasses = []
    
    for cls in oclfiles:
        classfile = open(cls, 'r')
        oclass = pickle.load(classfile)
        oclasses.append(oclass)

#
# list of classes
# and loading classes:

######################################################################

#
# twidding with cgi:
#
F = cgi.FieldStorage()

#
# too long :-)
F.gv = F.getvalue
F.gf = F.getfirst


# get CGI values from the form:
dev, iclid, oclid, ikey, okey, unit, limits, trange, \
                pkts_upperlim, pkts_forcelim, ceil_upperlim, ceil_forcelim = \
    F.gv("dev"),    F.gf("iclid"),  F.gv("oclid"), \
    F.gv("ikey"),   F.gv("okey"),   F.gf("unit"), \
    F.gv("limits"), F.gf("trange"),  \
    F.gv("pupperlim"), F.gv("pforcelim"), \
    F.gv("cupperlim"), F.gv("cforcelim")

if dev not in (devone, devtwo):
    if devone != disabled:
        dev = devone
    else:
        dev = devtwo

#
# defclid = "63"
#

if not iclid:
    iclid = [ defclid ]
else:
    iclid = F.getlist("iclid")

if not oclid:
    oclid = [ defclid ]
else:
    oclid = F.getlist("oclid")

if ikey not in keys: ikey = 'classid'
if okey not in keys: okey = 'classid'

if dev == devone:
    clid = iclid
    key = ikey
else:
    clid = oclid
    key = okey

if not unit:
    unit = [ 'bytes' ]
else:
    unit = F.getlist("unit")

if not trange:
    trange = [ '0118800' ]
else:
    trange = F.getlist("trange")


if not ceil_upperlim:
    ceil_upperlim = 1
else:
    ceil_upperlim = float(ceil_upperlim)

if not ceil_forcelim:
    ceil_forcelim = ''
else:
    ceil_forcelim = 'checked'

if not pkts_upperlim:
    pkts_upperlim = 1
else:
    pkts_upperlim = float(pkts_upperlim)

if not pkts_forcelim:
    pkts_forcelim = ''
else:
    pkts_forcelim = 'checked'



#
# all cgi values are set.
#
######################################################################

#
# Here we need to create a list with clids to be drawn:
#

if dev == devone:
    classfilelist = iclasses
else:
    classfilelist = oclasses
    # swap pathes:
    (rrdONEpath, rrdTWOpath) = (rrdTWOpath, rrdONEpath)

#

# all the classes (possibly to process) for this flow direction:
classfilelist.sort()

#
#
statpic = HTBstat.STATpic()
statpic.picpath(picpath)
statpic.units(unit)

# we need this only to `dump()':
htbclasslist = []

#
# make list of classes to be `pictured':
if key == 'classid':
    for cl in clid:
        htb = getbyclid(classfilelist, cl)
        htbclasslist.append(htb)
        if devone != disabled:
            rrdONEfile = '%s/%s.rrd' % ( rrdONEpath,  htb.clid() )
        else:
            rrdONEfile = None
        if devtwo != disabled:
            rrdTWOfile = '%s/%s.rrd' % ( rrdTWOpath, htb.clid() )
        else:
            rrdTWOfile = None
        statpic.addhtbclass(htb, rrdONEfile, rrdTWOfile)
elif key == 'parent':
    for htb in classfilelist:
        for cl in clid:
            if htb.parent() == cl:
                htbclasslist.append(htb)
                if devone != disabled:
                    rrdONEfile = '%s/%s.rrd' % ( rrdONEpath,  htb.clid() )
                else:
                    rrdONEfile = None
                if devtwo != disabled:
                    rrdTWOfile = '%s/%s.rrd' % ( rrdTWOpath, htb.clid() )
                else:
                    rrdTWOfile = None
                statpic.addhtbclass(htb, rrdONEfile, rrdTWOfile)
else:
    for cl in clid:
        htb = getbyclid(classfilelist, cl)
        htbclasslist.append(htb)
        if devone != disabled:
            rrdONEfile = '%s/%s.rrd' % ( rrdONEpath,  htb.clid() )
        else:
            rrdONEfile = None
        if devtwo != disabled:
            rrdTWOfile = '%s/%s.rrd' % ( rrdTWOpath, htb.clid() )
        else:
            rrdTWOfile = None
        statpic.addhtbclass(htb, rrdONEfile, rrdTWOfile)


#
#
# PNG image.
#
#

print "Content-Type: image/png"     # image is following
print                   # blank line, end of headers

# if we asked to draw rate and ceil lines
# (`limits' should be `on' or None ideally):
statpic.needlimits(limits)

# set upper limit for graph:
statpic.ceil_upperlim(ceil_upperlim)

# force hard upper limit, if needed:
if ceil_forcelim == 'checked':
    statpic.ceil_forcelim(1)
else:
    statpic.ceil_forcelim(0)


# set upper limit for graph:
statpic.pkts_upperlim(pkts_upperlim)

# force hard upper limit, if needed:
if pkts_forcelim == 'checked':
    statpic.pkts_forcelim(1)
else:
    statpic.pkts_forcelim(0)


# add timeranges:
for i in range(len(trange)):
    if i == 0:
        statpic.timerange(int(trange[i]))
    else:
        statpic.addtimerange(int(trange[i]))

#
md5key  = md5.new(str(time.time())).hexdigest()
picname = '%s-$s.png' % ( remaddr, md5key )


# draw all the pictures!
piclist = statpic.draw(picname)


for pic in piclist:
    nameofpic = picpath + pic
    out = open(nameofpic, "r")
    allthepicture = out.read()
    sys.stdout.write(allthepicture)

# WOW! All is well.
