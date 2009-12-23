## Process this file with automake to produce Makefile.in

SUBDIRS = gobject bugs annotations fail .

if BUILD_TESTS

TESTS = tools.sh gobject.sh bugs.sh annotations.sh fail.sh
TESTS_ENVIRONMENT = \
	ABS_TOP_BUILDDIR=$(abs_top_builddir) \
	PATH=$(abs_top_builddir):$(srcdir):$(PATH) \
	PERL5LIB=$(abs_top_builddir):$(PERL5LIB)

endif

EXTRA_DIST = gtkdoctest.sh tools.sh \
	gobject.sh bugs.sh annotations.sh fail.sh

# run any given test by running make <test>.check
%.check: %
	@$(TESTS_ENVIRONMENT)	\
	./$*


-include $(top_srcdir)/git.mk
