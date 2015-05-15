## Process this file with automake to produce Makefile.in

SUBDIRS = gobject bugs annotations fail empty .

if BUILD_TESTS

TESTS = tools.sh gobject.sh bugs.sh annotations.sh fail.sh empty.sh sanity.sh
TESTS_ENVIRONMENT = \
	BUILDDIR=$(abs_builddir) \
	SRCDIR=$(abs_srcdir) \
	ABS_TOP_BUILDDIR=$(abs_top_builddir) \
	ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	PATH=$(abs_top_builddir):$(srcdir):$(PATH) \
	PERL5LIB=$(abs_top_builddir):$(PERL5LIB)

endif

EXTRA_DIST = gtkdoctest.sh tools.sh sanity.sh \
	gobject.sh bugs.sh annotations.sh fail.sh empty.sh 

# run any given test by running make <test>.check
%.check: %
	@$(TESTS_ENVIRONMENT)	\
	./$*

snapshot:
	@for dir in $(SUBDIRS); do \
	  if test -d $$dir/docs/html; then \
      rm -rf $$dir/docs/html.ref; \
      cp -r $$dir/docs/html $$dir/docs/html.ref; \
    fi; \
	done

.PHONY: snapshot

-include $(top_srcdir)/git.mk
