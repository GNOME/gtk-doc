// $Id$

#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>

#define _PADDDING 4
/**
 * bug_460127:
 * @a: field
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=460127
 */
struct _bug_460127 {
  /*< public >*/
  gint a;

  /*< private >*/
  union {
    struct {
      gint b;
    } ABI;
    gpointer _reserved[_PADDDING + 0];
  } abidata;

};

struct bug {
  int test;
};

void bug_141869_a (unsigned pid);
void bug_141869_b (signed pid);

void bug_379466 (int
  pid);

int bug_380824 (int arg);

struct bug *
bug_411739 (void);

void bug_419997 (int const_values);

void bug_445693 (unsigned long pid);

#endif // GTKDOC_TESTER_H

