#!/bin/sh

suite=$1
dir=`dirname $0`

make -C $dir/$suite/docs/ clean check

cd $dir/$suite/docs && \
env BUILDDIR=$BUILDDIR/$suite/docs SRCDIR=$SRCDIR/$suite/docs gtkdoc-check
