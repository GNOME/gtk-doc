dnl Process this file with autoconf to produce a configure script.
AC_PREREQ([2.63])

m4_define(gtk_doc_version, 1.35.1)

AC_INIT([gtk-doc],[gtk_doc_version],[https://gitlab.gnome.org/GNOME/gtk-doc/issues],[gtk-doc])

AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([gtk-doc.pc.in])
AC_CONFIG_AUX_DIR([build-aux])

AM_INIT_AUTOMAKE([1.11 check-news std-options -Wno-portability tar-ustar no-dist-gzip dist-xz])
AM_MAINTAINER_MODE([enable])

# Support silent build rules, requires at least automake-1.11. Disable
# by either passing --disable-silent-rules to configure or passing V=1
# to make
AM_SILENT_RULES([yes])

# Check for programs
AC_PROG_CC

# Initialize libtool
LT_PREREQ([2.2])
LT_INIT

dnl Make sure we have pkg-config >= 0.19, so installing in $(datadir) is OK.
PKG_PROG_PKG_CONFIG([0.19])

dnl
dnl Check for Python.
dnl
AM_PATH_PYTHON([3.2])

dnl
dnl Check for xsltproc
dnl
AC_PATH_PROG([XSLTPROC], [xsltproc])
if test -z "$XSLTPROC"; then
	AC_MSG_ERROR([xsltproc not found])
fi

dnl
dnl Check for dblatex/fop (for pdf output)
dnl
AC_PATH_PROG([DBLATEX], [dblatex])
if test -z "$DBLATEX"; then
	AC_PATH_PROG([FOP], [fop])
	if test -z "$FOP"; then
		AC_MSG_WARN([neither dblatex nor fop found, so no pdf output from xml])
	fi
fi

dnl check for DocBook DTD and stylesheets in the local catalog.
JH_CHECK_XML_CATALOG([-//OASIS//DTD DocBook XML V4.3//EN], [DocBook XML DTD V4.3])
JH_CHECK_XML_CATALOG([http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl], [DocBook XSL Stylesheets])

dnl
dnl Set runtime package dirs so we can find the script containing common routines.
dnl
dnl From Autoconf Macro Archive:
m4_define([AC_DEFINE_DIR], [
	prefix_NONE=
	exec_prefix_NONE=
	test "x$prefix" = xNONE && prefix_NONE=yes && prefix=$ac_default_prefix
	test "x$exec_prefix" = xNONE && exec_prefix_NONE=yes && exec_prefix=$prefix
	eval ac_define_dir="\"[$]$2\""
	eval ac_define_dir="\"$ac_define_dir\""
	AC_SUBST($1, "$ac_define_dir")
	test "$prefix_NONE" && prefix=NONE
	test "$exec_prefix_NONE" && exec_prefix=NONE
])
PACKAGE_DATA_DIR="${datadir}/${PACKAGE}/data"
AC_DEFINE_DIR([PACKAGE_DATA_DIR], [PACKAGE_DATA_DIR])
PYTHON_PACKAGE_DIR="${datadir}/${PACKAGE}/python"
AC_DEFINE_DIR([PYTHON_PACKAGE_DIR], [PYTHON_PACKAGE_DIR])

dnl Only use -Wall if we have gcc
if test "x$GCC" = "xyes"; then
	if test -z "`echo "$CFLAGS" | grep "\-Wall" 2> /dev/null`" ; then
		CFLAGS="$CFLAGS -Wall"
	fi
fi

dnl if glib is available we can enable the tests
PKG_CHECK_MODULES(TEST_DEPS, [glib-2.0 >= 2.6.0 gobject-2.0 >= 2.6.0],
	[	glib_prefix="`$PKG_CONFIG --variable=prefix glib-2.0`"
		gtk_doc_use_libtool="yes"
		build_tests="yes"
	],
	[	gtk_doc_use_libtool="no"
		build_tests="no"
	]
)
AM_CONDITIONAL(GTK_DOC_USE_LIBTOOL, test -n "$LIBTOOL" -a x$gtk_doc_use_libtool = xyes )
dnl this enables the rule in test/Makefile.am
AM_CONDITIONAL(BUILD_TESTS, test x$build_tests = xyes)
AC_SUBST(glib_prefix)

dnl enable runtime debugging code
AC_MSG_CHECKING(whether to enable runtime debugging code)
AC_ARG_ENABLE([debug],
	AS_HELP_STRING([--enable-debug],
	[enable runtime debugging code (default=no)]),,
	[enable_debug="no"])
AC_MSG_RESULT($enable_debug)

dnl check what date format we can use for the makefile tracing in tests
dnl this is mostly to detect the date command on macosx that is quite cripled
dnl  and broken too
AC_MSG_CHECKING(whether date can output nanoseconds)
date +%s.%N | grep -q 'N'
if test "$?" = "1"; then
  TS_FMT="+%s.%N"
  ELAPSED_FMT="+%H:%M:%S.%N"
  AC_MSG_RESULT(yes)
else
  TS_FMT="+%s.0"
  ELAPSED_FMT="+%H:%M:%S"
  AC_MSG_RESULT(no)
fi
AC_SUBST(TS_FMT)
AC_SUBST(ELAPSED_FMT)

AC_MSG_CHECKING(whether date can format dates)
date >/dev/null 2>&1 --utc --date @1.1 $ELAPSED_FMT
if test "$?" = "0"; then
  DATE_FMT_CMD="date --utc $ELAPSED_FMT --date @0"
  AC_MSG_RESULT(yes)
else
  DATE_FMT_CMD="echo "
  AC_MSG_RESULT(no)
fi
AC_SUBST(DATE_FMT_CMD)

dnl
dnl Documentation
dnl
AC_MSG_CHECKING([for yelp-tools])
have_yelp_tools=no
m4_ifdef([YELP_HELP_INIT],[
AC_MSG_RESULT([yes])
YELP_HELP_INIT
have_yelp_tools=yes
])
if test "x$have_yelp_tools" != "xyes"; then
  AC_MSG_RESULT([no])
fi
AM_CONDITIONAL([HAVE_YELP_TOOLS],[test x$have_yelp_tools = xyes])

dnl
dnl Python modules
dnl
AX_PYTHON_MODULE("pygments")

AC_CONFIG_FILES([Makefile
gtk-doc.pc
buildsystems/autotools/Makefile
buildsystems/cmake/Makefile
buildsystems/cmake/GtkDocConfigVersion.cmake
gtkdoc/config_data.py
help/Makefile
help/manual/Makefile
tests/Makefile
tests/annotations/Makefile
tests/annotations/src/Makefile
tests/annotations/docs/Makefile
tests/bugs/Makefile
tests/bugs/src/Makefile
tests/bugs/docs/Makefile
tests/empty/Makefile
tests/empty/src/Makefile
tests/empty/docs/Makefile
tests/fail/Makefile
tests/fail/src/Makefile
tests/fail/docs/Makefile
tests/gobject/Makefile
tests/gobject/src/Makefile
tests/gobject/docs/Makefile
tests/program/Makefile
tests/program/src/Makefile
tests/program/docs/Makefile
tests/repro/Makefile
tests/repro/src/Makefile
tests/repro/docs/Makefile
])

dnl run chmod on these after parsing them.
AC_CONFIG_FILES([gtkdoc-check],    [chmod +x gtkdoc-check])
AC_CONFIG_FILES([gtkdoc-depscan],  [chmod +x gtkdoc-depscan])
AC_CONFIG_FILES([gtkdoc-fixxref],  [chmod +x gtkdoc-fixxref])
AC_CONFIG_FILES([gtkdoc-mkdb],     [chmod +x gtkdoc-mkdb])
AC_CONFIG_FILES([gtkdoc-mkhtml],   [chmod +x gtkdoc-mkhtml])
AC_CONFIG_FILES([gtkdoc-mkhtml2],  [chmod +x gtkdoc-mkhtml2])
AC_CONFIG_FILES([gtkdoc-mkman],    [chmod +x gtkdoc-mkman])
AC_CONFIG_FILES([gtkdoc-mkpdf],    [chmod +x gtkdoc-mkpdf])
AC_CONFIG_FILES([gtkdoc-rebase],   [chmod +x gtkdoc-rebase])
AC_CONFIG_FILES([gtkdoc-scan],     [chmod +x gtkdoc-scan])
AC_CONFIG_FILES([gtkdoc-scangobj], [chmod +x gtkdoc-scangobj])
AC_CONFIG_FILES([buildsystems/autotools/gtkdocize],       [chmod +x buildsystems/autotools/gtkdocize])
AC_CONFIG_FILES([tests/tools.sh],  [chmod +x tests/tools.sh])
AC_OUTPUT

AC_MSG_NOTICE([
gtk-doc was configured with the following options:
==================================================])

test -n "$DBLATEX$FOP" \
    && AC_MSG_NOTICE([** PDF support enabled, using $DBLATEX$FOP]) \
    || AC_MSG_NOTICE([   PDF support disabled, no dblatex or fop available])
test "x$build_tests" != "xno" \
    && AC_MSG_NOTICE([** Building regression tests]) \
    || AC_MSG_NOTICE([   Skipping regression tests])
test "x$enable_debug" != "xno" \
    && AC_MSG_NOTICE([** Debug tracing enabled]) \
    || AC_MSG_NOTICE([   Debug tracing disabled])
test "x$have_yelp_tools" != "xno" \
    && AC_MSG_NOTICE([** Documentation enabled]) \
    || AC_MSG_NOTICE([   Documentation disabled])
