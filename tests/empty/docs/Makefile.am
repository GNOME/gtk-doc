## Process this file with automake to produce Makefile.in

# this tests bootstraps gtk-doc, that includes generating a default
# DOC_MAIN_SGML_FILE
# right now that fails with parallel make, as make cannot see that what is a
# dependency for another target is generated as needed
MAKEFLAGS = -j1

# We require automake 1.6 at least.
AUTOMAKE_OPTIONS = 1.6

# The name of the module, e.g. 'glib'.
DOC_MODULE=tester

# The top-level SGML file. You can change this if you want to.
DOC_MAIN_SGML_FILE=$(DOC_MODULE)-docs.xml

# The directory containing the source code. Relative to $(srcdir).
# gtk-doc will search all .c & .h files beneath here for inline comments
# documenting the functions and macros.
DOC_SOURCE_DIR=$(top_srcdir)/tests/empty/src

# Extra options to pass to gtkdoc-scangobj. Not normally needed.
SCANGOBJ_OPTIONS=

# Extra options to supply to gtkdoc-scan.
SCAN_OPTIONS=--deprecated-guards="GTKDOC_TESTER_DISABLE_DEPRECATED" \
  --rebuild-sections

# Extra options to supply to gtkdoc-mkdb.
MKDB_OPTIONS=--xml-mode

# Extra options to supply to gtkdoc-mkhtml
MKHTML_OPTIONS=

# Extra options to supply to gtkdoc-fixref. Not normally needed.
# --html-dir=$(HTML_DIR)
FIXXREF_OPTIONS=--extra-dir=$(glib_prefix)/share/gtk-doc/html

# Used for dependencies. The docs will be rebuilt if any of these change.
HFILE_GLOB=$(top_srcdir)/tests/empty/src/*.h
CFILE_GLOB=$(top_srcdir)/tests/empty/src/*.c

# Header files to ignore when scanning.
IGNORE_HFILES=config.h

# Images to copy into HTML directory.
HTML_IMAGES =

# Extra SGML files that are included by $(DOC_MAIN_SGML_FILE).
# e.g. content_files=running.sgml building.sgml changes-2.0.sgml
content_files =

# SGML files where gtk-doc abbreviations (#GtkWidget) are expanded
# These files must be listed here *and* in content_files
# e.g. expand_content_files=running.sgml
expand_content_files=

# CFLAGS and LDFLAGS for compiling gtkdoc-scangobj with your library.
# Only needed if you are using gtkdoc-scangobj to dynamically query widget
# signals and properties.
GTKDOC_CFLAGS = -I$(top_srcdir)/tests/empty/src $(TEST_DEPS_CFLAGS)
GTKDOC_LIBS = $(TEST_DEPS_LIBS) $(top_builddir)/tests/empty/src/libtester.la

# include generic part
include $(top_srcdir)/tests/gtk-doc.make

# Other files to distribute
# e.g. EXTRA_DIST += version.xml.in
EXTRA_DIST +=

CLEANFILES += \
  $(DOC_MODULE)-overrides.txt \
  $(DOC_MODULE).types

if BUILD_TESTS
TESTS_ENVIRONMENT = \
	DOC_MODULE=$(DOC_MODULE) DOC_MAIN_SGML_FILE=$(DOC_MAIN_SGML_FILE) \
	PATH=$(abs_top_builddir):$(srcdir):$(PATH)
endif

CLEANFILES += \
	tester-docs.xml \
	tester-sections.txt

EXTRA_DIST += meson.build
EXTRA_DIST += xml/meson.build

-include $(top_srcdir)/git.mk
