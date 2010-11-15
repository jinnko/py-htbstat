#!/usr/bin/python
#
#
# $Id: htbcheck.py,v 1.8 2008/01/17 15:36:22 dima Exp $
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

rcsid = '$Id: htbcheck.py,v 1.8 2008/01/17 15:36:22 dima Exp $'

import cgi

import os
import glob
import re

import pickle
import copy

import HTBstat

# config file:
execfile('/etc/htbstat/htbstat.cgi')

remaddr = os.getenv("REMOTE_ADDR")

##########################################################

def printgraphlink(dev, cl):
    print """<B><U>Class %s</U></B>: <A
                href="htbstat.py?dev=%s&ikey=classid&iclid=%s&okey=classid&oclid=%s&unit=bytes&unit=packets">View graph</A>""" % ( cl, dev, cl, cl )

def printclasslink(dev, cl):
    print """<A href="?dev=%s&root=%s"><B>Class %s</B></A> <A href="?dev=%s&root=%s&do=dumpchild">(dump connected children)</A> <A href="?dev=%s&root=%s&do=dumpall">(dump all classes below)</A>:
    """ % ( dev, cl, cl, dev, cl, dev, cl )

######################################################################


F = cgi.FieldStorage()

#
# too long :-)
F.gv = F.getvalue

queried_root = F.gv("root")
queried_action = F.gv("do")
queried_dev   = F.gv("dev")

if not queried_root:
    queried_root = defroot
else:
    queried_root = queried_root

if not queried_action:
    queried_action = 'checktree'
# else:
#   queried_root = queried_root

#
# select dev:
if queried_dev not in (devone, devtwo):
    if devone != disabled:
        queried_dev = devone
        devname = devonename
    else:
        queried_dev = devtwo
        devname = devtwoname

#
# choose pathes:
if queried_dev == devone:
    rrdpath = rrdONEpath
else:
    rrdpath = rrdTWOpath

iclfiles = glob.glob('%s/*.pickle' % rrdpath)
iclasses = []

for cls in iclfiles:
    classfile = open(cls, 'r')
    iclass = pickle.load(classfile)
    iclasses.append(iclass)

#
# build list (tree) of classes from `rootclass' and below:
#
rootclass = getbyclid(iclasses,queried_root)
rootslist = [ rootclass ]

rootlen = 0
appended = 1

iclasses.sort()

while appended > 0:
    appended = 0
    rootleng = len(rootslist)
    for i in range(rootlen, rootleng):
        for cl in iclasses:
            if rootslist[i].clid() == cl.parent():
                rootslist.append(cl)
                appended = appended + 1
                continue
        rootlen = rootleng

#
# calculate kidsrate and kidsceil for every class:
#
for kid in iclasses:
    # for parent in iclasses:
    for parent in rootslist:
        if kid.parent() == parent.clid():
            parent.kidsrate(parent.kidsrate() + kid.rate())
            parent.kidsceil(parent.kidsceil() + kid.ceil())

#
#
# HTML page.
#
#
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

print """
<HTML>
<HEAD>
 <TITLE>HTB statistic</TITLE>
 <!-- LINK rel="stylesheet" type="text/css" href="/admin.css" -->
 <STYLE type="text/css">
    SPAN.term {
            font-family: 'Fixed', 'Courier New';
        }
    SPAN.rcsid {
        font-family: 'Fixed', 'Courier New';
        font-size: 70%;
    }
    SPAN.red {
        color:  red;
        font-weight: bold;
    }
    SPAN.overrate {
        color:  brown;
    }
    SPAN.overceil {
        color:  teal;
    }
 </STYLE>
<BODY>
<TABLE border="1">
<TR>
<FORM>
  <TH>
"""


if disabled not in (devone, devtwo):
    print 'Select source: &nbsp;'
    if queried_dev == devone:
        print '<TD><INPUT type="radio" name="dev" value="%s" checked>' % devone
        print devonename
        if devtwo != disabled:
            print '<TD><INPUT type="radio" name="dev" value="%s">' % devtwo
            print devtwoname

    elif queried_dev == devtwo:
        if devone != disabled:
            print '<TD><INPUT type="radio" name="dev" value="%s">' % devone
            print devonename
        print '<TD><INPUT type="radio" name="dev" value="%s" checked>' % devtwo
        print devtwoname
