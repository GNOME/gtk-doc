## Process this file with automake to produce Makefile.in

SUBDIRS = help/manual/C

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
	version-greater-or-equal.xsl \
	devhelp.xsl		\
	devhelp2.xsl		\
	gtk-doc.make		\
	home.png		\
	left.png		\
	right.png		\
	up.png			\
	style.css

pkgconfigdir = $(datadir)/pkgconfig
pkgconfig_DATA = gtk-doc.pc

aclocaldir = $(datadir)/aclocal
aclocal_DATA = gtk-doc.m4

sgmldir = $(datadir)/sgml/gtk-doc
sgml_DATA = gtk-doc.cat

EXTRA_DIST = \
  MAINTAINERS     \
  gtk-doc.pc.in   \
  gtk-doc.m4      \
  gtk-doc.make    \
  gtk-doc.spec.in \
  gtk-doc.spec    \
  gtk-doc.dcl     \
  gtk-doc.xsl     \
  version-greater-or-equal.xsl \
  devhelp.xsl     \
  devhelp2.xsl     \
  gtk-doc.cat.in  \
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
  tools/docpercentages.pl \
  tools/gtk-doc.el \
  style.css \
  COPYING-DOCS \
  omf.make \
  xmldocs.make
