#!/bin/sh

dir=`dirname $0`
suite="fail"
DOC_MODULE="tester"
failed=0
tested=0

cd $dir/$suite/docs

echo "Running suite(s): gtk-doc-$suite";

# tests
# check missing section description
grep >/dev/null "tester:Long_Description" $DOC_MODULE-undocumented.txt
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

# summary
echo "tested : $tested, failed : $failed"
rate=$((100*($tested - $failed)/$tested));
echo "$rate %: Checks $tested, Failures: $failed"
exit `test $failed = 0`;
