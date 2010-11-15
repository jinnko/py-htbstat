#!/usr/bin/python
#
# $Id: htbstat.py,v 1.11 2008/01/24 09:11:36 dima Exp $
# vim:set ts=4 sw=4 sts=4 expandtab:
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

rcsid = '$Id: htbstat.py,v 1.11 2008/01/24 09:11:36 dima Exp $'

import cgi

import rrdtool
import os
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

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

print '<html>\n<head>\n<title>%s</title>' % pagetitle
print """
 <style type="text/css">
    pre    {
        text-align: left;
    }
    span.term {
        font-family: 'Fixed', 'Courier New';
    }
    span.rcsid {
        font-family: 'Fixed', 'Courier New';
        font-size: 70%%;
    }
 </style>
 <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
"""

######################################################################

keys = { 'parent': 'Parent is ',
     'classid': 'Class ID is ' }

units = { 'packets': 'Packets',
      'bytes': 'Bytes',
      'tokens': 'Tokens' }

timeranges = { '0014400': 'last 2 hours',
        '0118800': 'last 33 hours',
        '0831600': 'last 9 days',
        '3564000': 'last 41 days' }

uppers = { '0.5ceil':  'ceil x .5',
    '1.0ceil':  'ceil',
    '1.1ceil': 'ceil x 1.1',
    '2ceil':  'ceil x 2',
    '4ceil':  'ceil x 4',
    'tenceil': 'ceil x 10',
    'unlim':  'unlim' }

