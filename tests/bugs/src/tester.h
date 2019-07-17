#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>


/**
 * bug_501038:
 * @a: value
 * @b: deprecated value
 * @_b: scrambled deprecated value
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=501038
 */
struct _bug_501038 {
  gint a;
#ifndef GTK_DISABLE_DEPRECATED
  gint b;
#else
  gint _b;
#endif
};


#define _PADDDING 4
/**
 * bug_460127:
 * @a: field
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=460127
 */
struct _bug_460127 {
  /*< public >*/
  gint a;

  /*< private >*/
  union {
    struct {
      gint b;
    } ABI;
    gpointer _reserved[_PADDDING + 0];
  } abidata;
};


/**
 * bug_477532:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=477532
 */
GLIB_VAR guint64 (*bug_477532) (void);

int bug_380824 (int arg);

void bug_419997 (int const_values);

void bug_445693 (unsigned long pid);

G_CONST_RETURN gchar* G_CONST_RETURN *
bug_471014 (void);

/**
 * Bug446648:
 * @BUG_446648_FOO: foo
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=446648
 */
typedef enum _Bug446648 Bug446648;
enum _Bug446648 {
    BUG_446648_FOO
};

/**
 * Bug512154:
 * @index: field
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=512154
 */
typedef struct {
  unsigned long index;
} Bug512154;


/**
 * bug_512155a_function_pointer_t:
 * @arg1: param 1
 * @arg2: param 1
 * @arg3: param 1
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=512155
 */
typedef int
(*bug_512155a_function_pointer_t) (unsigned int arg1, unsigned int arg2,
                                  unsigned int arg3);

/**
 * bug_512155b_function_pointer_t:
 * @arg1: param 1
 * @arg2: param 1
 * @arg3: param 1
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=512155
 */
typedef
int (*bug_512155b_function_pointer_t) (unsigned int arg1, unsigned int arg2,
                                       unsigned int arg3);

/**
 * bug_512155c_function_pointer_t:
 * @arg1: param 1
 * @arg2: param 1
 * @arg3: param 1
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=512155
 */
typedef int (*bug_512155c_function_pointer_t) (unsigned int arg1,
                                               unsigned int arg2,
                                               unsigned int arg3);


/**
 * BUG_530758:
 *
 * <![CDATA[http://bugzilla.gnome.org/show_bug.cgi?id=530758#c1]]>
 *
 * <ulink url="http://bugzilla.gnome.org/show_bug.cgi?id=530758#c1">Test</ulink>
 */
#define BUG_530758 "dummy"


/**
 * bug_554833:
 * @i: value;
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=554833
 */
struct _bug_554833 {
  int i;
};


/**
 * bug_554833_new:
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=554833
 *
 * Returns: result
 */
struct _bug_554833 *
                bug_554833_new (void);


#define GTKDOC_GNUC_CONST
int bug_574654a(void) GTKDOC_GNUC_CONST;
void bug_574654b(double offset);


void bug_580300a_get_type(void);
void bug_580300b_get_type(gint a);
void bug_580300c_get_type();
extern int bug_580300d_get_type();

void bug_597937(void (*function_arg)(int arg1, char arg2, void *));

long int bug_602518a(void);
unsigned long int bug_602518b(void);
unsigned int bug_602518c(void);

/**
 * Bug165425a:
 * @i: data as int
 * @f: data as float
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=165425
 */
union _Bug165425a {
  int i;
  float f;
};
typedef union _Bug165425a Bug165425a;

/**
 * Bug165425b:
 * @i: data as int
 * @f: data as float
 *
 * http://bugzilla.gnome.org/show_bug.cgi?id=165425
 */
typedef union _Bug165425b {
  int i;
  float f;
} Bug165425b;


/*
 * BugXXX1b:
 * @a: field
 *
 * No bug report
 *
typedef struct _BugXXX1b BugXXX1b;
struct _BugXXX1b {
  *//*< protected >*//*
  gint a;

  *//*< private >*//*
  gint b;
};
*/

long double bug_607445(long double **a, int n);


signed long bug_610257(const unsigned char *der, int *len);


void bug_623968a(void);
void bug_623968b(void);
void bug_623968c(void);


