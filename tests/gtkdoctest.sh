#!/bin/sh

suite=$1
res=0

if test -s $suite/docs/tester-unused.txt; then
  echo "unused symbols found"
  res=1
fi

cov=`head -n 1 $suite/docs/tester-undocumented.txt | cut -d\% -f1`
if test "$cov" != "100"; then
  echo "undocumented symbols found"
  res=1
fi

# TODO add more checks
grep >/dev/null "WARNING:" $suite/docs/gtkdoc-mkdb.log
if test "$?" == "0" ; then
  echo "gtkdoc-mkdb run had warnings"
  res=1
fi

exit $res

