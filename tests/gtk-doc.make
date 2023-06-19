# -*- mode: makefile -*-

####################################
# Everything below here is generic #
####################################

if GTK_DOC_USE_LIBTOOL
GTKDOC_CC = $(LIBTOOL) --tag=CC --mode=compile $(CC) $(INCLUDES) $(GTKDOC_DEPS_CFLAGS) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(LIBTOOL) --tag=CC --mode=link $(CC) $(GTKDOC_DEPS_LIBS) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS)
GTKDOC_RUN = $(LIBTOOL) --mode=execute
else
GTKDOC_CC = $(CC) $(INCLUDES) $(GTKDOC_DEPS_CFLAGS) $(AM_CPPFLAGS) $(CPPFLAGS) $(AM_CFLAGS) $(CFLAGS)
GTKDOC_LD = $(CC) $(GTKDOC_DEPS_LIBS) $(AM_CFLAGS) $(CFLAGS) $(AM_LDFLAGS) $(LDFLAGS)
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

DOC_STAMPS=setup-build.stamp scan-build.stamp sgml-build.stamp \
	html-build.stamp pdf-build.stamp \
	sgml.stamp html.stamp pdf.stamp

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

CLEANFILES = $(SCANOBJ_FILES) $(REPORT_FILES) $(DOC_STAMPS) \
  $(DOC_MODULE).pdf \
  ts \
	gtkdoc-scan.log \
	gtkdoc-scangobj.log \
	gtkdoc-mkdb.log \
	gtkdoc-mkhtml.log \
	gtkdoc-mkpdf.log \
	gtkdoc-fixxref.log

GITIGNOREFILES = \
  html.ref xml.ref

check-local: html-build.stamp pdf-build.stamp
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: All done"

docs: html-build.stamp pdf-build.stamp
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: All done"

$(REPORT_FILES): sgml-build.stamp

ts:
	@echo >ts `date $(TS_FMT)`;

#### setup ####

setup-build.stamp: ts
	-@if test "$(abs_srcdir)" != "$(abs_builddir)" ; then \
	  echo '  DOC   Preparing build'; \
	  files=`echo $(SETUP_FILES) $(expand_content_files) $(DOC_MODULE).types`; \
	  if test "x$$files" != "x" ; then \
	    for file in $$files ; do \
	      destdir=`dirname $(abs_builddir)/$$file`; \
	      test -d "$$destdir" || mkdir -p "$$destdir"; \
	      test -f $(abs_srcdir)/$$file && \
	        cp -pf $(abs_srcdir)/$$file $(abs_builddir)/$$file || true; \
	    done; \
	  fi; \
	fi
	@touch setup-build.stamp

#### scan ####

scan-build.stamp: ts setup-build.stamp $(HFILE_GLOB) $(CFILE_GLOB)
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: Scanning header files"
	@_source_dir='' ; \
	for i in $(DOC_SOURCE_DIR) ; do \
	  _source_dir="$${_source_dir} --source-dir=$$i" ; \
	done ; \
	echo "gtkdoc-scan --module=$(DOC_MODULE) --ignore-headers="$(IGNORE_HFILES)" $${_source_dir} $(SCAN_OPTIONS) $(EXTRA_HFILES)"  >gtkdoc-scan.log; \
	PATH=$(abs_top_builddir):$(PATH) PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) \
	gtkdoc-scan --module=$(DOC_MODULE) --ignore-headers="$(IGNORE_HFILES)" $${_source_dir} $(SCAN_OPTIONS) $(EXTRA_HFILES) 2>&1 | tee -a gtkdoc-scan.log
	@if grep -l '^..*$$' $(DOC_MODULE).types > /dev/null 2>&1 ; then \
		ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	  echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: Introspecting gobjects"; \
	  scanobj_options=""; \
	  if test "x$(V)" = "x1"; then \
	    scanobj_options="--verbose"; \
	  fi; \
	  echo "gtkdoc-scangobj $(SCANGOBJ_OPTIONS) --module=$(DOC_MODULE) $$scanobj_options" >gtkdoc-scangobj.log; \
	  PATH=$(abs_top_builddir):$(PATH) PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) \
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

#### xml ####

sgml-build.stamp: setup-build.stamp $(DOC_MODULE)-decl.txt $(SCANOBJ_FILES) $(HFILE_GLOB) $(CFILE_GLOB) $(DOC_MODULE)-sections.txt $(DOC_MODULE)-overrides.txt $(expand_content_files) xml/gtkdocentities.ent
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: Building XML"
	@_source_dir='' ; \
	for i in $(DOC_SOURCE_DIR) ; do \
	  _source_dir="$${_source_dir} --source-dir=$$i" ; \
	done ; \
	echo "gtkdoc-mkdb --module=$(DOC_MODULE) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $${_source_dir} $(MKDB_OPTIONS)" >gtkdoc-mkdb.log; \
	PATH=$(abs_top_builddir):$(PATH) PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) \
	gtkdoc-mkdb --module=$(DOC_MODULE) --output-format=xml --expand-content-files="$(expand_content_files)" --main-sgml-file=$(DOC_MAIN_SGML_FILE) $${_source_dir} $(MKDB_OPTIONS) 2>&1 | tee -a gtkdoc-mkdb.log
	@touch sgml-build.stamp

