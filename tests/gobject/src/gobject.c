/**
 * SECTION:object
 * @title: GtkdocObject
 * @short_description: class for gtk-doc unit test
 * @see_also: #GtkdocIface
 * @Image: object.png
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 * We can link to the #GtkdocObject:otest property and the #GtkdocObject::otest
 * signal.
 *
 * When subclassing it is useful to override the #GtkdocObjectClass.test()
 * method. The #GtkdocObjectClass.foo_bar() vmethod lets you refine your
 * frobnicator.
 *
 * A new instance can be created using the gtkdoc_object_new() function. The
 * whole lifecycle usualy looks like shown in this example:
 * |[<!-- language="C" -->
 * GObject *myobj;
 *
 * myobj = gtkdoc_object_new();
 * // do something
 * g_object_unref (myobj);
 * ]|
 *
 * # Examples #
 *
 * Here are a few examples.
 *
 * ## Example 1 ##
 *
 * You can also change parameters:
 * <informalexample>
 * <programlisting language="c"><xi:include xmlns:xi="http://www.w3.org/2003/XInclude" parse="text" href="../../examples/gobject.c" /></programlisting>
 * </informalexample>
 *
 * This example serves two main purposes:
 *
 * - testing conversion (long description
 *   follows here)
 *
 * - catching bugs
 *
 * - having an example
 *
 * # Discussion
 *
 * This is a section with a heading without a trailing hash mark.
 *
 * <orderedlist>
 * <listitem><para>
 * This list is here to ensure the parsing of the above list
 * </para></listitem>
 * <listitem><para>
 * Doesn't change it.
 * </para></listitem>
 * </orderedlist>
 *
 * This example serves two main purposes:
 *
 * * testing alternate list syntax
 *
 *   With section text in each.
 *
 * * not sure if we want this one
 *
 *   It has more stuff.
 *
 * # Coda #
 *
 * 1. This is a ordered list
 *
 * 1. This is a code block in a list:
 *    |[<!-- language="C" -->
 *    GObject *myobj;
 *
 *    myobj = gtkdoc_object_new();
 *    // do something
 *    g_object_unref (myobj);
 *    ]|
 *    And another:
 *    |[<!-- language="C" -->
 *    GObject *myobj;
 *
 *    myobj = gtkdoc_object_new();
 *    // do something
 *    g_object_unref (myobj);
 *    ]|
 *
 * 1. Really
 *
 *    Has a paragraph.
 *
 * 1. Is
 *
 * Nothing more to say.
 */

/**
 * SECTION:object2
 * @title: GtkdocObject2
 * @short_description: class with interface for gtk-doc unit test
 * @see_also: #GtkdocIface
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 *
 * Internals
 * =========
 *
 * All the internal details go here or not:
 *
 * - single item list
 */

#include <glib.h>
#include <glib-object.h>

#include "gobject.h"
#include "giface.h"

/* property ids */

enum {
  GTKDOC_OBJECT_TEST=1,
  GTKDOC_OBJECT_DEP_TEST
};

enum {
  GTKDOC_OBJECT2_ITEST=1
};

/* constructor methods */

/**
 * gtkdoc_object_new:
 *
 * Create a new instance
 * <note><para>
 *   This will only work if you have called g_type_init() before.
 * </para></note>
 *
 * Returns: the instance or %NULL in case of an error
 * Since: 0.1
 */
GtkdocObject *gtkdoc_object_new (void) {
  return(NULL);
}

/* methods */

/**
 * gtkdoc_object_set_otest:
 * @self: the object
 * @value: the new otest value, whose description extends further than one
 *  line will allow
 *
 * Set the #GtkdocObject:otest property. This is a long paragraph.
 *
 * Oh, btw. setting the property directly saves us one method.
 *
 * Deprecated: Use g_object_set(obj,&quot;otest&quot;,value,NULL); instead.
 * Since: 0.5
 */
void gtkdoc_object_set_otest (GObject *self, const gchar *value) {

}

/**
 * gtkdoc_object_frobnicate:
 * @self: the object
 * @n: number of iterations
 *
 * Frobnicate the content of @self @n times. This implements a
 * complex algorithm (http://en.wikipedia.org/wiki/Algorithm).
 * <footnote>
 *  <para>
 *    Negative frobnication can lead to unexpected behaviour.
 *  </para>
 * </footnote>
 *
 * Since: 0.5
 */
