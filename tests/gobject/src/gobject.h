#ifndef GTKDOC_OBJECT_H
#define GTKDOC_OBJECT_H

#include <glib.h>
#include <glib-object.h>

/* type macros */

#define GTKDOC_TYPE_OBJECT            (gtkdoc_object_get_type ())
#define GTKDOC_OBJECT(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), GTKDOC_TYPE_OBJECT, GtkdocObject))
#define GTKDOC_OBJECT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), GTKDOCTYPE_OBJECT, GtkdocObjectClass))
#define GTKDOC_IS_OBJECT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GTKDOC_TYPE_OBJECT))
#define GTKDOC_IS_OBJECT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GTKDOC_TYPE_OBJECT))
#define GTKDOC_OBJECT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), GTKDOC_TYPE_OBJECT, GtkdocObjectClass))

#define GTKDOC_TYPE_OBJECT2           (gtkdoc_object2_get_type ())

#define GTKDOC_TYPE_OBJECT3           (gtkdoc_object3_get_type ())

/* type structs */

typedef struct _GtkdocObject GtkdocObject;
typedef struct _GtkdocObjectClass GtkdocObjectClass;

typedef struct _GtkdocObject2 GtkdocObject2;
typedef struct _GtkdocObject2Class GtkdocObject2Class;

typedef struct _GtkdocObject3 GtkdocObject3;
typedef struct _GtkdocObject3Class GtkdocObject3Class;

/* in gtkdoc-scan::ScanHeader() we currently skip the enums, but output a decl
* to -decl.txt and -decl-list.txt for the struct
* If the symbol has no docs, we get a warning in -unused.txt for the struct, but
* not the enum
*
typedef struct GtkdocHelperStruct GtkdocHelperStruct;
typedef enum GtkdocHelperEnum GtkdocHelperEnum;
*/

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
 * @test: overideable method
 * @ping: can be used before calling the @test() function
 * @foo_bar: lets you refine your frobnicator
 *
 * class data of gtk-doc unit test class
 */
struct _GtkdocObjectClass {
  GObjectClass parent;

  /* class methods */
  void (*test)(const GtkdocObject * const self, gconstpointer const user_data);
  gboolean (*ping)(const GtkdocObject * const self);
  gboolean (*foo_bar)(const GtkdocObject * const self);
};

/**
 * GtkdocObject2:
 *
 * instance data of gtk-doc unit test class
 */
struct _GtkdocObject2 {
  GObject parent;
};

/**
 * GtkdocObject2Class:
 * @parent: this is a bug :/
 *
 * class data of gtk-doc unit test class
 */
struct _GtkdocObject2Class {
  GObjectClass parent;
};

struct _GtkdocObject3 {
  GObject parent;
};

struct _GtkdocObject3Class {
  GObjectClass parent;
};


/**
 * GtkdocHelperStruct:
 * @a: field
 *
 * GtkdocHelperStruct
 */
struct GtkdocHelperStruct {
  int a;
};

/**
 * GtkdocHelperEnum:
 * @GTKDOC_HELPER_ENUM_A: enum a
 * @GTKDOC_HELPER_ENUM_B: enum b
 *
 * GtkdocHelperEnum
 */
enum GtkdocHelperEnum {
  GTKDOC_HELPER_ENUM_A,
  GTKDOC_HELPER_ENUM_B
};

GType  gtkdoc_object_get_type(void) G_GNUC_CONST;
GType  gtkdoc_object2_get_type(void) G_GNUC_CONST;
GType  gtkdoc_object3_get_type(void) G_GNUC_CONST;

GtkdocObject *gtkdoc_object_new(void);
#ifndef GTKDOC_TESTER_DISABLE_DEPRECATED
void gtkdoc_object_set_otest (GObject *self, const gchar *value);
void gtkdoc_object_do_not_use (GObject *self);
#endif
void gtkdoc_object_frobnicate (GObject *self, gint n);
gboolean gtkdoc_object_fooify (GObject *self, ...);

/**
 * GTKDOC_OBJECT_MACRO_DUMMY:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro does nothing.
 *
 * Since: 0.1
 */
#define GTKDOC_OBJECT_MACRO_DUMMY(parameter_1,parameter_2) /* do nothing */

/**
 * GTKDOC_OBJECT_MACRO_SUM:
 * @parameter_1: first arg
 * @parameter_2: second arg
 *
 * This macro adds its args.
 *
 * Returns: the sum of @parameter_1 and @parameter_2
 */
#define GTKDOC_OBJECT_MACRO_SUM(parameter_1,parameter_2) \
  ((parameter_1) + (parameter_2))

#define _GTKDOC_OBJECT_INTERNAL_MACRO /* do nothing */

#endif // GTKDOC_OBJECT_H

