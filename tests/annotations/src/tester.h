#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>
#include <glib-object.h>

/**
 * GtkdocAnnotation:
 * @that: (allow-none): eventually points to something
 *
 * small struct
 */
struct _GtkdocAnnotation {
  gpointer that;
};

void annotation_array_length (GObject *list, gint n_columns, GType *types);

gchar * annotation_allow_none (const gchar *uri, const gchar *label);
gchar * annotation_nullable (const gchar *uri, const gchar *label);
gchar * annotation_not_nullable (const gchar *uri, const gchar *label);

gboolean annotation_elementtype (const GList *list);
gboolean annotation_elementtype_transfer (const GList *list);
GList *annotation_elementtype_returns (void);

gboolean annotation_outparams (GList **list);
gboolean annotation_outparams_optional (GList **list);
gboolean annotation_outparams_not_optional (GList **list);
gboolean annotation_outparams_nullable (GList **list);
gboolean annotation_outparams_not_nullable (GList **list);
gboolean annotation_outparams_optional_nullable (GList **list);
gboolean annotation_outparams_not_optional_nullable (GList **list);
gboolean annotation_outparams_optional_not_nullable (GList **list);
gboolean annotation_outparams_not_optional_not_nullable (GList **list);

void annotation_skip (GList *list);
gboolean annotation_skip_return (GList *list);

void annotation_scope (GCallback *callback, gpointer user_data);

void annotation_rename_to (void);

void annotation_attributes_single (void);
void annotation_attributes_single_eq (void);

void stability_unstable(void);

void annotation_multiline_on_function (void);
void annotation_multiline_on_function2 (void);

#endif // GTKDOC_TESTER_H

