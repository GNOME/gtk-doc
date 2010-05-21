# -*- mode: makefile -*-

####################################
# Everything below here is generic #
####################################

if GTK_DOC_USE_LIBTOOL
GTKDOC_CC = $(LIBTOOL) --tag=CC --mode=compile $(CC) $(INCLUDES) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(LIBTOOL) --tag=CC --mode=link $(CC) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS)
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

# we don't install anything in tests
#TARGET_DIR=$(HTML_DIR)/$(DOC_MODULE)

EXTRA_DIST = 				\
	$(content_files)		\
	$(HTML_IMAGES)			\
	$(DOC_MAIN_SGML_FILE)		\
	$(DOC_MODULE)-sections.txt

DOC_STAMPS=scan-build.stamp sgml-build.stamp html-build.stamp pdf-build.stamp \
	$(srcdir)/sgml.stamp $(srcdir)/html.stamp  \
	$(srcdir)/pdf.stamp

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

check-local: html-build.stamp pdf-build.stamp
	@echo "gtk-doc: `date +%H:%M:%S.%N`: All done"

docs: html-build.stamp pdf-build.stamp
	@echo "gtk-doc: `date +%H:%M:%S.%N`: All done"

$(REPORT_FILES): sgml-build.stamp

#### scan ####

scan-build.stamp: $(HFILE_GLOB) $(CFILE_GLOB)
	@echo "gtk-doc: `date +%H:%M:%S.%N`: Scanning header files"
	@-chmod -R u+w $(srcdir)
	@cd $(srcdir) && PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	  gtkdoc-scan --module=$(DOC_MODULE) --source-dir=$(DOC_SOURCE_DIR) --ignore-headers="$(IGNORE_HFILES)" $(SCAN_OPTIONS) $(EXTRA_HFILES)
	@if grep -l '^..*$$' $(srcdir)/$(DOC_MODULE).types > /dev/null 2>&1 ; then \
		echo "gtk-doc: `date +%H:%M:%S.%N`: Introspecting gobjects"; \
	    CC="$(GTKDOC_CC)" LD="$(GTKDOC_LD)" RUN="$(GTKDOC_RUN)" CFLAGS="$(GTKDOC_CFLAGS) $(CFLAGS)" LDFLAGS="$(GTKDOC_LIBS) $(LDFLAGS)" PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) gtkdoc-scangobj --module=$(DOC_MODULE) --output-dir=$(srcdir) $(SCANGOBJ_OPTIONS); \
	else \
	    cd $(srcdir) ; \
	    for i in $(SCANOBJ_FILES) ; do \
               test -f $$i || touch $$i ; \
	    done \
	fi
	@touch scan-build.stamp

$(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt: scan-build.stamp
	@true

#### xml ####

sgml-build.stamp: $(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt $(expand_content_files)
	@echo "gtk-doc: `date +%H:%M:%S.%N`: Building XML"
	@-chmod -R u+w $(srcdir)
	@cd $(srcdir) && PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	gtkdoc-mkdb --module=$(DOC_MODULE) --source-dir=$(DOC_SOURCE_DIR) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $(MKDB_OPTIONS)
	@touch sgml-build.stamp

sgml.stamp: sgml-build.stamp
	@true

#### html ####

html-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@echo "gtk-doc: `date +%H:%M:%S.%N`: Building HTML"
	@-chmod -R u+w $(srcdir)
	@rm -rf $(srcdir)/html
	@mkdir $(srcdir)/html
	@cd $(srcdir)/html && PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	gtkdoc-mkhtml --uninstalled --path="$(abs_srcdir)" $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE)  $(MKHTML_OPTIONS)
	@test "x$(HTML_IMAGES)" = "x" || ( cd $(srcdir) && cp $(HTML_IMAGES) html/ )
	@echo "gtk-doc: `date +%H:%M:%S.%N`: Fixing cross-references"
	@cd $(srcdir) && PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	gtkdoc-fixxref --module=$(DOC_MODULE) --module-dir=html --html-dir=$(HTML_DIR) $(FIXXREF_OPTIONS)
	@touch html-build.stamp

#### pdf ####

pdf-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@echo "gtk-doc: `date +%H:%M:%S.%N`: Building PDF"
	@-chmod -R u+w $(srcdir)
	@rm -rf $(srcdir)/$(DOC_MODULE).pdf
	@mkpdf_imgdirs=""; \
	if test "x$(HTML_IMAGES)" != "x"; then \
	  for img in $(HTML_IMAGES); do \
	    part=`dirname $$img`; \
	    echo $$mkpdf_imgdirs | grep >/dev/null "\-\-imgdir=$$part "; \
	    if test $$? != 0; then \
	      mkpdf_imgdirs="$$mkpdf_imgdirs --imgdir=$$part"; \
	    fi; \
	  done; \
	fi; \
	cd $(srcdir) && PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	gtkdoc-mkpdf --uninstalled --path="$(abs_srcdir)" $$mkpdf_imgdirs $(DOC_MODULE) $(DOC_MAIN_SGML_FILE) $(MKPDF_OPTIONS)
	@touch pdf-build.stamp

##############

# we need to enforce a rebuild for the tests
clean-local:
	@rm -f *~ *.bak
	@rm -rf .libs
	@chmod -R u+w $(srcdir)
	$(MAKE) distclean-local

distclean-local:
	@cd $(srcdir) && \
	  rm -rf xml $(REPORT_FILES) $(DOC_MODULE).pdf \
	         $(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt

maintainer-clean-local: clean
	@cd $(srcdir) && rm -rf html

.PHONY : dist-hook-local docs
