GTK-Doc - Documentation generator for C code
============================================

Introduction
------------

GTK-Doc is used to document C code. It is typically used to document the public
API of libraries, such as GLib-based libraries, but it can also be used to
document application code.

Note that GTK-Doc wasn't originally intended to be a general-purpose
documentation tool, so it can be a bit awkward to setup and use. For a more
general-purpose documentation tool you may want to look at
[Doxygen](https://www.doxygen.nl/). However GTK-Doc has some special code to
document the signals and properties of GTK widgets and GObject classes which
other tools may not have.

From your source code comments GTK-Doc generates a DocBook XML document, which
is then transformed into HTML and/or PDF.

The generated HTML documentation can be browsed in an ordinary web browser or
by using the special
[Devhelp API browser](https://github.com/gdev-technology/devhelp).

Important message about the docbook-style-xsl dependency
--------------------------------------------------------

To generate the `api-index-*.html` files, you need to use docbook-style-xsl
version 1.79.1, not the latest version.

See:
- https://sourceforge.net/p/docbook/bugs/1401/
- https://gitlab.gnome.org/GNOME/gtk-doc/-/issues/36

Documentation
-------------

See the `help/manual/` directory. You can read the manual with
[Yelp](https://apps.gnome.org/Yelp/):

```
$ yelp help/manual/C/index.docbook
```

Requirements
------------

[Python 3](https://www.python.org/) with these additional modules:
- For the tests: unittest, parameterized
- For mkhtml2 (experimental): anytree, lxml and pygments
- For fixxref: pygments

For XML output (recommended):
- The [DocBook](https://www.oasis-open.org/docbook/) XML DTD.
- The [DocBook XSL Stylesheets](http://docbook.sourceforge.net/projects/xsl/).
- [libxml2 and libxslt](https://gitlab.gnome.org/GNOME/libxml2).

For PDF output:
- The [dblatex](https://dblatex.sourceforge.net/) tool.

Building
--------

The [Meson](https://mesonbuild.com/) build system is used.
