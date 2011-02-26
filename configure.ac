dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.58)

dnl Use a simple 2-digit version number for a while, since our old example
dnl Makefile can only cope with that, i.e. use 1.1, 1.2, 1.3 ... 9.9.
dnl FIXME: I can't see anything failing (1.14.1), lets try to use a three digit
dnl number for the development version
m4_define(gtk_doc_version, 1.17)

AC_INIT([gtk-doc], [gtk_doc_version], [http://bugzilla.gnome.org/enter_bug.cgi?product=gtk-doc])

AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([gtkdoc-common.pl.in])

AM_INIT_AUTOMAKE([check-news std-options -Wno-portability])
AM_MAINTAINER_MODE([enable])

# Support silent build rules, requires at least automake-1.11. Disable
# by either passing --disable-silent-rules to configure or passing V=1
# to make
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

dnl Forcing a non-null ACTION-IF-NOT-FOUND disables scrollkeeper if
dnl gnome-doc-utils is not found but does not invalidate the build.
GNOME_DOC_INIT([],[],enable_scrollkeeper=no)

# Check for programs
AC_ISC_POSIX
AC_PROG_CC
AC_PROG_LIBTOOL

dnl Make sure we have pkg-config >= 0.19, so installing in $(datadir) is OK.
PKG_PROG_PKG_CONFIG([0.19])

dnl
dnl Check for Perl.
dnl
AC_PATH_PROG([PERL], [perl])
if test -z "$PERL"; then
	AC_MSG_ERROR([perl not found])
fi

AC_MSG_CHECKING([if Perl version >= 5.6.0])
if "$PERL" -e "require v5.6.0"; then
	AC_MSG_RESULT([yes])
else
	AC_MSG_RESULT([no])
	AC_MSG_ERROR([perl >= 5.6.0 is required for gtk-doc])
fi

dnl
dnl Check for Python.
dnl
AM_PATH_PYTHON([2.3],,[:])
AM_CONDITIONAL([HAVE_PYTHON], [test "$PYTHON" != :])

dnl
dnl Check for jade or openjade.
dnl
dnl We prefer to use openjade with the '-t sgml-raw' option, since '-t sgml'
dnl adds a newline before the closing '>' of HTML tags. lynx can't parse
dnl that, which is bad for accessibility.
dnl
SGML_FORMAT_TYPE=sgml-raw
AC_PATH_PROG([JADE], [openjade])
if test -z "$JADE"; then
	SGML_FORMAT_TYPE=sgml
	AC_PATH_PROG([JADE], [jade])
	if test -z "$JADE"; then
		AC_MSG_WARN([Could not find openjade or jade, so SGML is not supported])
	fi
fi
AC_SUBST([SGML_FORMAT_TYPE])

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
dnl Check for syntax highlighters
dnl
AC_ARG_WITH([highlight],
	AS_HELP_STRING([--with-highlight], [Select source code syntax highlighter (no|source-highlight|highlight|vim|auto)]),
	, [with_highlight=auto])

case $with_highlight in
	no|source-highlight|highlight|vim|auto) ;;
	*) AC_MSG_ERROR([Invalid value for syntax highlighting option.]) ;;
esac

HIGHLIGHT_OPTIONS=""
if test "$with_highlight" = "auto"; then
	AC_PATH_PROG([HIGHLIGHT], [source-highlight])
	if test -n "$HIGHLIGHT"; then
		HIGHLIGHT_OPTIONS="-t4 -sc -cstyle.css --no-doc -i"
	else
		AC_PATH_PROG([HIGHLIGHT], [highlight])
		if test -n "$HIGHLIGHT"; then
			HIGHLIGHT_OPTIONS="-X -f --class-name=gtkdoc "
		else
			AC_PATH_PROG([HIGHLIGHT], [vim])
			if test -n "$HIGHLIGHT"; then
				dnl vim is useless if it does not support syntax highlighting
				AC_MSG_CHECKING([whether vim has +syntax feature])
				if $HIGHLIGHT --version | grep '+syntax' >/dev/null; then
					AC_MSG_RESULT([yes])
				else
					AC_MSG_RESULT([no])
					HIGHLIGHT=
				fi
			fi
		fi
	fi
else
	if test "$with_highlight" != "no"; then
		AC_PATH_PROG([HIGHLIGHT], [$with_highlight], [no])
	fi

	case $with_highlight in
		source-highlight) HIGHLIGHT_OPTIONS="-t4 -sc -cstyle.css --no-doc -i";;
		highlight) HIGHLIGHT_OPTIONS="-X -f --class-name=gtkdoc ";;
		vim)
			AC_MSG_CHECKING([whether vim has +syntax feature])
			if $HIGHLIGHT --version | grep '+syntax' >/dev/null; then
				AC_MSG_RESULT([yes])
			else
				AC_MSG_RESULT([no])
				HIGHLIGHT=no
			fi
		;;
	esac

	if test "$HIGHLIGHT" = "no" && test "$with_highlight" != "no"; then
		AC_MSG_ERROR([Could not find requested syntax highlighter])
	fi
