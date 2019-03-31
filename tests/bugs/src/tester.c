/**
 * SECTION:tester
 * @short_description: module for gtk-doc unit test
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 *
 * As described in http://bugzilla.gnome.org/show_bug.cgi?id=457077 it
 * returns nothing.
 *
 * Some special characters need escaping. The tests should pass 100\%.
 * Try a <ulink url="http://www.gtk.org/gtk-doc/#Top">link containing a # char</ulink>.
 *
 * <refsect2 id="dummy-id">
 * <title>more details</title>
 * <para>
 * Second paragraph inside subsection.
 * </para>
 * </refsect2>
 */

#include "tester.h"

/**
 * bug_380824:
 * @arg: arg
 *
 * Returns a value.
 * http://bugzilla.gnome.org/show_bug.cgi?id=380824
 *
 * Since: 0.1
 *
 * Returns: result
 */
int bug_380824 (int arg) {
  return 0;
}


/**
 * bug_419997:
 * @const_values: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=419997
 */
void bug_419997 (int const_values) {
}


/**
 * bug_445693:
 * @pid: arg
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=445693
 */
void bug_445693 (unsigned long pid) {
}


/**
 * bug_471014:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=471014
 *
 * Returns: result
 */
G_CONST_RETURN gchar* G_CONST_RETURN * bug_471014 (void) {
  return NULL;
}

/**
 * bug_574654a:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=574654
 *
 * Returns: result
 */
/**
 * bug_574654b:
 * @offset: skip this many items
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=574654
 */
int bug_574654a(void) {
  return 0;
}

void bug_574654b(double offset) { }


/**
 * bug_580300a_get_type:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 */
void bug_580300a_get_type(void) { }

/**
 * bug_580300b_get_type:
 * @a: value
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 */
void bug_580300b_get_type(gint a) { }

/**
 * bug_580300c_get_type:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 */
void bug_580300c_get_type() { }

/**
 * bug_580300d_get_type:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=580300
 *
 * Returns: result
 */
int bug_580300d_get_type() { return 0; }

/**
 * bug_597937:
 * @function_arg: value
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=597937
 */
void bug_597937(void (*function_arg)(int arg1, char arg2, void *)) { }

/**
 * bug_602518a:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=602518
 *
 * Returns: result
 */
long int bug_602518a(void) {
  return (long int)0;
}

/**
 * bug_602518b:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=602518
 *
 * Returns: result
 */
unsigned long int bug_602518b(void) {
  return (unsigned long int)0;
}

/**
 * bug_602518c:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=602518
 *
 * Returns: result
 */
unsigned int bug_602518c(void) {
  return (unsigned int)0;
}

/**
 * bug_607445:
 * @a: parameter
 * @n: parameter
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=607445
 */
long double bug_607445(long double **a, int n) {
  return 2.0*n;
}

/**
 * bug_610257:
 * @der: parameter
 * @len: parameter
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=610257
 */
signed long
bug_610257(const unsigned char *der, int *len)
{
  return 1L;
}


/**
 * bug_623968a:
 *
 * <para>test</para>
 * <refsect3>
 *   <title>subsect</title>
 *   <para>test</para>
 * </refsect3>
 **/
void
bug_623968a(void)
{
}

/**
 * bug_623968b:
 *
 * test
 *
 * <refsect3>
 *   <title>subsect</title>
 *   <para>test</para>
 * </refsect3>
 **/
void
bug_623968b(void)
{
}

/**
 * bug_623968c:
 *
 * <para>test</para>
 **/
void
bug_623968c(void)
{
}


/**
 * bug_624200a:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624200
 *
 * Returns: result
 */
const char * const *
bug_624200a(void)
{
  return NULL;
}

/**
 * bug_624200b:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624200
 *
 * Returns: result
 */
const char ** const
bug_624200b(void)
{
  return NULL;
}

/**
 * bug_638330:
 * @arg1: arg1
 * @data: data
 * @length: length
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=638330
 */
void (*bug_638330) (void *arg1,
     const unsigned char *data,
     unsigned int length) = NULL;


/* internal function */
gchar *
_bug_000000a (const gchar *name)
{
  return NULL;
}

/* varargs */

/**
 * bug_000000_va1:
 * @name: a name
 * @...: A printf-style message to output
 *
 * Outputs a message.
 */
void bug_000000_va1 (gchar name, ...)
{
}


/**
 * bug_624001a:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624001
 *
 * Deprecated: Use main() instead.
 */
void bug_624001a(void)
{
}

/**
 * bug_624001b:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624001
 *
 * Deprecated: Use main() instead.
 */
void bug_624001b(void)
{
}

/**
 * bug_624001c:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624001
 *
 * Deprecated: Use main() instead.
 */
void bug_624001c(void)
{
}

/**
 * bug_624001d:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624001
 *
 * Deprecated: Use main() instead.
 */
void bug_624001d(void)
{
}

/**
 * bug_624001e:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=624001
 *
 * Deprecated: Use main() instead.
 */
void bug_624001e(void)
{
}

/**
 * bug_711598:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=711598
 */
void bug_711598(void)
{
}

/**
 * deprecation_notice:
 *
 * Foo.
 *
 * Deprecated: 3.10: Use named icon "bar" instead.
 */
void deprecation_notice(void)
{
}

/**
 * bug_741941:
 * @object: the object
 * @par: parameter
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=741941
 */
void bug_741941(void *object, void *par)
{
}

/**
 * bug_732689:
 * @spec: the string specifying the color.
 *
 * Parses a textual specification of a color and fill in the
 * <structfield>red</structfield>, <structfield>green</structfield>,
 * and <structfield>blue</structfield> fields of a color.
 **/
void
bug_732689 (const gchar *spec)
{
}

/**
 * bug_749142:
 *
 * The message's structure contains one field:
 * <itemizedlist>
 * <listitem><para>int timeout: the timeout.</para></listitem>
 * </itemizedlist>
 *
 * <refsect3>
 * <title>Example usage</title>
 * |[
 * echo "Hello" | foo
 * ]|
 * </refsect3>
 **/
void
bug_749142 (void)
{
}

/**
 * bug_783420:
 * @in: input
 * @out: output
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=783420
 *
 * |[
 * #include <tester.h>
 *
 * int res;
 * bug_783420(42, &res);
 * ]|
 *
 * <refsect2 id="subsect">
 * <title>Subsection</title>
 * <para>
 * Lorem ipsum ...
 * |[
 * #include <tester.h>
 *
 * int res;
 * bug_783420(42, &res);
 * ]|
 * </para>
 * </refsect2>
 */
void
bug_783420 (int in, int *out)
{
}
