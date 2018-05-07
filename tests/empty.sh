#!/bin/sh

set -e

if ! grep -q ^GtkDocTestIf$ empty/docs/tester-sections.txt; then
    echo "Test for bug https://bugzilla.gnome.org/show_bug.cgi?id=705633 has failed."
    exit 1
fi

gtkdoctest.sh empty
sanity.sh empty
