## Process this file with automake to produce Makefile.in

SUBDIRS =
TESTS = \
  tools.sh check.py common.py highlight.py mkdb.py mk_to_db.py mkhtml2.py \
  scan.py

if BUILD_TESTS
# we need to run '.' last so that sanity processes the generated docs
# maybe move it to a subdir?
SUBDIRS += annotations bugs empty fail gobject program repro .
TESTS += annotations.sh bugs.sh empty.sh fail.sh gobject.sh program.sh
endif

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

EXTRA_DIST = gtkdoctest.sh sanity.sh $(TESTS)

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

coverage:
	@python3-coverage erase; \
	for f in *.py; do \
	  $(TESTS_ENVIRONMENT) python3-coverage run -a $$f; \
	done; \
	python3-coverage html --include="*/gtkdoc/*.py"; \
	python3-coverage report --include="*/gtkdoc/*.py"

EXTRA_DIST += \
	gtkdocentities.ent.in \
	helpers/gtkdoc_check_runner.py \
	helpers/gtkdoc_fixxref_runner.py \
	helpers/gtkdoc_mkdb_runner.py \
	helpers/gtkdoc_mkhtml_runner.py \
	helpers/gtkdoc_scan_runner.py \
	helpers/gtkdoc_scangobj_runner.py \
	helpers/meson.build \
	meson.build

.PHONY: snapshot

-include $(top_srcdir)/git.mk
