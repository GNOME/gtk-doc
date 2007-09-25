# -*- mode: makefile -*-

####################################
# Everything below here is generic #
####################################

if GTK_DOC_USE_LIBTOOL
GTKDOC_CC = $(LIBTOOL) --mode=compile $(CC) $(INCLUDES) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(LIBTOOL) --mode=link $(CC) $(AM_CFLAGS) $(CFLAGS) $(LDFLAGS)
else
GTKDOC_CC = $(CC) $(INCLUDES) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(CC) $(AM_CFLAGS) $(CFLAGS) $(LDFLAGS)
endif

# We set GPATH here; this gives us semantics for GNU make
# which are more like other make's VPATH, when it comes to
# whether a source that is a target of one rule is then
# searched for in VPATH/GPATH.
#
GPATH = $(srcdir)

TARGET_DIR=$(HTML_DIR)/$(DOC_MODULE)

EXTRA_DIST = 				\
	$(content_files)		\
	$(HTML_IMAGES)			\
	$(DOC_MAIN_SGML_FILE)		\
	$(DOC_MODULE)-sections.txt	\
	$(DOC_MODULE)-overrides.txt

DOC_STAMPS=scan-build.stamp tmpl-build.stamp sgml-build.stamp html-build.stamp \
	   $(srcdir)/tmpl.stamp $(srcdir)/sgml.stamp $(srcdir)/html.stamp

SCANOBJ_FILES = 		 \
	$(DOC_MODULE).args 	 \
	$(DOC_MODULE).hierarchy  \
	$(DOC_MODULE).interfaces \
	$(DOC_MODULE).prerequisites \
	$(DOC_MODULE).signals

REPORT_FILES = \
	$(DOC_MODULE)-undocumented.txt \
	$(DOC_MODULE)-undeclared.txt \
	$(DOC_MODULE)-unused.txt

CLEANFILES = $(SCANOBJ_FILES) $(REPORT_FILES) $(DOC_STAMPS)

if ENABLE_GTK_DOC
check-local: html-build.stamp
else
check-local:
endif

docs: html-build.stamp

#### scan ####

scan-build.stamp: $(HFILE_GLOB) $(CFILE_GLOB)
	@echo 'gtk-doc: Scanning header files'
	@-chmod -R u+w $(srcdir)
	if grep -l '^..*$$' $(srcdir)/$(DOC_MODULE).types > /dev/null 2>&1 ; then \
	    CC="$(GTKDOC_CC)" LD="$(GTKDOC_LD)" CFLAGS="$(GTKDOC_CFLAGS)" LDFLAGS="$(GTKDOC_LIBS)" $(top_builddir)/gtkdoc-scangobj --module=$(DOC_MODULE) --output-dir=$(srcdir) $(SCANGOBJ_OPTIONS) ; \
	else \
	    cd $(srcdir) ; \
	    for i in $(SCANOBJ_FILES) ; do \
               test -f $$i || touch $$i ; \
	    done \
	fi
	cd $(srcdir) && \
	PERL5LIB=$(top_builddir):$(PERL5LIB) $(top_builddir)/gtkdoc-scan --module=$(DOC_MODULE) --source-dir=$(DOC_SOURCE_DIR) --ignore-headers="$(IGNORE_HFILES)" $(EXTRA_HFILES) $(SCAN_OPTIONS)
	touch scan-build.stamp

$(DOC_MODULE)-decl.txt $(SCANOBJ_FILES): scan-build.stamp
	@true

#### templates ####

tmpl-build.stamp: $(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt
	@echo 'gtk-doc: Rebuilding template files'
	@-chmod -R u+w $(srcdir)
	cd $(srcdir) && \
    PERL5LIB=$(top_builddir):$(PERL5LIB) $(top_builddir)/gtkdoc-mktmpl --module=$(DOC_MODULE) $(MKTMPL_OPTIONS)
	touch tmpl-build.stamp

tmpl.stamp: tmpl-build.stamp
	@true

#### xml ####

sgml-build.stamp: $(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt $(expand_content_files)
	@echo 'gtk-doc: Building XML'
	@-chmod -R u+w $(srcdir)
	cd $(srcdir) && \
	PERL5LIB=$(top_builddir):$(PERL5LIB) $(top_builddir)/gtkdoc-mkdb --module=$(DOC_MODULE) --source-dir=$(DOC_SOURCE_DIR) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $(MKDB_OPTIONS)
	touch sgml-build.stamp

sgml.stamp: sgml-build.stamp
	@true

#### html ####

html-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@echo 'gtk-doc: Building HTML'
	@-chmod -R u+w $(srcdir)
	rm -rf $(srcdir)/html
	mkdir $(srcdir)/html
	cd $(srcdir)/html && \
    PERL5LIB=$(top_builddir):$(PERL5LIB) ../$(top_builddir)/gtkdoc-mkhtml $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE)  $(MKHTML_OPTIONS)
	test "x$(HTML_IMAGES)" = "x" || ( cd $(srcdir) && cp $(HTML_IMAGES) html )
	@echo 'gtk-doc: Fixing cross-references'
	cd $(srcdir) && \
    PERL5LIB=$(top_builddir):$(PERL5LIB) $(top_builddir)/gtkdoc-fixxref --module-dir=html $(FIXXREF_OPTIONS)
	touch html-build.stamp

##############

clean-local:
	rm -f *~ *.bak
	rm -rf .libs

distclean-local:
	cd $(srcdir) && \
	  rm -rf xml $(REPORT_FILES) \
	         $(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt

maintainer-clean-local: clean
	cd $(srcdir) && rm -rf html \
	$(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt $(REPORT_FILES)

dist-hook: dist-hook-local
	if test -f $(srcdir)/$(DOC_MODULE).types; then \
	  cp $(srcdir)/$(DOC_MODULE).types $(distdir)/$(DOC_MODULE).types; \
	fi

.PHONY : dist-hook-local
