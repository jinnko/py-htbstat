Name: py-htbstat
Version: 0.2.1
Release: dor3

Summary: Python module HTBstat and (CGI and shell) scripts to collect and analyze HTB statistics.
License: GPL
Group: Networking/Tools
Requires: python-base py-rrdtool
Packager: Dmytro O. Redchuk <dor(at)ldc.net>
Url: http://www2.ldc.net/~dor

Source: %{name}-%{version}.src.tar.bz2

Provides: python(HTBstat)

%define python_libdir %_libdir/python%__python_version

# Automatically added by buildreq on Thu Apr 14 2005 (-ba)
BuildRequires: python-base python-modules-compiler python-modules-encodings rpm-build-python

%description
Python module HTBstat and (CGI and shell) scripts to collect and
analyze HTB statistics.

Uses py-rrdtool to work with RRD bases.

%prep
%setup

%install
mkdir -p $RPM_BUILD_ROOT/%python_libdir/site-packages/HTBstat
cp HTBstat/*.py $RPM_BUILD_ROOT/%python_libdir/site-packages/HTBstat

mkdir -p $RPM_BUILD_ROOT/usr/bin
cp bin/statsfill.py $RPM_BUILD_ROOT/usr/bin/htbstatsfill.py

mkdir -p $RPM_BUILD_ROOT/etc/htbstat
cp etc/htbstat.conf etc/htbstat.cgi etc/functions $RPM_BUILD_ROOT/etc/htbstat

mkdir -p $RPM_BUILD_ROOT/var/www/cgi-bin
cp cgi-bin/htbstat.py cgi-bin/htbcheck.py cgi-bin/dumpclass.py cgi-bin/htbstatpic.py\
	$RPM_BUILD_ROOT/var/www/cgi-bin

mkdir -p $RPM_BUILD_ROOT/usr/share/doc/%{name}-%{version}
cp -r doc/* $RPM_BUILD_ROOT/usr/share/doc/%{name}-%{version}

%files
%dir /%python_libdir/site-packages/HTBstat
/%python_libdir/site-packages/HTBstat/*.py
/%python_libdir/site-packages/HTBstat/*.pyc
/usr/bin/*.py
%dir /etc/htbstat
/etc/htbstat/*
%docdir /usr/share/doc/%{name}-%{version}
/usr/share/doc/%{name}-%{version}
/var/www/cgi-bin/*

%changelog
* Wed Sep 27 2006 Dmytro O. Redchuk <dor(at)ldc.net> 0.2.1-dor3
- Made it possible to use xxxx:xxxx classids.

* Fri Dec 16 2005 Dmytro O. Redchuk <dor(at)ldc.net> 0.2-dor1
- Changed method of setting graph upper limit
  (was: rrdtool's LIMIT, now: -u [-r])
- Added wwwpicpath to cgi config file.
- Added htbstatpic.py for getting single picture (png format).

* Thu Mar 24 2005 Dmytro O. Redchuk <dor(at)ldc.net> 0.1-dor1
- Initial build.

