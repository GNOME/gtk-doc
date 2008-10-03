# -*- mode: makefile -*-

####################################
# Everything below here is generic #
####################################

if GTK_DOC_USE_LIBTOOL
GTKDOC_CC = $(LIBTOOL) --mode=compile $(CC) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(LIBTOOL) --mode=link $(CC) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS)
GTKDOC_RUN = $(LIBTOOL) --mode=execute
else
GTKDOC_CC = $(CC) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(CC) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS)
GTKDOC_RUN = 
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

DOC_STAMPS=scan-build.stamp sgml-build.stamp html-build.stamp \
	   $(srcdir)/sgml.stamp $(srcdir)/html.stamp

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

check-local: html-build.stamp

docs: html-build.stamp

$(REPORT_FILES): sgml-build.stamp

#### scan ####

scan-build.stamp: $(HFILE_GLOB) $(CFILE_GLOB)
	@echo 'gtk-doc: Scanning header files'
	@-chmod -R u+w $(srcdir)
	@PATH=$(top_builddir):$(PATH) PERL5LIB=$(top_builddir):$(PERL5LIB) && cd $(srcdir) && \
	  gtkdoc-scan --module=$(DOC_MODULE) --source-dir=$(DOC_SOURCE_DIR) --ignore-headers="$(IGNORE_HFILES)" $(SCAN_OPTIONS) $(EXTRA_HFILES)
	if grep -l '^..*$$' $(srcdir)/$(DOC_MODULE).types > /dev/null 2>&1 ; then \
	    CC="$(GTKDOC_CC)" LD="$(GTKDOC_LD)" RUN="$(GTKDOC_RUN)" CFLAGS="$(GTKDOC_CFLAGS) $(CFLAGS)" LDFLAGS="$(GTKDOC_LIBS) $(LDFLAGS)" $(top_builddir)/gtkdoc-scangobj --module=$(DOC_MODULE) --output-dir=$(srcdir) $(SCANGOBJ_OPTIONS); \
	else \
	    cd $(srcdir) ; \
	    for i in $(SCANOBJ_FILES) ; do \
               test -f $$i || touch $$i ; \
	    done \
	fi
	touch scan-build.stamp

$(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt: scan-build.stamp
	@true

#### xml ####

sgml-build.stamp: $(HFILE_GLOB) $(CFILE_GLOB) $(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt $(expand_content_files)
	@echo 'gtk-doc: Building XML'
	@-chmod -R u+w $(srcdir)
	@PATH=$(top_builddir):$(PATH) PERL5LIB=$(top_builddir):$(PERL5LIB) && cd $(srcdir) && \
	gtkdoc-mkdb --module=$(DOC_MODULE) --source-dir=$(DOC_SOURCE_DIR) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $(MKDB_OPTIONS)
	touch sgml-build.stamp

sgml.stamp: sgml-build.stamp
	@true

#### html ####

html-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@echo 'gtk-doc: Building HTML'
	@-chmod -R u+w $(srcdir)
	rm -rf $(srcdir)/html
	mkdir $(srcdir)/html
	@PATH=$(top_builddir):$(PATH) PERL5LIB=$(top_builddir):$(PERL5LIB) && cd $(srcdir)/html && \
	gtkdoc-mkhtml --path="$(srcdir)" $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE)  $(MKHTML_OPTIONS)
	test "x$(HTML_IMAGES)" = "x" || ( cd $(srcdir) && cp $(HTML_IMAGES) html )
	@echo 'gtk-doc: Fixing cross-references'
	@PATH=$(top_builddir):$(PATH) PERL5LIB=$(top_builddir):$(PERL5LIB) && cd $(srcdir) && \
	gtkdoc-fixxref --module-dir=html --html-dir=$(HTML_DIR) $(FIXXREF_OPTIONS)
	touch html-build.stamp

##############

# we need to enforce a rebuild for the tests
clean-local:
	rm -f *~ *.bak
	rm -rf .libs
	cd $(srcdir) && \
	  rm -rf xml $(REPORT_FILES) \
	         $(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt

distclean-local:
	cd $(srcdir) && \
	  rm -rf xml $(REPORT_FILES) \
	         $(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt

maintainer-clean-local: clean
	cd $(srcdir) && rm -rf html

install-data-local:
	-installfiles=`echo $(srcdir)/html/*`; \
	if test "$$installfiles" = '$(srcdir)/html/*'; \
	then echo '-- Nothing to install' ; \
	else \
	  $(mkinstalldirs) $(DESTDIR)$(TARGET_DIR); \
	  for i in $$installfiles; do \
	    echo '-- Installing '$$i ; \
	    $(INSTALL_DATA) $$i $(DESTDIR)$(TARGET_DIR); \
	  done; \
	  echo '-- Installing $(srcdir)/html/index.sgml' ; \
	  $(INSTALL_DATA) $(srcdir)/html/index.sgml $(DESTDIR)$(TARGET_DIR) || :; \
	  which gtkdoc-rebase >/dev/null && \
	    gtkdoc-rebase --relative --dest-dir=$(DESTDIR) --html-dir=$(DESTDIR)$(TARGET_DIR) ; \
	fi

uninstall-local:
	rm -f $(DESTDIR)$(TARGET_DIR)/*

#
# Require gtk-doc when making dist
#
dist-check-gtkdoc:

dist-hook: dist-check-gtkdoc dist-hook-local
	mkdir $(distdir)/html
	cp $(srcdir)/html/* $(distdir)/html
	-cp $(srcdir)/$(DOC_MODULE).types $(distdir)/
	-cp $(srcdir)/$(DOC_MODULE)-sections.txt $(distdir)/
	cd $(distdir) && rm -f $(DISTCLEANFILES)
	-gtkdoc-rebase --online --relative --html-dir=$(distdir)/html

.PHONY : dist-hook-local docs
