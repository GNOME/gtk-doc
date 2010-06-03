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
# we can't just check for a missing "tester_nodocs" entry
grep >/dev/null "tester_nodocs:Long_Description" $DOC_MODULE-undocumented.txt
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

# check missing section long description
grep >/dev/null "tester_nolongdesc:Long_Description" $DOC_MODULE-undocumented.txt
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

# check missing section short description
grep >/dev/null "tester_noshortdesc:Short_Description" $DOC_MODULE-undocumented.txt
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

# check enums
grep >/dev/null "EnumNoItemDocs (<items>)" $DOC_MODULE-undocumented.txt
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

# summary
rate=$((100*($tested - $failed)/$tested));
echo "$rate %: Checks $tested, Failures: $failed"

test $failed = 0
exit $?
