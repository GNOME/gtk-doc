## Process this file with automake to produce Makefile.in

bin_SCRIPTS = \
	gtkdoc-scanobj  \
	gtkdoc-scangobj \
	gtkdoc-scan     \
	gtkdoc-mktmpl   \
	gtkdoc-mkdb     \
	gtkdoc-mkhtml   \
	gtkdoc-mkman    \
	gtkdoc-fixxref

gtkdocdatadir = $(datadir)/gtk-doc
gtkdocdata_DATA = \
	gtkdoc-common.pl	\
        gtk-doc.dsl		\
	gtk-doc.dcl		\
	gtk-doc.xsl		\
	devhelp.xsl		\
	xml.dcl			\
	home.png		\
	left.png		\
	right.png		\
	up.png

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = gtk-doc.pc

EXTRA_DIST= \
	MAINTAINERS	\
	gtk-doc.pc.in	\
	gtk-doc.spec.in	\
	gtk-doc.dcl  	\
	gtk-doc.xsl	\
	devhelp.xsl	\
	xml.dcl		\
	home.png	\
	left.png	\
	right.png	\
	up.png


dist-hook:
	mkdir $(distdir)/doc
	cp -pr $(srcdir)/doc/* $(distdir)/doc
	rm -rf $(distdir)/doc/CVS
	mkdir $(distdir)/db2man
	cp -pr $(srcdir)/db2man/* $(distdir)/db2man
	rm -rf $(distdir)/db2man/CVS
	mkdir $(distdir)/examples
	cp -pr $(srcdir)/examples/* $(distdir)/examples
	rm -rf $(distdir)/examples/CVS
	mkdir $(distdir)/tools
	cp -pr $(srcdir)/tools/* $(distdir)/tools
	rm -rf $(distdir)/tools/CVS
	cp gtk-doc.spec $(distdir)

