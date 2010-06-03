#!/bin/sh

dir=`dirname $0`
suite="sanity"

failed=0
tested=0

echo "Running suite(s): gtk-doc-$suite";

# check the presence and non-emptyness of certain files
nok=0
for path in $dir/*/docs*/html; do
  if test ! -s $path/index.html ; then nok=$(($nok + 1)); break; fi
  if test ! -s $path/index.sgml ; then nok=$(($nok + 1)); break; fi
  if test ! -s $path/home.png ; then nok=$(($nok + 1)); break; fi
done
if test $nok -gt 0 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))


# check online tags
nok=0
for file in $dir/*/docs*/html/index.sgml; do
  grep >/dev/null "<ONLINE href=" $file
  if test $? = 1 ; then nok=$(($nok + 1)); break; fi
  grep >/dev/null "<ANCHOR id=" $file
  if test $? = 1 ; then nok=$(($nok + 1)); break; fi
done
if test $nok -gt 0 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))


# check validity of generated xml files
nok=0
for file in $dir/*/docs*/xml/*.xml; do
  xmllint --noout --noent $file
  if test $? != 0 ; then
    nok=$(($nok + 1));
  fi
done
if test $nok -gt 0 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))


# check validity of generated sgml files
nok=0
for file in $dir/*/docs*/xml/*.sgml; do
  xmllint --noout --noent $file
  if test $? != 0 ; then
    nok=$(($nok + 1));
  fi
done
if test $nok -gt 0 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))


# summary
rate=$((100*($tested - $failed)/$tested));
echo "$rate %: Checks $tested, Failures: $failed"

test $failed = 0
exit $?
