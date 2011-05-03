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

SETUP_FILES = \
	$(content_files)		\
	$(DOC_MAIN_SGML_FILE)		\
	$(DOC_MODULE)-sections.txt	\
	$(DOC_MODULE)-overrides.txt

EXTRA_DIST = 				\
	$(HTML_IMAGES)			\
	$(SETUP_FILES)

DOC_STAMPS=setup-build.stamp scan-build.stamp tmpl-build.stamp sgml-build.stamp \
	html-build.stamp pdf-build.stamp \
	tmpl.stamp sgml.stamp html.stamp pdf.stamp

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
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: All done"

docs: html-build.stamp pdf-build.stamp
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: All done"

$(REPORT_FILES): sgml-build.stamp

#### setup ####

setup-build.stamp:
	@echo >ts `date +%s.%N`;
	-@if test "$(abs_srcdir)" != "$(abs_builddir)" ; then \
	    echo '  DOC   Preparing build'; \
	    files=`echo $(SETUP_FILES) $(expand_content_files) $(DOC_MODULE).types`; \
	    if test "x$$files" != "x" ; then \
	        for file in $$files ; do \
	            test -f $(abs_srcdir)/$$file && \
	                cp -pu $(abs_srcdir)/$$file $(abs_builddir)/ || true; \
	        done; \
	    fi; \
	    test -f $(abs_srcdir)/tmpl && \
	        cp -rp $(abs_srcdir)/tmpl $(abs_builddir)/; \
	fi
	@touch setup-build.stamp

#### scan ####

scan-build.stamp: $(HFILE_GLOB) $(CFILE_GLOB)
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: Scanning header files"
	@_source_dir='' ; \
	for i in $(DOC_SOURCE_DIR) ; do \
	    _source_dir="$${_source_dir} --source-dir=$$i" ; \
	done ; \
	echo "gtkdoc-scan --module=$(DOC_MODULE) --ignore-headers="$(IGNORE_HFILES)" $${_source_dir} $(SCAN_OPTIONS) $(EXTRA_HFILES)"  >gtkdoc-scan.log; \
	PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	gtkdoc-scan --module=$(DOC_MODULE) --ignore-headers="$(IGNORE_HFILES)" $${_source_dir} $(SCAN_OPTIONS) $(EXTRA_HFILES) 2>&1 | tee -a gtkdoc-scan.log
	@if grep -l '^..*$$' $(DOC_MODULE).types > /dev/null 2>&1 ; then \
		ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	    echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: Introspecting gobjects"; \
	    scanobj_options=""; \
	    if test "x$(V)" = "x1"; then \
	        scanobj_options="--verbose"; \
	    fi; \
	    echo "gtkdoc-scangobj $(SCANGOBJ_OPTIONS) --module=$(DOC_MODULE) $$scanobj_options" >gtkdoc-scangobj.log; \
	    PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	    CC="$(GTKDOC_CC)" LD="$(GTKDOC_LD)" RUN="$(GTKDOC_RUN)" CFLAGS="$(GTKDOC_CFLAGS) $(CFLAGS)" LDFLAGS="$(GTKDOC_LIBS) $(LDFLAGS)" \
	    gtkdoc-scangobj $(SCANGOBJ_OPTIONS) --module=$(DOC_MODULE) $$scanobj_options 2>&1 | tee -a gtkdoc-scangobj.log; \
	else \
	    for i in $(SCANOBJ_FILES) ; do \
	        test -f $$i || touch $$i ; \
	    done \
	fi
	@touch scan-build.stamp

