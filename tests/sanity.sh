#!/bin/sh

suite=$1
dir=$BUILDDIR

failed=0
tested=0

echo "Running suite(s): gtk-doc-sanity $suite";

# check the presence and non-emptyness of certain files
nok=0
for path in $dir/$suite/docs/html; do
  if test ! -s $path/index.html ; then
    echo 1>&2 "no or empty $path/index.html"
    nok=`expr $nok + 1`; break;
  fi
  if test ! -s $path/home.png ; then
    echo 1>&2 "no or empty $path/home.png"
    nok=`expr $nok + 1`; break;
  fi
  file=`echo $path/*.devhelp2`
  if test ! -s $file ; then
    echo 1>&2 "no or empty $file"
    nok=`expr $nok + 1`; break;
  fi
done
if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
tested=`expr $tested + 1`

# TODO: if we have pdf support check for ./tests/$suite/docs/tester.pdf
nok=0
for path in $dir/$suite/docs; do
  if test ! -s $path/tester.pdf ; then
    if test -s $path/gtkdoc-mkpdf.log; then
      if ! grep >/dev/null 2>&1 "must be installed to use gtkdoc-mkpdf" $path/gtkdoc-mkpdf.log; then
        echo 1>&2 "no or empty $path/tester.pdf"
        nok=`expr $nok + 1`; break;
      fi
    fi
  fi
done
if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
tested=`expr $tested + 1`

# check validity of generated xml files
nok=0
for file in $dir/$suite/docs/xml/*.xml; do
  xmllint --noout --noent $file
  if test $? != 0 ; then
    echo 1>&2 "xml validity check failed for $file"
    nok=`expr $nok + 1`;
  fi
done
if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
tested=`expr $tested + 1`


# check validity of generated sgml files (if any)
if ls $dir/$suite/docs/xml/*.sgml 1> /dev/null 2>&1; then
  nok=0
  for file in $dir/$suite/docs/xml/*.sgml; do
    xmllint --noout --noent $file
    if test $? != 0 ; then
      echo 1>&2 "sgml validity check failed for $file"
      nok=`expr $nok + 1`;
    fi
  done
  if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
  tested=`expr $tested + 1`
fi

# check validity of devhelp2 files
nok=0
for file in $dir/$suite/docs/html/*.devhelp2; do
  xmllint --noout --nonet --schema $ABS_TOP_SRCDIR/devhelp2.xsd $file
  if test $? != 0 ; then
    echo 1>&2 "devhelp2 xml validity check failed for $file"
    nok=`expr $nok + 1`;
  fi
done
if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
tested=`expr $tested + 1`

nok=0
# check that log files have only one line (the command)
# - discard references to launchapd bugs
# - discard errors for missing optional tools.
DISCARD_PATTERN1='Please fix https://bugs.launchpad.net/ubuntu/+source/gtk-doc/+bug/[0-9]* . For now run:
gunzip .*.gz

'
DISCARD_PATTERN2='dblatex or fop must be installed.'
for file in $dir/$suite/docs/gtkdoc-*.log; do
  # skip this in verbose mode as we'll have more text
  if test "x${V}" = "x1"; then
    continue
  fi

  expected_lines="1"
  # adjust for known files
  if test $file = "$dir/bugs/docs/gtkdoc-mkdb.log"; then
    expected_lines="2"
  fi
  if test $file = "$dir/gobject/docs/gtkdoc-fixxref.log"; then
    expected_lines="2"
  fi
  case $file in
  *gtkdoc-fixxref.log)
    # if there is no /usr/share/gtk-doc/html/gobject we should skip fixxref logs
    if test ! -d "$GLIB_PREFIX/share/gtk-doc/html/gobject"; then
      continue
    fi
    ;;
  esac

  # count expected lines
  lines=`grep -v -x -G -e "$DISCARD_PATTERN1" $file | grep -v -x -G -e "$DISCARD_PATTERN2" | wc -l | cut -d' ' -f1`
  if test $lines -gt $expected_lines; then
    echo 1>&2 "expected no more than $expected_lines log line in $file, but got $lines"
    nok=`expr $nok + 1`;
  fi
done
if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
tested=`expr $tested + 1`

# check stability of generated xml/html
nok=0
for path in $dir/$suite/docs*; do
  if test -d $path/xml.ref; then
    diff -u $path/xml.ref $path/xml
    if test $? = 1 ; then
      echo 1>&2 "difference in generated xml for $path"
      nok=`expr $nok + 1`;
    fi
  fi
  if test -d $path/html.ref; then
    diff -u $path/html.ref $path/html
    if test $? = 1 ; then
      echo 1>&2 "difference in generated html for $path"
      nok=`expr $nok + 1`;
    fi
  fi
done
if test $nok -gt 0 ; then failed=`expr $failed + 1`; fi
tested=`expr $tested + 1`


# summary
successes=`expr $tested - $failed`
rate=`expr 100 \* $successes / $tested`;
echo "$rate %: Checks $tested, Failures: $failed"

test $failed = 0
exit $?
