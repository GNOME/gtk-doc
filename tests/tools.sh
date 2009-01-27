#!/bin/sh

failed=0
tested=0

echo "Running suite(s): gtk-doc-tools";

# tests
# I had the wonderful idea to check in configure.in if the generated tools are
# fine, like:
# - AC_CONFIG_FILES([gtkdoc-check],    [chmod +x gtkdoc-check])
# + AC_CONFIG_FILES([gtkdoc-check],    [chmod +x gtkdoc-check;$PERL -cwT gtkdoc-check])
# unfortunately configure creates config.status, which runs these command and
# this does not know about results of configure checks

/usr/bin/perl -cwT `which gtkdoc-check`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-fixxref`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-mkdb`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-mktmpl`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-rebase`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-scan`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-scangobj`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

/usr/bin/perl -cwT `which gtkdoc-scanobj`
if test $? = 1 ; then failed=$(($failed + 1)); fi
tested=$(($tested + 1))

# summary
echo "tested : $tested, failed : $failed"
rate=$((100*($tested - $failed)/$tested));
echo "$rate %: Checks $tested, Failures: $failed"
exit `test $failed = 0`;
