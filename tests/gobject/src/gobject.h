#ifndef GTKDOC_OBJECT_H
#define GTKDOC_OBJECT_H

#include <glib.h>
#include <glib-object.h>

#define GTKDOC_TYPE_OBJECT            (gtkdoc_object_get_type ())
#define GTKDOC_OBJECT(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), GTKDOC_TYPE_OBJECT, GtkdocObject))
#define GTKDOC_OBJECT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), GTKDOCTYPE_OBJECT, GtkdocObjectClass))
#define GTKDOC_IS_OBJECT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GTKDOC_TYPE_OBJECT))
#define GTKDOC_IS_OBJECT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GTKDOC_TYPE_OBJECT))
#define GTKDOC_OBJECT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), GTKDOC_TYPE_OBJECT, GtkdocObjectClass))

/* type macros */

typedef struct _GtkdocObject GtkdocObject;
typedef struct _GtkdocObjectClass GtkdocObjectClass;

typedef struct GtkdocHelperStruct GtkdocHelperStruct;
typedef enum GtkdocHelperEnum GtkdocHelperEnum;

/**
 * GtkdocObject:
 *
 * instance data of gtk-doc unit test class
 */
struct _GtkdocObject {
  GObject parent;

  /*< private >*/
  gchar *test_string;
};

/**
 * GtkdocObjectClass:
 * @parent: this is a bug :/
 *
 * class data of gtk-doc unit test class
 */
struct _GtkdocObjectClass {
  GObjectClass parent;

  /* class methods */
  void (*test)(const GtkdocObject * const self, gconstpointer const user_data);
};

struct GtkdocHelperStruct {
  int a;
};

enum GtkdocHelperEnum {
  GTKDOC_HELPER_ENUM_A,
  GTKDOC_HELPER_ENUM_B
};

GType  gtkdoc_object_get_type(void) G_GNUC_CONST;

GtkdocObject *gtkdoc_object_new(void);

/**
 * GTKDOC_OBJECT_MACRO_DUMMY:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro does nothing.
 */
#define GTKDOC_OBJECT_MACRO_DUMMY(parameter_1,parameter_2) /* do nothing */

/**
 * GTKDOC_OBJECT_MACRO_SUM:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro adds its args.
 *
 * Return: the sum of @parameter_1 and @parameter_2
 */
#define GTKDOC_OBJECT_MACRO_SUM(parameter_1,parameter_2) \
  ((parameter_1) + (parameter_2))

#define _GTKDOC_OBJECT_INTERNAL_MACRO /* do nothing */

#endif // GTKDOC_OBJECT_H

