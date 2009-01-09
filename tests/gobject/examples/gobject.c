/* example for gobject usage */

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
