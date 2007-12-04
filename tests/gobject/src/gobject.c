/**
 * SECTION:object
 * @short_description: class for gtk-doc unit test
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 * We can link to the #GtkdocObject:test property and the #GtkdocObject::test
 * signal.
 * A new instance can be created using the gtkdoc_object_new() function.
 */

#include <glib.h>
#include <glib-object.h>

#include "gobject.h"

/* property ids */

enum {
  GTKDOC_OBJECT_TEST=1
};

/* constructor methods */

/**
 * gtkdoc_object_new:
 *
 * Create a new instance
 *
 * Returns: the instance or %NULL in case of an error
 */
GtkdocObject *gtkdoc_object_new (void) {
  return(NULL);
}

/* methods */

/* class internals */

static void gtkdoc_object_get_property (GObject  *object, guint property_id,
    GValue *value, GParamSpec *pspec)
{

}

static void gtkdoc_object_set_property (GObject  *object, guint property_id,
    const GValue *value, GParamSpec *pspec)
{

}

static void gtkdoc_object_class_init (GtkdocObjectClass *klass) {
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);

  gobject_class->set_property = gtkdoc_object_set_property;
  gobject_class->get_property = gtkdoc_object_get_property;

  /**
   * GtkdocObject::test:
   * @self: myself
   *
   * The event has been triggered.
   */
  g_signal_new ("otest", G_TYPE_FROM_CLASS (klass),
                G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                G_STRUCT_OFFSET (GtkdocObjectClass,test),
                NULL, // accumulator
                NULL, // acc data
                g_cclosure_marshal_VOID__OBJECT,
                G_TYPE_NONE, // return type
                0); // n_params

  g_object_class_install_property (gobject_class,GTKDOC_OBJECT_TEST,
                                  g_param_spec_string ("otest",
                                     "otest prop",
                                     "dummy property for object",
                                     "dummy", /* default value */
                                     G_PARAM_READWRITE));

}

GType gtkdoc_object_get_type (void) {
  static GType type = 0;
  if (type == 0) {
    static const GTypeInfo info = {
      (guint16)sizeof(GtkdocObjectClass),
      NULL, // base_init
      NULL, // base_finalize
      (GClassInitFunc)gtkdoc_object_class_init, // class_init
      NULL, // class_finalize
      NULL, // class_data
      (guint16)sizeof(GtkdocObject),
      0,   // n_preallocs
      NULL, // instance_init
      NULL // value_table
    };
    type = g_type_register_static(G_TYPE_OBJECT,"GtkdocObject",&info,0);
  }
  return type;
}

