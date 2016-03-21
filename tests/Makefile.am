## Process this file with automake to produce Makefile.in

SUBDIRS = gobject bugs annotations fail empty .

if BUILD_TESTS

TESTS = \
  gtkdoc-common.t gtkdoc-fixxref.t gtkdoc-mkdb.t gtkdoc-rebase.t gtkdoc-scan.t \
  tools.sh gobject.sh bugs.sh annotations.sh fail.sh empty.sh sanity.sh
TESTS_ENVIRONMENT = \
	BUILDDIR=$(abs_builddir) \
	SRCDIR=$(abs_srcdir) \
	ABS_TOP_BUILDDIR=$(abs_top_builddir) \
	ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	PATH=$(abs_top_builddir):$(srcdir):$(PATH) \
	PERL5LIB=$(abs_top_builddir):$(PERL5LIB)

endif

EXTRA_DIST = gtkdoctest.sh tools.sh sanity.sh \
	gobject.sh bugs.sh annotations.sh fail.sh empty.sh \
	gtkdoc-common.t gtkdoc-fixxref.t gtkdoc-mkdb.t gtkdoc-rebase.t gtkdoc-scan.t


# run any given test by running make <test>.check
%.check: %
	@$(TESTS_ENVIRONMENT)	\
	./$*

snapshot:
	@for dir in $(SUBDIRS); do \
    rm -rf $$dir/docs/html.ref; \
	  if test -d $$dir/docs/html; then \
      cp -r $$dir/docs/html $$dir/docs/html.ref; \
    fi; \
    rm -rf $$dir/docs/xml.ref; \
	  if test -d $$dir/docs/xml; then \
      cp -r $$dir/docs/xml $$dir/docs/xml.ref; \
    fi; \
	done

.PHONY: snapshot

-include $(top_srcdir)/git.mk
