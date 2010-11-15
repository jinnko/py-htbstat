#!/usr/bin/python
#
#
# $Id: dumpclass.py,v 1.9 2008/01/16 10:39:10 dima Exp $
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

rcsid = '$Id: dumpclass.py,v 1.9 2008/01/16 10:39:10 dima Exp $'

import cgi

import rrdtool
import os
import re
import glob

import pickle
import md5

import HTBstat

# config file:
execfile('/etc/htbstat/htbstat.cgi')

remaddr = os.getenv("REMOTE_ADDR")

######################################################################

#
# twidding with cgi:
#
F = cgi.FieldStorage()


# get CGI values from the form:
dev, clid = F.getvalue("dev"), F.getvalue("clid")

if dev not in (devone, devtwo):
    if devone != disabled:
        dev = devone
        devname = devonename
    else:
        dev = devtwo
        devname = devtwoname
else:
    devname = (dev == devone) and devonename or devtwoname

if not clid: clid = defclid

#
# all cgi values are set.
#

if dev == devtwo:
    rrdpath = rrdTWOpath
else:
    rrdpath = rrdONEpath

#
# list of classes
# and loading classes:
clfiles = glob.glob('%s/*.pickle' % rrdpath)
allclasses = []
classes = {}

for cls in clfiles:
    namepat = re.search('([0-9]+:[0-9]+).pickle', cls)
    namestr = namepat.group(1)
    classes[namestr] = namestr
    classfile = open(cls, 'r')
    thisclass = pickle.load(classfile)
    allclasses.append(thisclass)
    classfile.close()

######################################################################

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
 <TITLE>HTB Class Dumper</TITLE>
 <!-- LINK rel="stylesheet" type="text/css" href="/admin.css" -->
 <STYLE type="text/css">
        PRE     {
                text-align: left;
        }
        SPAN.term {
                font-family: 'Fixed', 'Courier New';
        }
        SPAN.rcsid {
                font-family: 'Fixed', 'Courier New'; 
                font-size: 70%;
        }
 </STYLE>
<BODY>
"""

print """
<FORM>
<TABLE border="1">
<TR>
"""

if disabled not in (devone, devtwo):
    print '<TH>Select source:'
else:
    print '<TH rowspan="2">%s: &nbsp;' % devname

print """
  <TH>Class to display:
  <TH rowspan="2">&nbsp;<INPUT type="submit" value="Update">&nbsp;
  <TR><TD><TABLE border="1" align="center">
"""


if disabled not in (devone, devtwo):
    if dev == devone: 
        print '<TR><TD>'
        print '<INPUT type="radio" name="dev" value="%s" checked>' % devone
        print devonename
        if devtwo != disabled:
            print '<TD>'
            print '<INPUT type="radio" name="dev" value="%s">' % devtwo
            print devtwoname

    elif dev == devtwo:
        if devone != disabled:
            print '<TR><TD>'
            print '<INPUT type="radio" name="dev" value="%s">' % devone
            print devonename
        print '<TD>'
        print '<INPUT type="radio" name="dev" value="%s" checked>' % devtwo
        print devtwoname
else:
    printSelect(classes, 'clid', clid)

print '</TABLE>'

if disabled not in (devone, devtwo):
    print '<TD align="center">%s' % getSelect(classes, 'clid', clid)

print """
</TABLE>
</FORM>
"""

htb = getbyclid(allclasses, clid)

print '<PRE>\n%s\n</PRE>\n' % htb.dump()

print '<HR>\n'

cmdin, cmdout, cmderr = \
   os.popen3('/sbin/tc -s -d class show dev %s | grep -A 4 " htb %s "' % (dev, clid) )

error = cmderr.read()
clidstat = cmdout.read()

if error not in (None, ''):
    print '<PRE>%s</PRE>' % error
else:
    if clidstat in (None, ''):
        print '<PRE>Class does not exist.'
        print 'Are your classes configured in this machine\'s kernel?</PRE>'

print '<PRE>%s</PRE>\n' % clidstat

cmdout.close()
cmdin.close()

print """
<HR>
<TABLE border="0" width="90%" align="center">
<TR><TD>
<SPAN class="rcsid">Copyright (c) 2005&ndash;2008 <A href="mailto:%s@%s.%s.%s">Dmytro O. Redchuk</A></SPAN><BR>
<SPAN class="rcsid">Copyright (c) 2005&ndash;2008 <A href="http://www.volz.ua/">VOLZ Llc</A></SPAN><BR>
""" % ('dmytro', 'redchuck', 'org', 'ua')

# print '<!-- '
print """
<TD align="right">\n<SPAN class="rcsid">dumpclass.py: %s</SPAN><BR>
<SPAN class="rcsid">HTBstat: %s</SPAN><BR>
""" % ( rcsid, htb.rcsid() )
# print ' -->'
print '</TABLE>'

# WOW! All is well.