sgml.stamp: sgml-build.stamp
	@true

$(DOC_MAIN_SGML_FILE): sgml-build.stamp
	@true

xml/gtkdocentities.ent: Makefile
	@$(MKDIR_P) $(@D) && ( \
		echo "<!ENTITY package \"$(PACKAGE)\">"; \
		echo "<!ENTITY package_bugreport \"$(PACKAGE_BUGREPORT)\">"; \
		echo "<!ENTITY package_name \"$(PACKAGE_NAME)\">"; \
		echo "<!ENTITY package_string \"$(PACKAGE_STRING)\">"; \
		echo "<!ENTITY package_tarname \"$(PACKAGE_TARNAME)\">"; \
		echo "<!ENTITY package_url \"$(PACKAGE_URL)\">"; \
		echo "<!ENTITY package_version \"$(PACKAGE_VERSION)\">"; \
	) > $@

#### html ####

html-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: Building HTML"
	@rm -rf html
	@mkdir html
	@mkhtml_options=""; \
	if test "x$(V)" = "x1"; then \
	  mkhtml_options="$$mkhtml_options --verbose"; \
	fi; \
	echo "gtkdoc-mkhtml --uninstalled --path="$(abs_srcdir)" $$mkhtml_options $(MKHTML_OPTIONS) $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE)" >gtkdoc-mkhtml.log; \
	cd html && PATH=$(abs_top_builddir):$(PATH) PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	gtkdoc-mkhtml --uninstalled --path="$(abs_srcdir)" $$mkhtml_options $(MKHTML_OPTIONS) $(DOC_MODULE) ../$(DOC_MAIN_SGML_FILE) 2>&1 | tee -a ../gtkdoc-mkhtml.log
	-@test "x$(HTML_IMAGES)" = "x" || \
	for file in $(HTML_IMAGES) ; do \
	  test -f $(abs_srcdir)/$$file && cp $(abs_srcdir)/$$file $(abs_builddir)/html; \
	  test -f $(abs_builddir)/$$file && cp $(abs_builddir)/$$file $(abs_builddir)/html; \
	done;
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: Fixing cross-references"
	@echo "gtkdoc-fixxref --module=$(DOC_MODULE) --module-dir=html --html-dir=$(HTML_DIR) $(FIXXREF_OPTIONS)" >gtkdoc-fixxref.log; \
	PATH=$(abs_top_builddir):$(PATH) PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) \
	gtkdoc-fixxref --module=$(DOC_MODULE) --module-dir=html --html-dir=$(HTML_DIR) $(FIXXREF_OPTIONS) 2>&1 | tee -a gtkdoc-fixxref.log
	@touch html-build.stamp

#### pdf ####

pdf-build.stamp: sgml.stamp $(DOC_MAIN_SGML_FILE) $(content_files)
	@ts=`cat ts`;tsd=`date -d "now - $$ts seconds" $(TS_FMT)`; \
	echo "  DOC   `$(DATE_FMT_CMD)$$tsd`: Building PDF"
	@rm -f $(DOC_MODULE).pdf
	@mkpdf_options=""; \
	if test "x$(V)" = "x1"; then \
	  mkpdf_options="$$mkpdf_options --verbose"; \
	fi; \
	if test "x$(HTML_IMAGES)" != "x"; then \
	  for img in $(HTML_IMAGES); do \
	    part=`dirname $$img`; \
	    echo $$mkpdf_options | grep >/dev/null "\--imgdir=$$part "; \
	    if test $$? != 0; then \
	      mkpdf_options="$$mkpdf_options --imgdir=$$part"; \
	    fi; \
	  done; \
	fi; \
	echo "gtkdoc-mkpdf --uninstalled --path="$(abs_srcdir)" $$mkpdf_options $(DOC_MODULE) $(DOC_MAIN_SGML_FILE) $(MKPDF_OPTIONS)" >gtkdoc-mkpdf.log; \
	PATH=$(abs_top_builddir):$(PATH) PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	gtkdoc-mkpdf --uninstalled --path="$(abs_srcdir)" $$mkpdf_options $(DOC_MODULE) $(DOC_MAIN_SGML_FILE) $(MKPDF_OPTIONS) 2>&1 | tee -a gtkdoc-mkpdf.log
	@touch pdf-build.stamp

##############

# we need to enforce a rebuild for the tests
clean-local:
	@rm -f *~ *.bak ts gtkdoc-*.log
	@rm -rf .libs
	@if echo $(SCAN_OPTIONS) | grep -q "\--rebuild-types" ; then \
	  rm -f $(DOC_MODULE).types; \
	fi
	$(MAKE) distclean-local

distclean-local:
	@rm -rf xml html $(REPORT_FILES) $(DOC_MODULE).pdf \
	    $(DOC_MODULE)-decl-list.txt $(DOC_MODULE)-decl.txt
	@if test "$(abs_srcdir)" != "$(abs_builddir)" ; then \
	    rm -f $(SETUP_FILES) $(expand_content_files) $(DOC_MODULE).types; \
	fi

maintainer-clean-local:
	@rm -rf xml html

.PHONY : dist-hook-local docs