else:
    print devname


print """<TD>&nbsp;<INPUT type="submit" value="Update">&nbsp;
</FORM>
</TABLE>
"""

# sorted by self.__class value:
iclasses.sort()

#
overclasses = []
children = []

#
if queried_root != defroot:
    print '<PRE><A href="?dev=%s">Jump to root</A>' % queried_dev ,

    print """ &nbsp; <A href="?dev=%s&root=%s">Jump to parent of %s (%s)</A>
          """ % ( queried_dev, rootclass.parent(), rootclass.clid(), rootclass.parent() )
    
    print '</PRE>'

#
if queried_action == 'checktree':
    # for cl in iclasses:
    for cl in rootslist:
        if ( cl.kidsrate() != 0 or cl.kidsceil() != 0 ) and \
           ( cl.kidsrate() > cl.rate() \
            or cl.kidsceil() > cl.ceil() \
            or cl.kidsrate() > cl.ceil() \
            ):
            overclasses.append(cl)
    #
    if len(overclasses) == 0:
        print '<H2>No overloaded classes&nbsp;&mdash; I can\'t believe, honest.</H2>'
    else:
        print '<H2>Total of %s overloaded classes:<BR>' % len(overclasses)
        print '(class handle %s and below)</H2>' % rootclass.clid()
    #
    for cl in overclasses:
        # print '<HR>'
        print '<PRE>'
        printclasslink(queried_dev, cl.clid())
        if cl.kidsrate() > cl.ceil():
            print '<SPAN class="red">',
            print '\t!!!!! Sum of children\'s rates (%s) is higher than own ceil (%s)' % (
                            cl.kidsrate(), cl.ceil()
                ),
            print '</SPAN>'

        if cl.kidsrate() > cl.rate():
            print '<SPAN class="overrate">',
            print '\tRATE: Sum of children\'s rates (%s) is higher than own rate (%s)' % (
                            cl.kidsrate(), cl.rate()
                ),
            print '</SPAN>'

        if cl.kidsceil() > cl.ceil():
            print '<SPAN class="overceil">',
            print '\tCEIL: Sum of children\'s ceils (%s) is higher than own ceil (%s)' % (
                            cl.kidsceil(), cl.ceil()
                ),
            print '</SPAN>'

        print '</PRE>'
#
elif queried_action == 'dumpall':
    print '<H2>Total %s classes:<BR>' % len(rootslist)
    print '(class handle %s and below)</H2>' % rootclass.clid()
    for cl in rootslist:
        # print '<HR>'
        print '<PRE>'
        printgraphlink(queried_dev, cl.clid())
        print cl.dump()
        print '</PRE>'
#
elif queried_action == 'dumpchild':
    for cl in iclasses:
        if cl.parent() == queried_root:
            children.append(cl)
    print '<H2>Total %s classes:<BR>' % len(children)
    print '(class handle %s and connected children)</H2>' % rootclass.clid()
    for cl in children:
        # print '<HR>'
        print '<PRE>'
        printgraphlink(queried_dev, cl.clid())
        print cl.dump()
        print '</PRE>'

#
print """
<HR>
<TABLE border="0" width="90%%" align="center">
<TR><TD>
<SPAN class="rcsid">Copyright (c) 2005&ndash;2008 <A href="mailto:%s@%s.%s.%s">Dmytro O. Redchuk</A></SPAN><BR>
<SPAN class="rcsid">Copyright (c) 2005&ndash;2008 <A href="http://www.volz.ua/">VOLZ Llc</A></SPAN><BR>
""" % ('dmytro', 'redchuck', 'org', 'ua')

# print '<!-- '
print """
<TD align="right">
    <SPAN class="rcsid">htbcheck.py: %s</SPAN><BR>
    <SPAN class="rcsid">HTBstat: %s</SPAN><BR>
""" % ( rcsid, rootclass.rcsid() )
# print ' -->'
print '</TABLE>'

# WOW! All is well.
