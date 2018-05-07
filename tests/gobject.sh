#!/bin/sh

set -e

make -C `dirname $0`/gobject/src/ all

gtkdoctest.sh gobject
sanity.sh gobject
