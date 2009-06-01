#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>
#include <glib-object.h>

extern void annotation_array_length (GObject *list, gint n_columns, GType *types);

extern gchar * annotation_nullable (const gchar *uri, const gchar *label);

extern gboolean annotation_elementtype (const GList *list);

extern gboolean annotation_outparams (GList **list);

#endif // GTKDOC_TESTER_H

