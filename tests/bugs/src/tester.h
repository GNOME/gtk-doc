#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>

/**
 * bug_324535:
 * @BUG_324535_A: enum 1
 * @BUG_324535_B: enum 2
 * @BUG_324535_C: enum 3
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=324535
 */
typedef enum {
  BUG_324535_A,
#ifdef GTK_DISABLE_DEPRECATED
  BUG_324535_B,
#endif
  BUG_324535_C,
} bug_324535;


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


/**
 * bug_477532:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=477532
 */
GLIB_VAR guint64 (*bug_477532) (void);


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

G_CONST_RETURN gchar* G_CONST_RETURN *
bug_471014 (void);

#endif // GTKDOC_TESTER_H

