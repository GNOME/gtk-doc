## Process this file with automake to produce Makefile.in

SUBDIRS = gobject bugs annotations .

if BUILD_TESTS

TESTS = gobject.sh bugs.sh annotations.sh
TESTS_ENVIRONMENT = PATH=$(srcdir):$(PATH)

endif

EXTRA_DIST = gtkdoctest.sh \
	gobject.sh bugs.sh

