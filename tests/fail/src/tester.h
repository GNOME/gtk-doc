#ifndef GTKDOC_TESTER_H
#define GTKDOC_TESTER_H

#include <glib.h>

/**
 * MACRO_NO_ITEM_DOCS:
 *
 * Here we document the macro but not the parameters.
 */
#define MACRO_NO_ITEM_DOCS(a,b) (a+b)

/**
 * MACRO_INCOMPLETE_DOCS:
 * @a: a value
 *
 * Here we document the macro but not all the parameters.
 */
#define MACRO_INCOMPLETE_DOCS(a,b) (a+b)

/**
 * MACRO_UNUSED_DOCS:
 * @a: a value
 * @b: a value
 * @c: an unexisting value
 *
 * Here we document the macro and more than the actual parameters.
 */
#define MACRO_UNUSED_DOCS(a,b) (a+b)


/**
 * EnumNoItemDocs:
 *
 * Here we document the enum but not the values.
 * http://bugzilla.gnome.org/show_bug.cgi?id=568711
 */
typedef enum {
    ENUM_NO_ITEM_DOCS_1,
    ENUM_NO_ITEM_DOCS_2
} EnumNoItemDocs;

/**
 * EnumIncompleteDocs:
 * @ENUM_INCOMPLETE_DOCS_1: a value
 *
 * Here we document the enum but not all the values.
 */
typedef enum {
    ENUM_INCOMPLETE_DOCS_1,
    ENUM_INCOMPLETE_DOCS_2
} EnumIncompleteDocs;

/**
 * EnumUnusedDocs:
 * @ENUM_UNUSED_DOCS_1: a value
 * @ENUM_UNUSED_DOCS_2: a value
 * @ENUM_UNUSED_DOCS_3: an unexisting value
 *
 * Here we document the enum and more than the actual values.
 */
typedef enum {
    ENUM_UNUSED_DOCS_1,
    ENUM_UNUSED_DOCS_2
} EnumUnusedDocs;


/**
 * StructNoItemDocs:
 *
 * Here we document the struct but not the values.
 */
typedef struct {
    int a;
    char b;
} StructNoItemDocs;

/**
 * StructIncompleteDocs:
 * @a: a value
 *
 * Here we document the struct but not all the values.
 */
typedef struct {
    int a;
    char b;
} StructIncompleteDocs;

/**
 * StructUnusedDocs:
 * @a: a value
 * @b: a value
 * @c: an unexisting value
 *
 * Here we document the struct and more than the actual values.
 */
typedef struct {
    int a;
    char b;
} StructUnusedDocs;


void func_no_docs(void);
void func_no_item_docs(int a, char b);
void func_incomplete_docs(int a, char b);
void func_unused_docs(int a, char b);

#endif // GTKDOC_TESTER_H