$(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt: scan-build.stamp
	@true

#### templates ####

tmpl-build.stamp: setup-build.stamp $(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: Rebuilding template files"
	@echo "gtkdoc-mktmpl --module=$(DOC_MODULE) $(MKTMPL_OPTIONS)" >gtkdoc-mktmpl.log; \
	PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	gtkdoc-mktmpl --module=$(DOC_MODULE) $(MKTMPL_OPTIONS) 2>&1 | tee -a gtkdoc-mktmpl.log
	@if test "$(abs_srcdir)" != "$(abs_builddir)" ; then \
	  if test -w $(abs_srcdir) ; then \
	    cp -rp $(abs_builddir)/tmpl $(abs_srcdir)/; \
	  fi \
	fi
	@touch tmpl-build.stamp

tmpl.stamp: tmpl-build.stamp
	@true

$(srcdir)/tmpl/*.sgml:
	@true

#### xml ####

sgml-build.stamp: tmpl.stamp $(DOC_MODULE)-sections.txt $(srcdir)/tmpl/*.sgml $(expand_content_files)
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: Building XML"
	@_source_dir='' ; \
	for i in $(DOC_SOURCE_DIR) ; do \
	    _source_dir="$${_source_dir} --source-dir=$$i" ; \
	done ; \
	echo "gtkdoc-mkdb --module=$(DOC_MODULE) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $${_source_dir} $(MKDB_OPTIONS)" >gtkdoc-mkdb.log; \
	PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	gtkdoc-mkdb --module=$(DOC_MODULE) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $${_source_dir} $(MKDB_OPTIONS) 2>&1 | tee -a gtkdoc-mkdb.log
	@touch sgml-build.stamp

sgml.stamp: sgml-build.stamp
	@true

#### html ####

html-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @00$$tsd +%H:%M:%S.%N`: Building HTML"
	@rm -rf html
	@mkdir html
	@mkhtml_options=""; \
	if test "x$(V)" = "x1"; then \
	  mkhtml_options="$$mkhtml_options --verbose"; \
	fi; \
	echo "gtkdoc-mkhtml --uninstalled --path="$(abs_srcdir)" $$mkhtml_options $(MKHTML_OPTIONS) $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE)" >gtkdoc-mkhtml.log; \
	cd html && PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	gtkdoc-mkhtml --uninstalled --path="$(abs_srcdir)" $$mkhtml_options $(MKHTML_OPTIONS) $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE) 2>&1 | tee -a ../gtkdoc-mkhtml.log
	-@test "x$(HTML_IMAGES)" = "x" || \
	for file in $(HTML_IMAGES) ; do \
	  if test -f $(abs_srcdir)/$$file ; then \
	    cp $(abs_srcdir)/$$file $(abs_builddir)/html; \
	  fi; \
	  if test -f $(abs_builddir)/$$file ; then \
	    cp $(abs_builddir)/$$file $(abs_builddir)/html; \
	  fi; \
	done;
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: Fixing cross-references"
	@echo "gtkdoc-fixxref --module=$(DOC_MODULE) --module-dir=html --html-dir=$(HTML_DIR) $(FIXXREF_OPTIONS)" >gtkdoc-fixxref.log; \
	PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) \
	gtkdoc-fixxref --module=$(DOC_MODULE) --module-dir=html --html-dir=$(HTML_DIR) $(FIXXREF_OPTIONS) 2>&1 | tee -a gtkdoc-fixxref.log
	@touch html-build.stamp

#### pdf ####

pdf-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@ts1=`cat ts`;ts2=`date +%s.%N`;tsd=`echo $$ts2-$$ts1 | bc`; \
	echo "  DOC   `date --utc --date @0$$tsd +%H:%M:%S.%N`: Building PDF"
	@rm -f $(DOC_MODULE).pdf
	@mkpdf_options=""; \
	if test "x$(V)" = "x1"; then \
	  mkpdf_options="$$mkpdf_options --verbose"; \
	fi; \
	if test "x$(HTML_IMAGES)" != "x"; then \
	  for img in $(HTML_IMAGES); do \
	    part=`dirname $$img`; \
	    echo $$mkpdf_options | grep >/dev/null "\-\-imgdir=$$part "; \
	    if test $$? != 0; then \
	      mkpdf_options="$$mkpdf_options --imgdir=$$part"; \
	    fi; \
	  done; \
	fi; \
	echo "gtkdoc-mkpdf --uninstalled --path="$(abs_srcdir)" $$mkpdf_options $(DOC_MODULE) $(DOC_MAIN_SGML_FILE) $(MKPDF_OPTIONS)" >gtkdoc-mkpdf.log; \
	PATH=$(abs_top_builddir):$(PATH) PERL5LIB=$(abs_top_builddir):$(PERL5LIB) ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	gtkdoc-mkpdf --uninstalled --path="$(abs_srcdir)" $$mkpdf_options $(DOC_MODULE) $(DOC_MAIN_SGML_FILE) $(MKPDF_OPTIONS) 2>&1 | tee -a gtkdoc-mkpdf.log
	@touch pdf-build.stamp

##############

# we need to enforce a rebuild for the tests
clean-local:
	@rm -f *~ *.bak ts
	@rm -rf .libs
	$(MAKE) distclean-local

distclean-local:
	@rm -rf xml html $(REPORT_FILES) $(DOC_MODULE).pdf \
	    $(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt
	@if test "$(abs_srcdir)" != "$(abs_builddir)" ; then \
	    rm -f $(SETUP_FILES) $(expand_content_files) $(DOC_MODULE).types; \
	    rm -rf tmpl; \
	fi

maintainer-clean-local: clean
	@rm -rf xml html

.PHONY : dist-hook-local docs
