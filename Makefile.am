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

dist-hook:
	mkdir $(distdir)/doc
	cp -pr doc/* $(distdir)/doc
	mkdir $(distdir)/db2man
	cp -pr db2man/* $(distdir)/db2man
	mkdir $(distdir)/examples
	cp -pr examples/* $(distdir)/examples
