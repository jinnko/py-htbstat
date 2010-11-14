#
#
# $Id: htbstat.cgi,v 1.5 2008/01/16 10:27:46 dima Exp $
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

#
# This config file is used by CGI scripts.
#

# comment/uncomment to disable/enable fancy cgi debug:
import cgitb; cgitb.enable()

#
# Page title and header (will appear on HTML page):
pagetitle = 'HTB Statistics'
pageheader = 'Detailed HTB Statistics'

#
# INTERFACES.
#
# Specify only one device name, only one RRD path -- if you have one HTB
# managed interface.
#
# You can specify two interfaces, if you have configured linux box with two
# HTB managed interfaces *with two symmetrical HTB hierarchies*. If those
# configurations are not symmetrical, you should better create two different
# configurations and CGI scripts sets.
#
# If you specify two interfaces -- graphs with `bytes transferred' will
# contain two values, area and line, MRTG like.
#
# HTB can manage *output* traffic only. And py-htbstat was developed to deal
# with at most two interfaces (think of ethernet switch) -- input and
# output. However, You know, both of them are *output* interfaces from HTB's
# point of view.
#
# So, please, dont be confused with names :-)
#
# It's just a names, to manage cgi script and html output.
#
# Device name may be any reasonable string:
devone = 'eth1'
#devtwo = ''
#
# Interfaces names (will appear on HTML page):
# devonename = 'Local Network'
# devtwoname = 'To Internet'
devonename = 'WAN traffic'
#devtwoname = 'Other traffic'


# RRD bases pathes.
# Must be real pathes to rrdbases. Don't fool yourself.
# Must be readable for apache user.
# rrdONEpath = '/var/spool/htbstat/' + devone
# rrdTWOpath = '/var/spool/htbstat/' + devtwo
rrdONEpath = '/var/lib/htbstat'
#rrdTWOpath = '/var/lib/htbstat/rrdbases/%s' % devtwo

# Path where generated pictures will be put to (check permissions!):
picpath = '/var/www/html/htb/pictures'

# Path html links will point to:
wwwpicpath = '/htb/pictures'

# Default class to be displayed, when none specified:
defclid = '1:4'

# This is you root class (change it if you need):
defroot = '1:2'


##########################################################
#
execfile('/etc/htbstat/functions')
#
##########################################################
