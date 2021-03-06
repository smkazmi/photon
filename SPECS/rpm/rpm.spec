%{!?python2_sitelib: %define python2_sitelib %(python2 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
%{!?python3_sitelib: %define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}

Summary:        Package manager
Name:           rpm
Version:        4.14.0
Release:        1%{?dist}
License:        GPLv2+
URL:            http://rpm.org
Group:          Applications/System
Vendor:         VMware, Inc.
Distribution:   Photon
Source0:        https://github.com/rpm-software-management/rpm/archive/%{name}-%{version}.tar.bz2
%define sha1    rpm=b15344d67b1bf4b15498efa3667f2ad5de40623f
Source1:        macros
Source2:        brp-strip-debug-symbols
Source3:        brp-strip-unneeded
Source4:        convert_bdb_to_lmdb.sh
Patch0:         find-debuginfo-do-not-generate-dir-entries.patch
Patch1:         rpm-use-lmdb.patch
Requires:       bash
Requires:       rpm-libs = %{version}-%{release}
Requires:       libarchive
BuildRequires:  libarchive-devel
BuildRequires:  lmdb-devel
BuildRequires:  popt-devel
BuildRequires:  nss-devel
BuildRequires:  elfutils-devel
BuildRequires:  libcap-devel
BuildRequires:  xz-devel
BuildRequires:  file-devel

%description
RPM package manager

%package devel
Summary:        Libraries and header files for rpm
Provides:       pkgconfig(rpm)
Requires:       %{name} = %{version}-%{release}
Requires:       lmdb-devel
%description devel
Static libraries and header files for the support library for rpm

%package libs
Summary:        Libraries for rpm
Requires:       nss-libs
Requires:       popt
Requires:       libgcc
Requires:       libcap
Requires:       zlib
Requires:       bzip2-libs
Requires:       elfutils-libelf
Requires:       xz-libs
Requires:       lmdb
%description    libs
Shared libraries librpm and librpmio

%package build
Requires:       perl
Requires:       %{name}-devel = %{version}-%{release}
Requires:       elfutils-libelf
Summary: Binaries, scripts and libraries needed to build rpms.
%description build
Binaries, libraries and scripts to build rpms.

%package lang
Summary:        Additional language files for rpm
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
%description lang
These are the additional language files of rpm.

%package -n     python-rpm
Summary:        Python 2 bindings for rpm.
Group:          Development/Libraries
BuildRequires:  python2-devel
Requires:       python2
%description -n python-rpm

%package -n     python3-rpm
Summary:        Python 3 bindings for rpm.
Group:          Development/Libraries
BuildRequires:  python3-devel
Requires:       python3

%description -n python3-rpm
Python3 rpm.

%package convert-db
Summary:        Tools to convert bdb to lmdb
Group:          Applications/Utilities
Requires:       libdb-utils
Requires:       lmdb
%description convert-db
Tools to convert existing rpm db from bdb to lmdb.

%prep
%setup -n %{name}-%{version}
%patch0 -p1
%patch1 -p1

%build
sed -i '/define _GNU_SOURCE/a #include "../config.h"' tools/sepdebugcrcfix.c
# pass -L opts to gcc as well to prioritize it over standard libs
sed -i 's/-Wl,-L//g' python/setup.py.in
sed -i 's/extra_link_args/library_dirs/g' python/setup.py.in
sed -i 's/_db_backend\s*bdb/_db_backend lmdb/' macros.in

./autogen.sh --noconfigure
./configure \
    CPPFLAGS='-I/usr/include/nspr -I/usr/include/nss -DLUA_COMPAT_APIINTCASTS' \
        --program-prefix= \
        --prefix=%{_prefix} \
        --exec-prefix=%{_prefix} \
        --bindir=%{_bindir} \
        --sbindir=%{_sbindir} \
        --sysconfdir=%{_sysconfdir} \
        --datadir=%{_datadir} \
        --includedir=%{_includedir} \
        --libdir=%{_libdir} \
        --libexecdir=%{_libexecdir} \
        --localstatedir=%{_var} \
        --sharedstatedir=%{_sharedstatedir} \
        --mandir=%{_mandir} \
        --infodir=%{_infodir} \
        --disable-dependency-tracking \
        --disable-static \
        --enable-python \
        --with-cap \
        --without-lua \
        --disable-silent-rules \
        --disable-bdb \
        --enable-lmdb
make %{?_smp_mflags}

pushd python
python2 setup.py build
python3 setup.py build
popd

%check
make check

%install
make DESTDIR=%{buildroot} install
find %{buildroot} -name '*.la' -delete
%find_lang %{name}
# System macros and prefix
install -dm 755 %{buildroot}%{_sysconfdir}/rpm
install -vm644 %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/
install -vm755 %{SOURCE2} %{buildroot}%{_libdir}/rpm/
install -vm755 %{SOURCE3} %{buildroot}%{_libdir}/rpm/
install -vm744 %{SOURCE4} %{buildroot}%{_bindir}

pushd python
python2 setup.py install --skip-build --prefix=%{_prefix} --root=%{buildroot}
python3 setup.py install --skip-build --prefix=%{_prefix} --root=%{buildroot}
popd

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/rpm
%{_bindir}/gendiff
%{_bindir}/rpm2archive
%{_bindir}/rpm2cpio
%{_bindir}/rpmdb
%{_bindir}/rpmgraph
%{_bindir}/rpmkeys
%{_bindir}/rpmquery
%{_bindir}/rpmverify

%{_libdir}/rpm/rpmpopt-*
%{_libdir}/rpm/rpmdb_*
%{_libdir}/rpm/rpm.daily
%{_libdir}/rpm/rpm.log
%{_libdir}/rpm/rpm.supp
%{_libdir}/rpm/rpm2cpio.sh
%{_libdir}/rpm/tgpg
%{_libdir}/rpm/platform
%{_libdir}/rpm-plugins/*
%{_mandir}/man8/rpm.8.gz
%{_mandir}/man8/rpm2cpio.8.gz
%{_mandir}/man8/rpmdb.8.gz
%{_mandir}/man8/rpmgraph.8.gz
%{_mandir}/man8/rpmkeys.8.gz
%exclude %{_mandir}/fr/man8/*.gz
%exclude %{_mandir}/ja/man8/*.gz
%exclude %{_mandir}/ko/man8/*.gz
%exclude %{_mandir}/pl/man1/*.gz
%exclude %{_mandir}/pl/man8/*.gz
%exclude %{_mandir}/ru/man8/*.gz
%exclude %{_mandir}/sk/man8/*.gz

%files libs
%defattr(-,root,root)
%{_sysconfdir}/rpm/macros
%{_libdir}/librpmio.so.*
%{_libdir}/librpm.so.*
%{_libdir}/rpm/macros
%{_libdir}/rpm/rpmrc
%{_libdir}/rpm/platform/*

%files build
%{_bindir}/rpmbuild
%{_bindir}/rpmsign
%{_bindir}/rpmspec
%{_libdir}/librpmbuild.so
%{_libdir}/librpmbuild.so.*
%{_libdir}/rpm/macros.*
%{_libdir}/rpm/perl.req
%{_libdir}/rpm/find-debuginfo.sh
%{_libdir}/rpm/find-lang.sh
%{_libdir}/rpm/find-provides
%{_libdir}/rpm/find-requires
%{_libdir}/rpm/brp-*
%{_libdir}/rpm/mono-find-provides
%{_libdir}/rpm/mono-find-requires
%{_libdir}/rpm/ocaml-find-provides.sh
%{_libdir}/rpm/ocaml-find-requires.sh
%{_libdir}/rpm/fileattrs/*
%{_libdir}/rpm/script.req
%{_libdir}/rpm/check-buildroot
%{_libdir}/rpm/check-files
%{_libdir}/rpm/check-prereqs
%{_libdir}/rpm/check-rpaths
%{_libdir}/rpm/check-rpaths-worker
%{_libdir}/rpm/config.guess
%{_libdir}/rpm/config.sub
%{_libdir}/rpm/debugedit
%{_libdir}/rpm/elfdeps
%{_libdir}/rpm/libtooldeps.sh
%{_libdir}/rpm/mkinstalldirs
%{_libdir}/rpm/pkgconfigdeps.sh
%{_libdir}/rpm/*.prov
%{_libdir}/rpm/sepdebugcrcfix


%{_libdir}/rpm/pythondeps.sh
%{_libdir}/rpm/rpmdeps
%{_libdir}/rpm/pythondistdeps.py

%{_mandir}/man1/gendiff.1*
%{_mandir}/man8/rpmbuild.8*
%{_mandir}/man8/rpmdeps.8*
%{_mandir}/man8/rpmspec.8*
%{_mandir}/man8/rpmsign.8.gz
%{_mandir}/man8/rpm-misc.8.gz
%{_mandir}/man8/rpm-plugin-systemd-inhibit.8.gz

%files devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/pkgconfig/rpm.pc
%{_libdir}/librpmio.so
%{_libdir}/librpm.so
%{_libdir}/librpmsign.so
%{_libdir}/librpmsign.so.*

%files lang -f %{name}.lang
%defattr(-,root,root)

%files -n python-rpm
%defattr(-,root,root)
%{python2_sitelib}/*

%files -n python3-rpm
%defattr(-,root,root)
%{python3_sitelib}/*

%files convert-db
%defattr(-,root,root)
%{_bindir}/convert_bdb_to_lmdb.sh

%changelog
*   Fri Dec 15 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.14.0-1
-   Update to 4.14.0, remove bdb dependences and use lmdb.
*   Wed Oct 04 2017 Alexey Makhalov <amakhalov@vmware.com> 4.13.0.1-6
-   make python{,3}-rpm depend on current version of librpm
*   Wed Jun 28 2017 Xiaolin Li <xiaolinl@vmware.com> 4.13.0.1-5
-   Add file-devel to BuildRequires
*   Mon Jun 26 2017 Chang Lee <changlee@vmware.com> 4.13.0.1-4
-   Updated %check
*   Mon Jun 05 2017 Bo Gan <ganb@vmware.com> 4.13.0.1-3
-   Fix Dependency
*   Thu May 18 2017 Xiaolin Li <xiaolinl@vmware.com> 4.13.0.1-2
-   Remove python2 from requires of rpm-devel subpackages.
*   Wed May 10 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.13.0.1-1
-   Update to 4.13.0.1
*   Fri Apr 21 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.13.0-1
-   Update to 4.13.0
*   Wed Apr 19 2017 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-22
-   Do not allow -debuginfo to own directories to avoid conflicts with
    filesystem package and between each other. Patch applied
*   Fri Apr 14 2017 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-21
-   rpm-libs requires nss-libs, xz-libs and bzip2-libs.
*   Tue Mar 21 2017 Xiaolin Li <xiaolinl@vmware.com> 4.11.2-20
-   Added python3 packages and moved python2 site packages from devel to python-rpm.
*   Mon Jan 10 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.11.2-19
-   added buildrequires for xz-devel for PayloadIsLzma cap
*   Thu Dec 15 2016 Xiaolin Li <xiaolinl@vmware.com> 4.11.2-18
-   Moved some files from rpm to rpm-build.
*   Tue Dec 06 2016 Xiaolin Li <xiaolinl@vmware.com> 4.11.2-17
-   Added -lang subpackage.
*   Wed Nov 23 2016 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-16
-   Move rpmrc and macros into -libs subpackage
-   Move zlib and elfutils-libelf dependency from rpm to rpm-libs
-   Add bzip2 dependency to rpm-libs
*   Thu Nov 17 2016 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-15
-   Added -libs subpackage
*   Tue Nov 15 2016 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-14
-   Disable lua support
*   Tue Oct 18 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.11.2-13
-   Apply patch for CVE-2014-8118
*   Wed Oct 05 2016 ChangLee <changlee@vmware.com> 4.11.2-12
-   Modified %check
*   Fri Aug 26 2016 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-11
-   find-debuginfo...patch: exclude non existing .build-id from packaging
-   Move all files from rpm-system-configuring-scripts tarball to here 
*   Wed May 25 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.11.2-10
-   Exclude .build-id/.1 and .build-id/.1.debug from debuginfo pkg
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.11.2-9
-   GA - Bump release of all rpms
*   Thu May 05 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 4.11.2-8
-   Update rpm version in lock-step with lua update to 5.3.2
*   Fri Apr 08 2016 Mahmoud Bassiouny <mbassiouny@vmware.com> 4.11.2-7
-   Build rpm with capabilities.
*   Thu Aug 05 2015 Sharath George <sharathg@vmware.com> 4.11.2-6
-   Moving build utils to a different package.
*   Sat Jun 27 2015 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-5
-   Update rpm-system-configuring-scripts. Use tar --no-same-owner for rpmbuild.
*   Thu Jun 18 2015 Anish Swaminathan <anishs@vmware.com> 4.11.2-4
-   Add pkgconfig Provides directive
*   Thu Jun 18 2015 Alexey Makhalov <amakhalov@vmware.com> 4.11.2-3
-   Do no strip debug info from .debug files
*   Wed Jun 3 2015 Divya Thaluru <dthaluru@vmware.com> 4.11.2-2
-   Removing perl-module-scandeps package from run time required packages
*   Tue Jan 13 2015 Divya Thaluru <dthaluru@vmware.com> 4.11.2-1
-   Initial build. First version
