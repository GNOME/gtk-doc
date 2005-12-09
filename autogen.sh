#!/bin/sh
# Run this to generate all the initial makefiles, etc.

PROJECT=gtk-doc
TEST_TYPE=-f
FILE=gtk-doc.dsl.in

# a silly hack that generates autoregen.sh but it's handy
echo "#!/bin/sh" > autoregen.sh
echo "./autogen.sh $@ \$@" >> autoregen.sh
chmod +x autoregen.sh

DIE=0

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

THEDIR="`pwd`"

cd "$srcdir"

(autoconf --version) < /dev/null > /dev/null 2>&1 || {
	echo
	echo "You must have autoconf installed to compile $PROJECT."
	echo "Download the appropriate package for your distribution,"
	echo "or get the source tarball at ftp://ftp.gnu.org/gnu/autoconf/"
	DIE=1
}

if automake-1.9 --version < /dev/null > /dev/null 2>&1; then
    AUTOMAKE=automake-1.9
    ACLOCAL=aclocal-1.9
elif automake-1.8 --version < /dev/null > /dev/null 2>&1; then
    AUTOMAKE=automake-1.8
    ACLOCAL=aclocal-1.8
elif automake-1.7 --version < /dev/null > /dev/null 2>&1; then
    AUTOMAKE=automake-1.7
    ACLOCAL=aclocal-1.7
elif automake-1.6 --version < /dev/null > /dev/null 2>&1; then
    AUTOMAKE=automake-1.6
    ACLOCAL=aclocal-1.6
else
	echo
	echo "You must have automake installed to compile $PROJECT."
	echo "Download the appropriate package for your distribution,"
	echo "or get the source tarball at ftp://ftp.gnu.org/gnu/automake/"
	DIE=1
fi

if test "$DIE" -eq 1; then
	exit 1
fi

test $TEST_TYPE $FILE || {
	echo "You must run this script in the top-level $PROJECT directory"
	exit 1
}

if test "$#" = 0; then
	echo "I am going to run ./configure with no arguments - if you wish "
        echo "to pass any to it, please specify them on the $0 command line."
fi

$ACLOCAL $ACLOCAL_FLAGS || exit $?

autoconf || exit $?
# optionally feature autoheader
#(autoheader --version)  < /dev/null > /dev/null 2>&1 && autoheader

$AUTOMAKE --add-missing $am_opt || exit $?

cd "$THEDIR"

$srcdir/configure --enable-maintainer-mode "$@" || exit $?

echo 
echo "Now type 'make install' to install $PROJECT."
