## Process this file with automake to produce Makefile.in

SUBDIRS = . src docs

if BUILD_TESTS

check-local: clean
	@rm -f docs/tester-docs.xml

endif


-include $(top_srcdir)/git.mk
