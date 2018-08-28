## Process this file with automake to produce Makefile.in

if BUILD_TESTS

noinst_LTLIBRARIES = libtester.la

libtester_la_SOURCES = tester.c tester.h
#libtester_la_LIBADD = $(TEST_DEPS_LIBS)

AM_CPPFLAGS = $(TEST_DEPS_CFLAGS)

endif


-include $(top_srcdir)/git.mk
