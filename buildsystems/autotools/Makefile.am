EXTRA_DIST = \
	$(autotoolsdata_DATA) \
	gtk-doc.m4

CLEANFILES = gtk-doc.flat.make

bin_SCRIPTS = gtkdocize

autotoolsdatadir = $(datadir)/gtk-doc/data
autotoolsdata_DATA = \
	gtk-doc.make		\
	gtk-doc.flat.make

aclocaldir = $(datadir)/aclocal
aclocal_DATA = gtk-doc.m4

gtk-doc.flat.make: gtk-doc.make
	@$(SED) -e "s/EXTRA_DIST =/EXTRA_DIST +=/" $< >$@

-include $(top_srcdir)/git.mk
