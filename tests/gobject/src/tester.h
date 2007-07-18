// $Id$

#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>
#include <glib-object.h>

#define GTKDOC_TYPE_TESTER            (gtkdoc_tester_get_type ())
#define GTKDOC_TESTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), GTKDOC_TYPE_TESTER, GtkdocTester))
#define GTKDOC_TESTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), GTKDOCTYPE_TESTER, GtkdocTesterClass))
#define GTKDOC_IS_TESTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GTKDOC_TYPE_TESTER))
#define GTKDOC_IS_TESTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GTKDOC_TYPE_TESTER))
#define GTKDOC_TESTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), GTKDOC_TYPE_TESTER, GtkdocTesterClass))

/* type macros */

typedef struct _GtkdocTester GtkdocTester;
typedef struct _GtkdocTesterClass GtkdocTesterClass;

/**
 * GtkdocTester:
 *
 * instance data of gtk-doc unit test class
 */
struct _GtkdocTester {
  GObject parent;

  /*< private >*/
  gchar *test_string;
};

/**
 * GtkdocTesterClass:
 * @parent: this is a bug :/
 *
 * class data of gtk-doc unit test class
 */
struct _GtkdocTesterClass {
  GObjectClass parent;

  /* class methods */
  void (*test)(const GtkdocTester * const self, gconstpointer const user_data);
};

GType  gtkdoc_tester_get_type(void) G_GNUC_CONST;

GtkdocTester *gtkdoc_tester_new(void);

/**
 * GTKDOC_TESTER_MACRO_DUMMY:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro does nothing.
 */
#define GTKDOC_TESTER_MACRO_DUMMY(parameter_1,parameter_2) /* do nothing */

/**
 * GTKDOC_TESTER_MACRO_SUM:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro adds its args.
 *
 * Return: the sum of @parameter_1 and @parameter_2
 */
#define GTKDOC_TESTER_MACRO_SUM(parameter_1,parameter_2) \
  ((parameter_1) + (parameter_2))

#define _GTKDOC_TESTER_INTERNAL_MACRO /* do nothing */

#endif // GTKDOC_TESTER_H

