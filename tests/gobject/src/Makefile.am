## Process this file with automake to produce Makefile.in

if BUILD_TESTS

noinst_LTLIBRARIES = libtester.la

libtester_la_SOURCES = \
	gobject.c gobject.h \
	giface.c giface.h \
	gtypes.c gtypes.h
#libtester_la_LIBADD = $(TEST_DEPS_LIBS)

AM_CPPFLAGS = $(TEST_DEPS_CFLAGS)

endif

EXTRA_DIST = meson.build

-include $(top_srcdir)/git.mk
