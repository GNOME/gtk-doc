// $Id$
/**
 * SECTION:tester
 * @short_description: class for gtk-doc unit test
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 * We can link to the #GtkdocTester:test property and the #GtkdocTester::test
 * signal.
 */

#include <glib.h>
#include <glib-object.h>

#include "tester.h"

//-- property ids

enum {
  GTKDOC_TESTER_TEST=1
};

//-- constructor methods

/**
 * gtkdoc_tester_new:
 *
 * Create a new instance
 *
 * Returns: the instance or %NULL in case of an error
 */
GtkdocTester *gtkdoc_tester_new(void) {
  return(NULL);
}

//-- methods

//-- wrapper

//-- class internals

/* returns a property for the given property_id for this object */
static void gtkdoc_tester_get_property(GObject      *object,
                               guint         property_id,
                               GValue       *value,
                               GParamSpec   *pspec)
{

}

/* sets the given properties for this object */
static void gtkdoc_tester_set_property(GObject      *object,
                              guint         property_id,
                              const GValue *value,
                              GParamSpec   *pspec)
{

}

static void gtkdoc_tester_class_init(GtkdocTesterClass *klass) {
  GObjectClass *gobject_class = G_OBJECT_CLASS(klass);

  gobject_class->set_property = gtkdoc_tester_set_property;
  gobject_class->get_property = gtkdoc_tester_get_property;

  /**
   * GtkdocTester::test:
   * @self: myself
   *
   * The event has been triggered.
   */
  g_signal_new("test", G_TYPE_FROM_CLASS(klass),
                G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                G_STRUCT_OFFSET(GtkdocTesterClass,test),
                NULL, // accumulator
                NULL, // acc data
                g_cclosure_marshal_VOID__OBJECT,
                G_TYPE_NONE, // return type
                0); // n_params

  g_object_class_install_property(gobject_class,GTKDOC_TESTER_TEST,
                                  g_param_spec_string("test",
                                     "test prop",
                                     "dummy property for test",
                                     "dummy", /* default value */
                                     G_PARAM_READWRITE));

}

GType gtkdoc_tester_get_type(void) {
  static GType type = 0;
  if (type == 0) {
    static const GTypeInfo info = {
      (guint16)sizeof(GtkdocTesterClass),
      NULL, // base_init
      NULL, // base_finalize
      (GClassInitFunc)gtkdoc_tester_class_init, // class_init
      NULL, // class_finalize
      NULL, // class_data
      (guint16)sizeof(GtkdocTester),
      0,   // n_preallocs
      NULL, // instance_init
      NULL // value_table
    };
    type = g_type_register_static(G_TYPE_OBJECT,"GtkdocTester",&info,0);
  }
  return type;
}

