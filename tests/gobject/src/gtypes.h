#ifndef GTKDOC_TYPES_H
#define GTKDOC_TYPES_H

#include <glib.h>
#include <glib-object.h>

/* type macros */

#define GTKDOC_TYPE_ENUM              (gtkdoc_enum_get_type ())
#define GTKDOC_TYPE_BOXED             (gtkdoc_boxed_get_type ())

/**
 * GtkdocEnum:
 * @GTKDOC_ENUM_V1: first
 * @GTKDOC_ENUM_V2: second
 *
 * Enum values for the #GtkdocEnum type.
 */
typedef enum {
  GTKDOC_ENUM_V1=0,
  GTKDOC_ENUM_V2,
  /*< private >*/
  GTKDOC_ENUM_V3
} GtkdocEnum;

GType  gtkdoc_enum_get_type(void) G_GNUC_CONST;
GType  gtkdoc_boxed_get_type(void) G_GNUC_CONST;


#endif // GTKDOC_TYPES_H

