Introduction
============

This chapter introduces GTK-Doc and gives an overview of what it is and how it
is used.

What is GTK-Doc?
----------------

GTK-Doc is used to document C code. It is typically used to document the public
API of libraries, such as the GTK+ and GNOME libraries. But it can also be used
to document application code.

How Does GTK-Doc Work?
----------------------

GTK-Doc works by using documentation of functions placed inside the source files
in specially-formatted comment blocks, or documentation added to the template
files which GTK-Doc uses (though note that GTK-Doc will only document functions
that are declared in header files; it won't produce output for static
functions).

GTK-Doc consists of a number of python scripts, each performing a different step
in the process.

There are 5 main steps in the process.

### Step 1: writing the documentation

The author fills in the source files with the documentation for each function,
macro, structs or unions, etc.

### Step 2: gathering information about the code

`gtkdoc-scan` scans the header files of the code looking for declarations of
functions, macros, enums, structs, and unions.
It creates the file `<module>-decl-list.txt` containing a list of the
declarations, placing them into sections according to which header file they are
in.
On the first run this file is copied to `<module>-sections.txt`.
The author can rearrange the sections, and the order of the declarations within
them, to produce the final desired order.
The second file it generates is `<module>-decl.txt`.
This file contains the full declarations found by the scanner.
If for some reason one would like some symbols to show up in the docs, where the
full declaration cannot be found by the scanner or the declaration should appear
differently, one can place entities similar to the ones in `<module>-decl.txt`
into `<module>-overrides.txt`.

`gtkdoc-scangobj` can also be used to dynamically query a library about any
GObject subclasses it exports. It saves information about each object's position
in the class hierarchy and about any GObject properties and signals it provides.

`gtkdoc-scanobj` should not be used anymore. It was needed in the past when
GObject was still GtkObject inside gtk+.

### Step 3: generating the XML and HTML/PDF

`gtkdoc-mkdb` turns the template files into XML files in the `xml/`
subdirectory.
If the source code contains documentation on functions, using the special
comment blocks, it gets merged in here. If there are no tmpl files used it only
reads docs from sources and introspection data.

`gtkdoc-mkhtml` turns the XML files into HTML files in the `html/` subdirectory.
Likewise `gtkdoc-mkpdf` turns the XML files into a PDF document called
`<package>.pdf`.

Files in `xml/` and `html/` directories are always overwritten. One should never
edit them directly.

### Step 4: fixing up cross-references between documents

After installing the HTML files, `gtkdoc-fixxref` can be run to fix up any
cross-references between separate documents. For example, the GTK+ documentation
contains many cross-references to types documented in the GLib manual.

When creating the source tarball for distribution, `gtkdoc-rebase` turns all
external links into web-links. When installing distributed (pregenerated) docs
the same application will try to turn links back to local links (where those
docs are installed).