#define _BUG_624199(struct_type, n_structs, func) \
  (struct_type *) (__extension__ ({			\
    gsize __n = (gsize) (n_structs);			\
    gsize __s = sizeof (struct_type);			\
    gpointer __p;					\
    if (__s == 1)					\
      __p = g_##func (__n);				\
    else if (__builtin_constant_p (__n) &&			\
             (__s == 0 || __n <= G_MAXSIZE / __s))		\
      __p = g_##func (__n * __s);				\
    else							\
      __p = g_##func##_n (__n, __s);			\
    __p;							\
  }))


const char * const * bug_624200a(void);
const char ** const bug_624200b(void);


/* internal function */
gchar *_bug_000000a (const gchar *name);

void (*bug_638330) (void *arg1,
     const unsigned char *data,
     unsigned int length);


/**
 * Bug644291:
 * @BUG_644291_START: foo
 * @BUG_644291_TEXT: bar
 * @BUG_644291_END: milk
 * @BUG_644291_ATTRIBUTE: comes
 * @BUG_644291_XMLNS: from
 * @BUG_644291_ASSIGN_TO: cows
 *
 * https://bugzilla.gnome.org/show_bug.cgi?id=644291
 */
typedef enum
{
  BUG_644291_START = '(',
  BUG_644291_TEXT = '$',
  BUG_644291_END = ')',
  BUG_644291_ATTRIBUTE = '@',
  BUG_644291_XMLNS = ':',
  BUG_644291_ASSIGN_TO = '*'
} Bug644291;

/* varargs */

extern void bug_000000_va1 (gchar name, ...);

/**
 * BUG_000000_VA2:
 * @name: a name
 * @...: A printf-style message to output
 *
 * Outputs a message.
 */
#define BUG_000000_VA2(name,...)

/**
 * BUG_000000_VA3:
 * @name: a name
 * @...: A printf-style message to output
 *
 * Outputs a message.
 */
#define BUG_000000_VA3(name,args...)

/**
 * Bug000000Scope:
 *
 * Opaque structure.
 * "warning: Field descriptions for Bug000000Scope are missing in source code comment block."
 * but not if we remove the blank line before "int b";
 */
typedef struct _Bug000000Scope Bug000000Scope;
struct _Bug000000Scope {
  /*< private >*/
  union {
    struct {
      /* comment */
      int a;
    } ABI;
    gpointer _reserved[4 - 1];
  } abidata;

  int b;
};

/**
 * gst_play_marshal_BUFFER__BOXED:
 * @closure: test
 * @return_value: test
 * @marshal_data: test
 *
 * test.
 */
void
gst_play_marshal_BUFFER__BOXED (gint * closure,
    gint * return_value G_GNUC_UNUSED,
    gpointer marshal_data);


#ifndef G_GNUC_DEPRECATED
#define G_GNUC_DEPRECATED
#endif
#ifndef G_GNUC_DEPRECATED_FOR
#define G_GNUC_DEPRECATED_FOR(a)
#endif

void bug_624001a(void) G_GNUC_DEPRECATED;
void bug_624001b(void) G_GNUC_DEPRECATED_FOR(bug_624001a);

G_GNUC_DEPRECATED
void bug_624001c(void);

G_GNUC_DEPRECATED_FOR(bug_624001c)
void bug_624001d(void);

#ifndef GLIB_DEPRECATED
#define GLIB_DEPRECATED
#endif

GLIB_DEPRECATED
void bug_624001e (void);

#define BUG_711598_DEPRECATED_FOR(f) G_GNUC_DEPRECATED_FOR(f)
BUG_711598_DEPRECATED_FOR(bug_711598b)
void bug_711598(void);

#ifdef GTKDOC_TESTER_DISABLE_DEPRECATED
void deprecation_notice(void);
#endif

#ifndef G_GNUC_NONNULL
#define G_GNUC_NONNULL(a)
#endif
void bug_741941(void *object, void *par) G_GNUC_NONNULL(1) G_GNUC_NONNULL(2);

void bug_732689 (const gchar *spec);
void bug_749142 (void);

void bug_783420 (int in, int *out);

/**
 * MACRO_VALUE:
 *
 * This should be listed in the types and values section.
 */
#define MACRO_VALUE (1 << 1)

