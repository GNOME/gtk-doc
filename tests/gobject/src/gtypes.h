#ifndef GTKDOC_TYPES_H
#define GTKDOC_TYPES_H

#include <glib.h>
#include <glib-object.h>

/* type macros */

#define GTKDOC_TYPE_ENUM              (gtkdoc_enum_get_type ())
#define GTKDOC_TYPE_ENUM2             (gtkdoc_enum2_get_type ())
#define GTKDOC_TYPE_BOXED             (gtkdoc_boxed_get_type ())

/**
 * GtkdocEnum:
 * @GTKDOC_ENUM_V1: first
 * @GTKDOC_ENUM_V2: second
 *    Since: 0.5
 *
 * Enum values for the #GtkdocEnum type.
 */
typedef enum {
  GTKDOC_ENUM_V1=0,
  GTKDOC_ENUM_V2,
  /*< private >*/
  GTKDOC_ENUM_V3
} GtkdocEnum;

/**
 * GtkdocEnum2:
 * @GTKDOC_ENUM2_V1: first
 * @GTKDOC_ENUM2_V2: second
 *
 * Enum values for the #GtkdocEnum2 type.
 */
typedef enum {
  GTKDOC_ENUM2_V1=0,
  GTKDOC_ENUM2_V2,
} GtkdocEnum2;

GType  gtkdoc_enum_get_type(void) G_GNUC_CONST;
GType  gtkdoc_enum2_get_type(void) G_GNUC_CONST;
GType  gtkdoc_boxed_get_type(void) G_GNUC_CONST;


/**
 * GtkdocPlainOldData:
 * @n: Some integer member.
 * @x: Some floating point member.
 *
 * Unboxed plain old data that should default to public members.
 **/
typedef struct {
    guint n;
    gdouble x;
    /*<private>*/
    gpointer priv;
} GtkdocPlainOldData;

#define GTKDOC_TYPE_BOXED_PLAIN_OLD_DATA (gtkdoc_boxed_plain_old_data_get_type ())

/**
 * GtkdocBoxedPlainOldData:
 * @n: Some integer member.
 * @x: Some floating point member.
 *
 * Boxed plain old data that should default to public members.
 **/
typedef struct {
    guint n;
    gdouble x;
    /*<private>*/
    gpointer priv;
} GtkdocBoxedPlainOldData;

GType  gtkdoc_boxed_plain_old_data_get_type(void) G_GNUC_CONST;

#endif // GTKDOC_TYPES_H