CFs = {
    'MIN': 'MIN',
    'MAX': 'MAX',
    'AVERAGE': 'AVG'
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
    irrdcomment = {}

    for it in irrdlist:
        namepat = re.search('([0-9]+:[0-9]+).rrd', it)
        if namepat:
            namestr = namepat.group(1)

            if os.path.exists('/etc/htb'):
                # Connect to htbinit to get comments for the graphs
                htbinitpat = re.search('(1:([0-9]{2,}))', namestr)
                if htbinitpat:
                    tcclass = htbinitpat.group(2)
                    htbinitlist = glob.glob('/etc/htb/%s-*:%s*' % (devone, tcclass))
                    if len(htbinitlist) == 1:
                        commentpat = re.search('[0-9]+:[0-9]+:%s\.(.*)' % tcclass, htbinitlist[0])
                        htbcomment = commentpat.group(1)

                        irrdcomment[namestr] = htbcomment
        else:
            namestr = None

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
        namepat = re.search('([0-9]+:[0-9]+).rrd', it)
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
dev, iclid, oclid, ikey, okey, unit, limits, trange, upper, \
                pkts_upperlim, pkts_forcelim, ceil_upperlim, ceil_forcelim, \
                CF = \
    F.gv("dev"), F.gf("iclid"), F.gv("oclid"), \
    F.gv("ikey"), F.gv("okey"), F.gf("unit"), \
    F.gv("limits"), F.gf("trange"), F.gf("upper"), \
    F.gv("pupperlim"), F.gv("pforcelim"), F.gv("cupperlim"), \
    F.gv("cforcelim"), F.gv("CF")


if dev not in (devone, devtwo):
    if devone != disabled:
        dev = devone
    else:
        dev = devtwo

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


if not upper:
    upper = [ 'ceil' ]
else:
    upper = F.getlist("upper")


if not ceil_upperlim:
    ceil_upperlim = 1
else:
    ceil_upperlim = float(ceil_upperlim)

if not ceil_forcelim:
    ceil_forcelim = ''
else:
    ceil_forcelim = 'checked'

if not pkts_upperlim:
    pkts_upperlim = 1000.0
else:
    pkts_upperlim = float(pkts_upperlim) * 1000.0

if not pkts_forcelim:
    pkts_forcelim = ''
else:
    pkts_forcelim = 'checked'


if CF not in CFs.keys():
    CF = 'AVERAGE'

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
            rrdONEfile = '%s/%s.rrd' % ( rrdONEpath, htb.clid() )
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
                    rrdONEfile = '%s/%s.rrd' % ( rrdONEpath, htb.clid() )
                else:
                    rrdONEfile = None
                if devtwo != disabled:
                    rrdTWOfile = '%s/%s.rrd' % ( rrdTWOpath, htb.clid() )
                else:
                    rrdTWOfile = None
                statpic.addhtbclass(htb, rrdONEfile, rrdTWOfile, irrdcomment[htb.clid()])
else:
    for cl in clid:
        htb = getbyclid(classfilelist, cl)
        htbclasslist.append(htb)
        if devone != disabled:
            rrdONEfile = '%s/%s.rrd' % ( rrdONEpath, htb.clid() )
        else:
            rrdONEfile = None
        if devtwo != disabled:
            rrdTWOfile = '%s/%s.rrd' % ( rrdTWOpath, htb.clid() )
        else:
            rrdTWOfile = None
        statpic.addhtbclass(htb, rrdONEfile, rrdTWOfile)


#
#
# HTML page.
#
#

print """
<div id="body">
    <h1>%s</h1>
    <form>
    <table class="form"><tr>
        <th>Select source:</th>
        <th>What to display:</th>
    </tr><tr>
        <td>
            <table class="options">
""" % pageheader


# if both are enabled:
if disabled not in (devone, devtwo):
    if dev == devone:
        print "<tr>"
        print """<th colspan="2">
        <input type="radio" name="dev" value="%s" checked>%s
        </th>""" % (devone, devonename)

        if devtwo != disabled:
            print """<th colspan="2">
            <input type="radio" name="dev" value="%s">%s
            </th>""" % (devtwo, devtwoname)

        print "</tr>"

    elif dev == devtwo:
        print "<tr>"
        if devone != disabled:
            print """<th colspan="2">
            <input type="radio" name="dev" value="%s">%s
            </th>""" % (devone, devonename)

        print """<th colspan="2">
            <input type="radio" name="dev" value="%s" checked>%s
            </th>""" % (devtwo, devtwoname)

        print "</tr>"
else:
    print "<tr><th colspan='2'>"
    if dev == devone:
        print devonename
    else:
        print devtwoname

print '</th></tr>'


if devone != disabled:
    print '<TD>%s' % getSelect(keys, 'ikey', ikey)
    print '<TD>%s' % getSelect(irrdhash, 'iclid', clid, 1, 6, \
                        ' Use Control key to select multiple classes. ')

if devtwo != disabled:
    print '<TD>%s' % getSelect(keys, 'okey', okey)
    print '<TD>%s' % getSelect(orrdhash, 'oclid', clid, 1, 6, \
                        ' Use Control key to select multiple classes. ')

print '</TABLE>'

print '<TD align="center"><table class="options">'

print '<TR><TD>%s' % getSelect(units, 'unit', unit, 1, 3, \
                        ' Use Control key to select multiple entries. ')

print '<TD>%s' % getSelect(timeranges, 'trange', trange, 1, 4, \
                        ' Use Control key to select multiple timeranges. ')

print """
</TABLE>
"""

if limits == 'on':
    print '<BR><INPUT type="checkbox" name="limits" checked>',
else:
    print '<BR><INPUT type="checkbox" name="limits">',

print """
&nbsp;Show <SPAN class="term">rate</SPAN>
and <SPAN class="term">ceil</SPAN> values &nbsp;
<TR><TD align="right">Upper limit:<TT>
    <INPUT type="text" size="3" maxsize="3" name="cupperlim"
        value="%s" align="right">&nbsp;x&nbsp;ceil
""" % ceil_upperlim


print """
    (<INPUT type="checkbox" name="cforcelim" value="forced" %s>
        force hard)<BR>
""" % ceil_forcelim

print """
    <INPUT type="text" size="3" maxsize="3" name="pupperlim"
        value="%s" align="right">&nbsp; &nbsp;kpps
""" %  str(pkts_upperlim/1000)

print """
    (<INPUT type="checkbox" name="pforcelim" value="forced" %s>
        force hard)</TT>
""" % pkts_forcelim


print '<TD align="center">CF: %s' % \
            getSelect(CFs, 'CF', CF, 0, 0, "rrd's Consolidation Function")


print """
    &nbsp; <INPUT type="submit" value="Submit">

</FORM>
</TABLE>
<TR><TD align="center">
"""

# if we asked to draw rate and ceil lines
# (`limits' should be `on' or None ideally):
statpic.needlimits(limits)

# set upper limit for bytes:
statpic.ceil_upperlim(ceil_upperlim)

# force hard upper limit, if needed:
if ceil_forcelim == 'checked':
    statpic.ceil_forcelim(1)
else:
    statpic.ceil_forcelim(0)


# set upper limit for packets:
statpic.pkts_upperlim(pkts_upperlim)

# force hard upper limit, if needed:
if pkts_forcelim == 'checked':
    statpic.pkts_forcelim(1)
else:
    statpic.pkts_forcelim(0)

# set CF:
statpic.CF(CF)

# add timeranges:
for i in range(len(trange)):
    if i == 0:
        statpic.timerange(int(trange[i]))
    else:
        statpic.addtimerange(int(trange[i]))


# generate a picture ("base-") name:
md5key  = md5.new(str(time.time())).hexdigest()
picname = '%s-%s.png' % ( remaddr, md5key ) 

# draw all the pictures!
piclist = statpic.draw(picname)

# print HTML links to images:
if len(piclist) == 0:
    print '<CENTER><B>Nothing to draw.</B></CENTER>'
else:
    for pic in piclist:
        print '<IMG src="%s/%s">' % ( wwwpicpath, pic )

print '<br style="clear: both" />'
# dump class only `if':
if key == 'classid' or not key:
    print '<TR><TD align="center">'
    for htbclass in htbclasslist:
        print """
            <PRE style="border: solid thin gray; padding: 3 3 3 3;">
%s                      <A href="dumpclass.py?dev=%s&clid=%s"
                            target="_blank">Monitor this class</A>
</PRE>
""" % ( htbclass.dump(), dev, htbclass.clid() )

print """
</TABLE>
<HR>
<TABLE border="0" width="90%" align="center">
<TR><TD>
<SPAN class="rcsid">Copyright (c) 2005&ndash;2008 <A href="mailto:%s@%s.%s.%s">Dmytro O. Redchuk</A></SPAN><BR>
<SPAN class="rcsid">Copyright (c) 2005&ndash;2008 <A href="http://www.volz.ua/">VOLZ Llc</A></SPAN><BR>
""" % ('dmytro', 'redchuck', 'org', 'ua')

# to get RCS Id:-)
sample = iclasses[0]

# print '<!-- '
print """
<TD align="right">
    <SPAN class="rcsid">htbstat.py: %s</SPAN><BR>
    <SPAN class="rcsid">HTBstat: %s</SPAN><BR>
    <SPAN class="rcsid">STATpic: %s</SPAN><BR>
""" % ( rcsid, sample.rcsid(), statpic.rcsid() )
# print ' -->'
print '</TABLE>'

# WOW! All is well.
