// $Id$
/**
 * SECTION:tester
 * @short_description: module for gtk-doc unit test
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 *
 * As described in http://bugzilla.gnome.org/show_bug.cgi?id=457077 it
 * returns nothing.
 */

#include <glib.h>

#include "tester.h"

//-- methods

/**
 * bug_141869_a:
 * @pid: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=141869
 */
void bug_141869_a (unsigned pid) {
}

/**
 * bug_141869_b:
 * @pid: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=141869
 */
void bug_141869_b (signed pid) {
}


/**
 * bug_379466:
 * @pid: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=379466
 */
void bug_379466 (int
  pid) {
}


/**
 * bug_380824:
 * @arg: arg
 *
 * Returns a value.
 * http://bugzilla.gnome.org/show_bug.cgi?id=380824
 *
 * Since: 0.1
 *
 * Returns: result
 */
int bug_380824 (int arg) {
  return 0;
}

/**
 * bug_411739:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=411739
 *
 * Returns: result
 */

struct bug *
bug_411739 (void) {
  return NULL;
}


/**
 * bug_419997:
 * @pid: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=419997
 */
void bug_419997 (int const_values) {
}


/**
 * bug_445693:
 * @pid: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=445693
 */
void bug_445693 (unsigned long pid) {
}

