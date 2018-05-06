## Process this file with automake to produce Makefile.in

if BUILD_TESTS

TESTS = \
  check.py common.py mk_to_db.py mkhtml2.py \
  tools.sh gobject.sh bugs.sh annotations.sh fail.sh empty.sh program.sh \
  sanity.sh
TESTS_ENVIRONMENT = \
	BUILDDIR=$(abs_builddir) \
	SRCDIR=$(abs_srcdir) \
	ABS_TOP_BUILDDIR=$(abs_top_builddir) \
	ABS_TOP_SRCDIR=$(abs_top_srcdir) \
	PATH=$(abs_top_builddir):$(srcdir):$(PATH) \
	PYTHONPATH=$(abs_top_builddir):$(abs_top_srcdir):$(PYTHONPATH) \
	GLIB_PREFIX="$(glib_prefix)"
TEST_EXTENSIONS = .py
PY_LOG_COMPILER = $(PYTHON)
endif

EXTRA_DIST = gtkdoctest.sh $(TESTS)

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
