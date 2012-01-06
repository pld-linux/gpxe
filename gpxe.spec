Summary:	A network boot loader
Name:		gpxe
Version:	1.0.1
Release:	4
License:	GPL v2 and BSD
Group:		Base
URL:		http://www.etherboot.org/
Source0:	http://etherboot.org/rel/gpxe/%{name}-%{version}.tar.bz2
# Source0-md5:	38ae67a440abd2aea139495022ee4912
# extracted from echos of src/Makefile
Source1:	USAGE
Patch1:		virtionet-length.patch
BuildRequires:	mkisofs
BuildRequires:	mtools
BuildRequires:	perl-base
BuildRequires:	syslinux
BuildArch:	noarch
#ExclusiveArch:%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define formats rom

# ne is only for backwards compat with older versions of qemu
%define qemuroms rtl8029 ne 8086100e pcnet32 rtl8139 virtio-net

%description
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

%package bootimgs
Summary:	Network boot loader images in bootable USB, CD, floppy and GRUB formats
Group:		Development/Tools

%package roms
Summary:	Network boot loader roms in .rom format
Group:		Development/Tools
Requires:	%{name}-roms-qemu = %{version}-%{release}

%description roms
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the gPXE roms in .rom format.

%package roms-qemu
Summary:	Network boot loader roms supported by QEMU, .rom format
Group:		Development/Tools

%description bootimgs
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the gPXE boot images in USB, CD, floppy, and PXE
UNDI formats.

%description roms-qemu
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the gPXE ROMs for devices emulated by QEMU, in
.rom format.

%prep
%setup -q
%patch1 -p1
cp -p %{SOURCE1} .

%build
ISOLINUX_BIN=%{_datadir}/syslinux/isolinux.bin
cd src
# NO_WERROR is needed because of bogus (for us) error: variable '__table_entries' set but not used [-Werror=unused-but-set-variable]
%{__make} ISOLINUX_BIN=$ISOLINUX_BIN NO_WERROR=1
%{__make} bin/gpxe.lkrn
%{__make} allroms

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}

cd src/bin
cp -p undionly.kpxe gpxe.{iso,usb,dsk,lkrn} $RPM_BUILD_ROOT%{_datadir}/%{name}
for fmt in %{formats}; do
	for img in *.${fmt}; do
		if [ -e $img ]; then
			cp -p $img $RPM_BUILD_ROOT%{_datadir}/%{name}
			echo %{_datadir}/%{name}/$img >> ../../${fmt}.list
		fi
	done
done
cd -

# the roms supported by qemu will be packaged separatedly
# remove from the main rom list and add them to qemu.list
for fmt in rom; do
	for rom in %{qemuroms}; do
		sed -i -e "/\/$rom.$fmt/d" $fmt.list
		echo %{_datadir}/%{name}/$rom.$fmt >> qemu.$fmt.list
	done
done

%clean
rm -rf $RPM_BUILD_ROOT

%files bootimgs
%defattr(644,root,root,755)
%doc COPYING COPYRIGHTS USAGE
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/gpxe.iso
%{_datadir}/%{name}/gpxe.usb
%{_datadir}/%{name}/gpxe.dsk
%{_datadir}/%{name}/gpxe.lkrn
%{_datadir}/%{name}/undionly.kpxe

%files roms -f rom.list
%defattr(644,root,root,755)
%dir %{_datadir}/%{name}

%files roms-qemu -f qemu.rom.list
%defattr(644,root,root,755)
%dir %{_datadir}/%{name}
