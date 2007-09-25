## Process this file with automake to produce Makefile.in

SUBDIRS = gobject bugs .

if BUILD_TESTS

TESTS = gobject.sh bugs.sh
TESTS_ENVIRONMENT = PATH=$(srcdir):$(PATH)

endif

EXTRA_DIST = gtkdoctest.sh \
	gobject.sh bugs.sh

