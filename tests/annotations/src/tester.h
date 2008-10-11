#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>
#include <glib-object.h>

extern void annotation_array_length (GObject *list, gint n_columns, GType *types);

extern void annotation_nullable (const gchar *uri, const gchar *label);

#endif // GTKDOC_TESTER_H

