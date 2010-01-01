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
 * @const_values: arg
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


/**
 * bug_471014:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=471014
 *
 * Returns: result
 */
G_CONST_RETURN gchar* G_CONST_RETURN * bug_471014 (void) {
  return NULL;
}


/**
 * Bug446648:
 * @BUG_446648_FOO: foo
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=446648
 **/


/**
 * bug_552602:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=552602
 *
 * Returns: result
 */
const char* const * bug_552602 (void) {
  return NULL;
}

/**
 * bug_574654a:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=574654
 *
 * Returns: result
 */
/**
 * bug_574654b:
 * @offset: skip this many items
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=574654
 */
int bug_574654a(void) {
  return 0;
}

void bug_574654b(double offset) { }


/**
 * bug_580300a_get_type:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 */
void bug_580300a_get_type(void) { }

/**
 * bug_580300b_get_type:
 * @a: value
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 */
void bug_580300b_get_type(gint a) { }

/**
 * bug_580300c_get_type:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 */
void bug_580300c_get_type() { }

/**
 * bug_580300d_get_type:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 *
 * Returns: result
 */
int bug_580300d_get_type() { }


/**
 * bug_602518a:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=602518
 *
 * Returns: result
 */
long int bug_602518a(void) {
  return (long int)0;
}

/**
 * bug_602518b:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=602518
 *
 * Returns: result
 */
unsigned long int bug_602518b(void) {
  return (unsigned long int)0;
}

/**
 * bug_602518c:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=602518
 *
 * Returns: result
 */
unsigned int bug_602518c(void) {
  return (unsigned int)0;
}
