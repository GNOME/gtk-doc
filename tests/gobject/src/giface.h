#ifndef GTKDOC_IFACE_H
#define GTKDOC_IFACE_H

#include <glib.h>
#include <glib-object.h>

/* type macros */

#define GTKDOC_TYPE_IFACE               (gtkdoc_iface_get_type ())
#define GTKDOC_IFACE(obj)               (G_TYPE_CHECK_INSTANCE_CAST ((obj), GTKDOC_TYPE_IFACE, GtkdocIface))
#define GTKDOC_IS_IFACE(obj)            (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GTKDOC_TYPE_IFACE))
#define GTKDOC_IFACE_GET_INTERFACE(obj) (G_TYPE_INSTANCE_GET_CLASS ((obj), GTKDOC_TYPE_IFACE, GtkdocIfaceInterface))

#define GTKDOC_TYPE_IFACE2              (gtkdoc_iface2_get_type ())

/* type structs */

/**
 * GtkdocIface:
 *
 * opaque instance of gtk-doc unit test interface
 */
typedef struct _GtkdocIface GtkdocIface;
typedef struct _GtkdocIfaceInterface GtkdocIfaceInterface;

/**
 * GtkdocIface2:
 *
 * opaque instance of gtk-doc unit test interface
 */
typedef struct _GtkdocIface2 GtkdocIface2;

/**
 * GtkdocIfaceInterface:
 * @parent: this is a bug :/
 * @test: overideable method
 *
 * class data of gtk-doc unit test interface
 */
struct _GtkdocIfaceInterface {
  GTypeInterface parent;

  /* class methods */
  void (*test)(const GtkdocIface * const self, gconstpointer const user_data);
};

GType  gtkdoc_iface_get_type(void) G_GNUC_CONST;
GType  gtkdoc_iface2_get_type(void) G_GNUC_CONST;

gboolean gtkdoc_iface_configure (gchar *config);

/**
 * GTKDOC_IFACE_MACRO_DUMMY:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro does nothing.
 */
#define GTKDOC_IFACE_MACRO_DUMMY(parameter_1,parameter_2) /* do nothing */

/**
 * GTKDOC_IFACE_MACRO_SUM:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro adds its args.
 *
 * Returns: the sum of @parameter_1 and @parameter_2
 */
#define GTKDOC_IFACE_MACRO_SUM(parameter_1,parameter_2) \
  ((parameter_1) + (parameter_2))

#define _GTKDOC_IFACE_INTERNAL_MACRO /* do nothing */

#endif // GTKDOC_IFACE_H

