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

extern void annotation_array_length (GObject *list, gint n_columns, GType *types);

extern gchar * annotation_nullable (const gchar *uri, const gchar *label);

extern gboolean annotation_elementtype (const GList *list);
extern gboolean annotation_elementtype_transfer (const GList *list);
extern GList *annotation_elementtype_returns (void);

extern gboolean annotation_outparams (GList **list);

extern void annotation_skip (GList *list);

extern void annotation_scope (GCallback *callback, gpointer user_data);

#endif // GTKDOC_TESTER_H

