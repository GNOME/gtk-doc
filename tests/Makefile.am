## Process this file with automake to produce Makefile.in

SUBDIRS = gobject bugs annotations .

if BUILD_TESTS

TESTS = gobject.sh bugs.sh annotations.sh
TESTS_ENVIRONMENT = \
	PATH=$(abs_top_builddir):$(srcdir):$(PATH) \
	PERL5LIB=$(abs_top_builddir):$(PERL5LIB)

endif

EXTRA_DIST = gtkdoctest.sh \
	gobject.sh bugs.sh annotations.sh