/**
 * MACRO_FUNCTION:
 * @x: a value
 *
 * This should be listed in the functions section.
 */
#define MACRO_FUNCTION(x) (x << 1)

/**
 * _:
 * @str: a string
 *
 * https://bugzilla.gnome.org/show_bug.cgi?id=753052
 */
#define _(str) str

/**
 * BUG_791928:
 *
 * https://bugzilla.gnome.org/show_bug.cgi?id=791928
 *
 * Stability: UndefinedTestValue
 */
#define BUG_791928   1

/**
 * Bug76:
 * @arg: The type of the option, as a #GOptionArg
 * @arg_data: If the @arg type is %G_OPTION_ARG_CALLBACK, then @arg_data
 *     must point to a #GOptionArgFunc callback function, which will be
 *     called to handle the extra argument. Otherwise, @arg_data is a
 *     pointer to a location to store the value, the required type of
 *     the location depends on the @arg type:
 *     - %G_OPTION_ARG_NONE: %gboolean
 *     - %G_OPTION_ARG_STRING: %gchar*
 *     - %G_OPTION_ARG_INT: %gint
 *     - %G_OPTION_ARG_FILENAME: %gchar*
 *     - %G_OPTION_ARG_STRING_ARRAY: %gchar**
 *     - %G_OPTION_ARG_FILENAME_ARRAY: %gchar**
 *     - %G_OPTION_ARG_DOUBLE: %gdouble
 *     If @arg type is %G_OPTION_ARG_STRING or %G_OPTION_ARG_FILENAME,
 *     the location will contain a newly allocated string if the option
 *     was given. That string needs to be freed by the callee using g_free().
 *     Likewise if @arg type is %G_OPTION_ARG_STRING_ARRAY or
 *     %G_OPTION_ARG_FILENAME_ARRAY, the data should be freed using g_strfreev().
 * @description: the description for the option in `--help`
 *     output. The @description is translated using the @translate_func
 *     of the group, see g_option_group_set_translation_domain().
 *
 * https://gitlab.gnome.org/GNOME/gtk-doc/issues/76
 */
struct _Bug76
{
  int    arg;
  void * arg_data;
  char * description;
};
typedef struct _Bug76   Bug76;

#define MY_DEPRECATED_FOR(val)

/**
 * MyNotDeprecatedEnum:
 * @MY_NOT_DEPRECATED_ENUM_VAL1: new value
 *
 * some description
 */
typedef enum {
  MY_NOT_DEPRECATED_ENUM_VAL1,
} MyNotDeprecatedEnum;

/**
 * MyDeprecatedEnum:
 * @MY_DEPRECATED_ENUM_VAL1: deprecated, use instead %MY_DEPRECATED_ENUM_VAL2
 * @MY_DEPRECATED_ENUM_VAL2: val2
 *
 * some description
 * Deprecated: Use #MyNotDeprecatedEnum instead
 */
typedef enum {
  MY_DEPRECATED_ENUM_VAL1 MY_DEPRECATED_FOR(MY_DEPRECATED_ENUM_VAL2),
  MY_DEPRECATED_ENUM_VAL2,
} MyDeprecatedEnum MY_DEPRECATED_FOR(MyNotDeprecatedEnum);

/**
 * MyDeprecatedStruct:
 *
 * some description
 * Deprecated: Use #MyNotDeprecatedStruct instead
 */
typedef struct _MyDeprecatedStruct  MyDeprecatedStruct MY_DEPRECATED_FOR(MyNotDeprecatedStruct);
struct _MyDeprecatedStruct {
  /*< private >*/
  guint index;
} MY_DEPRECATED_FOR(MyNotDeprecatedStruct);

/**
 * MyNotDeprecatedStruct:
 *
 * some description
 */
typedef struct {
  /*< private >*/
  guint index_plop;
} MyNotDeprecatedStruct;

/**
 * inline_func_with_macro:
 * @obj: arg
 *
 * GLib has a few inline functions with a macro that has the same name. It puts
 * the inline function name into parenthesis to avoid macro expansion.
 * See g_set_object().
 */
static inline gboolean
(inline_func_with_macro) (void *obj)
{
  return TRUE;
}

#define inline_func_with_macro(obj)

#endif // GTKDOC_TESTER_H