fi
AC_SUBST([HIGHLIGHT_OPTIONS])

dnl
dnl Set PACKAGE_DATA_DIR so we can find the script containing common routines.
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
dnl this enable the rule in test/Makefile.am
AM_CONDITIONAL(BUILD_TESTS, test x$build_tests = xyes)
AC_SUBST(glib_prefix)

dnl enable runtime debugging code
AC_MSG_CHECKING(whether to enable runtime debugging code)
AC_ARG_ENABLE([debug],
	AS_HELP_STRING([--enable-debug],
	[enable runtime debugging code (default=no)]),,
	[enable_debug="no"])
AC_MSG_RESULT($enable_debug)

if test "$enable_debug" = "yes"; then
	TRACE="print __FILE__ . \":\" . __LINE__ . \":\" ."
else
	TRACE="#"
fi
AC_SUBST(TRACE)

AC_CONFIG_FILES([Makefile
gtk-doc.pc
gtk-doc.dsl
gtk-doc.spec
gtk-doc.cat
gtkdoc-common.pl
help/Makefile
help/manual/Makefile
tests/Makefile
tests/gobject/Makefile
tests/gobject/src/Makefile
tests/gobject/docs/Makefile
tests/gobject/docs-tmpl/Makefile
tests/bugs/Makefile
tests/bugs/src/Makefile
tests/bugs/docs/Makefile
tests/annotations/Makefile
tests/annotations/src/Makefile
tests/annotations/docs/Makefile
tests/fail/Makefile
tests/fail/src/Makefile
tests/fail/docs/Makefile
tests/empty/Makefile
tests/empty/src/Makefile
tests/empty/docs/Makefile
])

dnl run chmod on these after parsing them.
AC_CONFIG_FILES([gtkdoc-check],    [chmod +x gtkdoc-check])
AC_CONFIG_FILES([gtkdoc-depscan],  [chmod +x gtkdoc-depscan])
AC_CONFIG_FILES([gtkdoc-fixxref],  [chmod +x gtkdoc-fixxref])
dnl that would be nice, but would fail if perl is in a non-std path
dnl AC_CONFIG_FILES([gtkdoc-mkdb],     [chmod +x gtkdoc-mkdb && perl -cwT gtkdoc-mkdb])
AC_CONFIG_FILES([gtkdoc-mkdb],     [chmod +x gtkdoc-mkdb])
AC_CONFIG_FILES([gtkdoc-mkhtml],   [chmod +x gtkdoc-mkhtml])
AC_CONFIG_FILES([gtkdoc-mkman],    [chmod +x gtkdoc-mkman])
AC_CONFIG_FILES([gtkdoc-mkpdf],    [chmod +x gtkdoc-mkpdf])
AC_CONFIG_FILES([gtkdoc-mktmpl],   [chmod +x gtkdoc-mktmpl])
AC_CONFIG_FILES([gtkdoc-rebase],   [chmod +x gtkdoc-rebase])
AC_CONFIG_FILES([gtkdoc-scan],     [chmod +x gtkdoc-scan])
AC_CONFIG_FILES([gtkdoc-scangobj], [chmod +x gtkdoc-scangobj])
AC_CONFIG_FILES([gtkdoc-scanobj],  [chmod +x gtkdoc-scanobj])
AC_CONFIG_FILES([gtkdocize],       [chmod +x gtkdocize])
AC_CONFIG_FILES([tests/tools.sh],  [chmod +x tests/tools.sh])
AC_OUTPUT

AC_MSG_NOTICE([
gtk-doc was configured with the following options:
==================================================])

test "$PYTHON" != : \
    && AC_MSG_NOTICE([** Python based tools enabled, using $PYTHON]) \
    || AC_MSG_NOTICE([   Python based tools disabled])
test -n "$JADE" \
    && AC_MSG_NOTICE([** SGML support enabled, using $JADE]) \
    || AC_MSG_NOTICE([   SGML support disabled, no jade processor available])
test -n "$DBLATEX$FOP" \
    && AC_MSG_NOTICE([** XML PDF support enabled, using $DBLATEX$FOP]) \
    || AC_MSG_NOTICE([   XML PDF support disabled, no fop available])
test "x$gdu_cv_have_gdu" = "xyes" \
    && AC_MSG_NOTICE([** Gnome-doc-utils support enabled]) \
    || AC_MSG_NOTICE([   Gnome-doc-utils support disabled])
test "x$enable_scrollkeeper" = "xyes" \
    && AC_MSG_NOTICE([** Scrollkeeper support enabled]) \
    || AC_MSG_NOTICE([   Scrollkeeper support disabled])
test -n "$HIGHLIGHT" \
    && AC_MSG_NOTICE([** Syntax highlighting of examples enabled, using $HIGHLIGHT]) \
    || AC_MSG_NOTICE([   Syntax highlighting of examples disabled])
test "x$build_tests" != "xno" \
    && AC_MSG_NOTICE([** Building regression tests]) \
    || AC_MSG_NOTICE([   Skipping regression tests])
