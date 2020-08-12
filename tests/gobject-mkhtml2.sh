#!/bin/sh

set -e

gtkdoctest.sh gobject-mkhtml2
sanity.sh gobject-mkhtml2
