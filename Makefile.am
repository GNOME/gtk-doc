## Process this file with automake to produce Makefile.in

bin_SCRIPTS = \
	gtkdoc-scanobj  \
	gtkdoc-scangobj \
	gtkdoc-scan     \
	gtkdoc-mktmpl   \
	gtkdoc-mkdb     \
	gtkdoc-mkhtml   \
	gtkdoc-mkman    \
	gtkdoc-fixxref  \
	gtkdocize

gtkdocdatadir = $(datadir)/gtk-doc/data
gtkdocdata_DATA = \
	gtkdoc-common.pl	\
        gtk-doc.dsl		\
	gtk-doc.dcl		\
	gtk-doc.xsl		\
	devhelp.xsl		\
	gtk-doc.make		\
	home.png		\
	left.png		\
	right.png		\
	up.png

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = gtk-doc.pc

aclocaldir = $(datadir)/aclocal
aclocal_DATA = gtk-doc.m4

EXTRA_DIST = \
  MAINTAINERS     \
  gtk-doc.pc.in   \
  gtk-doc.m4      \
  gtk-doc.spec.in \
  gtk-doc.spec    \
  gtk-doc.dcl     \
  gtk-doc.xsl     \
  devhelp.xsl     \
  home.png  \
  left.png  \
  right.png \
  up.png    \
  doc/README            \
  doc/authors.txt       \
  doc/gnome.txt         \
  doc/sections-file.txt \
  doc/setting-up.txt    \
  doc/style-guide.txt   \
  db2man/README            \
  db2man/docbook-to-man    \
  db2man/docbook-to-man.ts \
  examples/README       \
  examples/Makefile.am  \
  examples/configure.in \
  tools/docpercentages.pl \
  tools/gtk-doc.el
