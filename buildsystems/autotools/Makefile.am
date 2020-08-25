EXTRA_DIST = \
	$(autotoolsdata_DATA) \
	gtk-doc.m4 \
	meson.build

CLEANFILES = gtk-doc.flat.make gtk-doc.no-xslt-flat.make

bin_SCRIPTS = gtkdocize

autotoolsdatadir = $(datadir)/gtk-doc/data
autotoolsdata_DATA = \
	gtk-doc.make \
	gtk-doc.flat.make \
	gtk-doc.no-xslt.make \
	gtk-doc.no-xslt-flat.make

aclocaldir = $(datadir)/aclocal
aclocal_DATA = gtk-doc.m4

gtk-doc.flat.make: gtk-doc.make
	@$(SED) -e "s/EXTRA_DIST =/EXTRA_DIST +=/" $< >$@

gtk-doc.no-xslt-flat.make: gtk-doc.no-xslt.make
	@$(SED) -e "s/EXTRA_DIST =/EXTRA_DIST +=/" $< >$@

-include $(top_srcdir)/git.mk
