#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>
#include <glib-object.h>

/**
 * GtkdocAnnotation:
 * @that: (allow-none): eventualy points to something
 *
 * small struct
 */
struct _GtkdocAnnotation {
  gpointer that;
};

void annotation_array_length (GObject *list, gint n_columns, GType *types);

gchar * annotation_nullable (const gchar *uri, const gchar *label);

gboolean annotation_elementtype (const GList *list);
gboolean annotation_elementtype_transfer (const GList *list);
GList *annotation_elementtype_returns (void);

gboolean annotation_outparams (GList **list);

void annotation_skip (GList *list);
gboolean annotation_skip_return (GList *list);

void annotation_scope (GCallback *callback, gpointer user_data);

void annotation_rename_to (void);

void stability_unstable(void);

#endif // GTKDOC_TESTER_H