void gtkdoc_object_frobnicate (GObject *self, gint n) {

}

/**
 * gtkdoc_object_fooify:
 * @self: the object
 * @...: a NULL terminated list of arguments
 *
 * Fooify the content of @self.
 *
 * Returns: %TRUE for success
 */
gboolean gtkdoc_object_fooify (GObject *self, ...) {
  return TRUE;
}

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
   * GtkdocObject::otest:
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

  /**
   * GtkdocObject::dep-otest:
   * @self: myself
   *
   * Here's an example signal handler.
   * |[
   * static gchar*
   * otest_callback (GObject  *o,
   *                 gpointer  user_data)
   * {
   *   gdouble      value;
   *
   *   value = abs (o->value);
   *
   *   return value;
   * }
   * ]|
   *
   * Deprecated: Use the #GtkdocObject::otest signal instead.
   */
  g_signal_new ("dep-otest", G_TYPE_FROM_CLASS (klass),
                G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                G_STRUCT_OFFSET (GtkdocObjectClass,test),
                NULL, // accumulator
                NULL, // acc data
                g_cclosure_marshal_VOID__OBJECT,
                G_TYPE_NONE, // return type
                0); // n_params

  /**
   * GtkdocObject::strings-changed:
   *
   * Something has happened.
   */
  g_signal_new ("strings-changed", G_TYPE_FROM_CLASS (klass),
                G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                0,
                NULL, // accumulator
                NULL, // acc data
                g_cclosure_marshal_VOID__BOXED,
                G_TYPE_NONE, // return type
                1, G_TYPE_STRV); // n_params

#if GLIB_CHECK_VERSION (2, 25, 9)
  /**
   * GtkdocObject::variant-changed:
   *
   * Something has happened.
   */
  g_signal_new ("variant-changed", G_TYPE_FROM_CLASS (klass),
                G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                0,
                NULL, // accumulator
                NULL, // acc data
                g_cclosure_marshal_VOID__VARIANT,
                G_TYPE_NONE, // return type
                1, G_TYPE_VARIANT); // n_params
#endif

  /**
   * GtkdocObject:otest:
   *
   * Since: 0.1
   */
  g_object_class_install_property (gobject_class,GTKDOC_OBJECT_TEST,
                                  g_param_spec_string ("otest",
                                     "otest prop",
                                     "dummy property for object",
                                     "dummy", /* default value */
                                     G_PARAM_READWRITE));

  /**
   * GtkdocObject:dep-otest:
   *
   * Deprecated: use #GtkdocObject:otest property
   */
  g_object_class_install_property (gobject_class,GTKDOC_OBJECT_DEP_TEST,
                                  g_param_spec_string ("dep-otest",
                                     "dep-otest prop",
                                     "dummy deprecated property for object",
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
      0,    // n_preallocs
      NULL, // instance_init
      NULL  // value_table
    };
    type = g_type_register_static(G_TYPE_OBJECT,"GtkdocObject",&info,0);
  }
  return type;
}


static void gtkdoc_object2_class_init (GtkdocObjectClass *klass) {
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);

  gobject_class->set_property = gtkdoc_object_set_property;
  gobject_class->get_property = gtkdoc_object_get_property;

  g_object_class_override_property (gobject_class, GTKDOC_OBJECT2_ITEST, "itest");
}

GType gtkdoc_object2_get_type (void) {
  static GType type = 0;
  if (type == 0) {
    static const GTypeInfo info = {
      (guint16)sizeof(GtkdocObject2Class),
      NULL, // base_init
      NULL, // base_finalize
      (GClassInitFunc)gtkdoc_object2_class_init, // class_init
      NULL, // class_finalize
      NULL, // class_data
      (guint16)sizeof(GtkdocObject2),
      0,    // n_preallocs
      NULL, // instance_init
      NULL  // value_table
    };
    static const GInterfaceInfo interface_info = {
      NULL,  // interface_init
      NULL,  // interface_finalize
      NULL   // interface_data
    };
    type = g_type_register_static(G_TYPE_OBJECT,"GtkdocObject2",&info,0);
    g_type_add_interface_static(type, GTKDOC_TYPE_IFACE, &interface_info);
  }
  return type;
}

