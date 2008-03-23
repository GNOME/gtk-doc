## Process this file with automake to produce Makefile.in

# We require automake 1.6 at least.
AUTOMAKE_OPTIONS = 1.6

# The name of the module, e.g. 'glib'.
DOC_MODULE=tester

# The top-level SGML file. You can change this if you want to.
DOC_MAIN_SGML_FILE=$(DOC_MODULE)-docs.xml

# The directory containing the source code. Relative to $(srcdir).
# gtk-doc will search all .c & .h files beneath here for inline comments
# documenting the functions and macros.
DOC_SOURCE_DIR=$(top_srcdir)/tests/gobject/src

# Extra options to pass to gtkdoc-scangobj. Not normally needed.
SCANGOBJ_OPTIONS=2>&1 | tee gtkdoc-scangobj.log

# Extra options to supply to gtkdoc-scan.
SCAN_OPTIONS=--deprecated-guards="GTKDOC_TESTER_DISABLE_DEPRECATED" 2>&1 | tee gtkdoc-scan.log

# Extra options to supply to gtkdoc-mkdb.
MKDB_OPTIONS=--sgml-mode --output-format=xml 2>&1 | tee gtkdoc-mkdb.log

# Extra options to supply to gtkdoc-mktmpl
# e.g. MKTMPL_OPTIONS=--only-section-tmpl
MKTMPL_OPTIONS=2>&1 | tee gtkdoc-mktmpl.log

# Extra options to supply to gtkdoc-mkhtml
MKHTML_OPTIONS=2>&1 | tee ../gtkdoc-mkhtml.log

# Extra options to supply to gtkdoc-fixref. Not normally needed.
# --html-dir=$(HTML_DIR)
FIXXREF_OPTIONS=--extra-dir=$(glib_prefix)/share/gtk-doc/html 2>&1 | tee gtkdoc-fixxref.log

# Used for dependencies. The docs will be rebuilt if any of these change.
HFILE_GLOB=$(top_srcdir)/tests/gobject/src/*.h
CFILE_GLOB=$(top_srcdir)/tests/gobject/src/*.c

# Header files to ignore when scanning.
IGNORE_HFILES=config.h

# Images to copy into HTML directory.
HTML_IMAGES =

# Extra SGML files that are included by $(DOC_MAIN_SGML_FILE).
# e.g. content_files=running.sgml building.sgml changes-2.0.sgml
content_files =

# SGML files where gtk-doc abbrevations (#GtkWidget) are expanded
# These files must be listed here *and* in content_files
# e.g. expand_content_files=running.sgml
expand_content_files=

# CFLAGS and LDFLAGS for compiling gtkdoc-scangobj with your library.
# Only needed if you are using gtkdoc-scangobj to dynamically query widget
# signals and properties.
INCLUDES = -I$(top_builddir) -I$(top_builddir)/tests/gobject/src $(TEST_DEPS_CFLAGS)
GTKDOC_LIBS = $(TEST_DEPS_LIBS) $(top_builddir)/tests/gobject/src/libtester.la

# include generic part
include $(top_srcdir)/tests/gtk-doc.make

# Other files to distribute
# e.g. EXTRA_DIST += version.xml.in
EXTRA_DIST +=

DISTCLEANFILES = \
	gtkdoc-scan.log \
	gtkdoc-scangobj.log \
	gtkdoc-mktmpl.log \
	gtkdoc-mkdb.log \
	gtkdoc-mkhtml.log \
	gtkdoc-fixxref.log
