/**
 * SECTION:types
 * @title: GtkdocTypes
 * @short_description: other gobject types for gtk-doc unit test
 * @see_also: #GtkdocObject, #GtkdocIface
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 */

#include "gtypes.h"

/* enum: class internals */

GType gtkdoc_enum_get_type (void) {
  static GType type = 0;
  if(type==0) {
    static const GEnumValue values[] = {
      { GTKDOC_ENUM_V1,          "GTKDOC_ENUM_V1",          "first" },
      { GTKDOC_ENUM_V2,          "GTKDOC_ENUM_V2",          "second" },
      { GTKDOC_ENUM_V3,          "GTKDOC_ENUM_V3",          "third" },
      { 0, NULL, NULL},
    };
    type = g_enum_register_static ("GtkdocEnum", values);
  }
  return type;
}

GType gtkdoc_enum2_get_type (void) {
  static GType type = 0;
  if(type==0) {
    static const GEnumValue values[] = {
      { GTKDOC_ENUM2_V1,          "GTKDOC_ENUM2_V1",          "first" },
      { GTKDOC_ENUM2_V2,          "GTKDOC_ENUM2_V2",          "second" },
      { 0, NULL, NULL},
    };
    type = g_enum_register_static ("GtkdocEnum2", values);
  }
  return type;
}

/* boxed: class internals */

static gpointer gtkdoc_boxed_copy (gpointer boxed) {
  return boxed;
}

static void gtkdoc_boxed_free (gpointer boxed) {
}

GType gtkdoc_boxed_get_type (void) {
  static GType type = 0;
  if (type == 0) {
    type = g_boxed_type_register_static("GtkdocBoxed",
        (GBoxedCopyFunc) gtkdoc_boxed_copy, (GBoxedFreeFunc) gtkdoc_boxed_free);
  }
  return type;
}

/* boxed plain old data: class internals */

static gpointer gtkdoc_boxed_plain_old_data_copy (gpointer boxed) {
  return g_memdup2(boxed, sizeof(GtkdocBoxedPlainOldData));
}

static void gtkdoc_boxed_plain_old_data_free (gpointer boxed) {
  g_free(boxed);
}

GType gtkdoc_boxed_plain_old_data_get_type (void) {
  static GType type = 0;
  if (type == 0) {
    type = g_boxed_type_register_static("GtkdocBoxedPlainOldData",
                                        (GBoxedCopyFunc) gtkdoc_boxed_plain_old_data_copy,
                                        (GBoxedFreeFunc) gtkdoc_boxed_plain_old_data_free);
  }
  return type;
}
