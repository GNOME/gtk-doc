/*
 * SECTION:tester_nodocs
 * @short_description: module for gtk-doc unit test
 * @title: GtkdocTesterNoDocs
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 */
/**
 * SECTION:tester_nolongdesc
 * @short_description: module for gtk-doc unit test
 * @title: GtkdocTesterNoLongDesc
 */
/**
 * SECTION:tester_noshortdesc
 * @title: GtkdocTesterNoShortDesc
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 */
/**
 * SECTION:tester_brokendocs
 * @short_description: module for gtk-doc unit test
 * @title: GtkdocTesterBrokenDocs
 *
 * This file contains non-sense code for the sole purpose of testing the docs.
 */

#include "tester.h"

/**
 * func_no_docs:
 */
void
func_no_docs(void)
{
}

/**
 * func_no_item_docs:
 *
 * Here we document the function but not the parameters.
 */
void
func_no_item_docs(int a, char b)
{
}

/**
 * func_incomplete_docs:
 * @a: a value
 *
 * Here we document the function but not all the parameters.
 */
void
func_incomplete_docs(int a, char b)
{
}

/**
 * func_unused_docs:
 * @a: a value
 * @b: a value
 * @c: an unexisting value
 *
 * Here we document the function and more than the actual parameters.
 */
void
func_unused_docs(int a, char b)
{
}

