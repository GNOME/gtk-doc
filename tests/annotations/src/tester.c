/**
 * SECTION:tester
 * @short_description: module for gtk-doc unit test
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 */

#include <glib.h>
#include <glib-object.h>

#include "tester.h"

/**
 * annotation_array_length:
 * @list: a #GtkListStore
 * @n_columns: number of columns
 * @types: (array length=n_columns): list of types
 *
 * Document parameter relation for array length.
 */
void
annotation_array_length (GObject *list,
                         gint          n_columns,
                         GType        *types)
{
}


/**
 * annotation_nullable:
 * @uri: a uri
 * @label: (allow-none): an optional string, which is used in ways too
 *  complicated to describe in a single line, making it necessary to wrap it
 *
 * Document optional parameters.
 *
 * Returns: (transfer full) (allow-none): Returns stuff which you have to
 *  free after use, whose description is also rather long
 */
gchar *
annotation_nullable (const gchar *uri,
                     const gchar *label)
{
   return NULL;
}

/**
 * annotation_elementtype:
 * @list: (element-type GObject): list of #GObject instances to search
 *
 * Document optional parameters.
 *
 * Returns: %TRUE for success
 */
gboolean
annotation_elementtype (const GList *list)
{
   return TRUE;
}

/**
 * annotation_elementtype_transfer:
 * @list: (element-type utf8) (transfer full): list of #GObject instances to search
 *
 * Document optional parameters.
 *
 * Returns: %TRUE for success
 */
gboolean
annotation_elementtype_transfer (const GList *list)
{
   return TRUE;
}

/**
 * annotation_elementtype_returns:
 *
 * Document optional parameters.
 *
 * Returns: (element-type GObject): A list of #GObject instances.
 */
GList *
annotation_elementtype_returns (void)
{
   return NULL;
}

/**
 * annotation_outparams:
 * @list: (out) (transfer none): a pointer to take a list
 *
 * Document optional parameters.
 *
 * Returns: %TRUE for success
 */
gboolean
annotation_outparams (GList **list)
{
   return TRUE;
}

/**
 * annotation_skip: (skip)
 * @list: a pointer to take a list
 *
 * Documentation for this function.
 */
void
annotation_skip (GList *list)
{
}

/**
 * annotation_scope:
 * @callback: (scope async): a callback
 * @user_data: data to pass to callback
 *
 * Documentation for this function.
 */
void
annotation_scope (GCallback *callback, gpointer user_data)
{
}
