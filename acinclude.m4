
AC_DEFUN([_JH_CHECK_XML_CATALOG_PREP],
[
  # check for the presence of the XML catalog
  AC_ARG_WITH([xml-catalog],
              AC_HELP_STRING([--with-xml-catalog=CATALOG],
                             [path to xml catalog to use]),,
              [with_xml_catalog=/etc/xml/catalog])
  XML_CATALOG_FILE="$with_xml_catalog"
  AC_MSG_CHECKING([for XML catalog ($XML_CATALOG_FILE)])
  if test -f "$XML_CATALOG_FILE"; then
    AC_MSG_RESULT([found])
  else
    AC_MSG_ERROR([XML catalog not found])
  fi

  # check for the xmlcatalog program
  AC_PATH_PROG(XMLCATALOG, xmlcatalog, no)
  if test "x$XMLCATALOG" = xno; then
    AC_MSG_ERROR([could not find xmlcatalog program])
  fi
])

# Checks if a particular URI appears in the XML catalog
# Usage:
#   JH_CHECK_XML_CATALOG(URI)
AC_DEFUN([JH_CHECK_XML_CATALOG],
[
  AC_REQUIRE([_JH_CHECK_XML_CATALOG_PREP])dnl
  AC_MSG_CHECKING([for $1 in XML catalog])
  if $XMLCATALOG --noout "$XML_CATALOG_FILE" "$1" >/dev/null 2>&1; then
    AC_MSG_RESULT([found])
  else
    AC_MSG_ERROR([not found])
  fi
])
