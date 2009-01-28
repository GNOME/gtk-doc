/* example for gobject usage
 * checkout the article at http://en.wikipedia.org/wiki/GObject
 *
 * This example is part of the release, that can be downloaded
 * from ftp://ftp.gnome.org/pub/gnome/sources/gtk-doc/ or any mirror.
 */

#include <glib.h>
#include <glib-object.h>

gint
main(gint argc, gchar **argv)
{
  GObject *myobj;

  myobj = gtkdoc_object_new();
  g_object_set (myobj, "parameter", 5, NULL);
  g_object_unref (myobj);
  
  return 0;
}
