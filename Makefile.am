## Process this file with automake to produce Makefile.in

bin_SCRIPTS = \
	gtkdoc-scanobj \
	gtkdoc-scan    \
	gtkdoc-mktmpl  \
	gtkdoc-mkdb    \
	gtkdoc-mkhtml  \
	gtkdoc-mkman   \
	gtkdoc-fixxref
	 
gtkdocdatadir = $(datadir)/gtk-doc
gtkdocdata_DATA = \
        gtk-doc.dsl

#EXTRA_DIST=gtk-doc.spec.in

dist-hook:
	mkdir $(distdir)/doc
	cp -pr $(srcdir)/doc/* $(distdir)/doc
	mkdir $(distdir)/db2man
	cp -pr $(srcdir)/db2man/* $(distdir)/db2man
	mkdir $(distdir)/examples
	cp -pr $(srcdir)/examples/* $(distdir)/examples
#	cp gtk-doc.spec $(distdir)
