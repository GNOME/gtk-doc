#!/bin/sh

suite=$1

if test -s $suite/docs/tester-unused.txt; then
  echo "unused symbols found"
  exit 1
fi

cov=`head -n 1 $suite/docs/tester-undocumented.txt | cut -d\% -f1`
if test "$cov" != "100"; then
  echo "undocumented symbols found"
  exit 1
fi

# TODO add more checks

exit 0

