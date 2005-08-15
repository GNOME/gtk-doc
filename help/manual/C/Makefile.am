figdir = 
docname = gtk-doc-manual
lang = C
omffile = gtk-doc-manual-C.omf
entities = fdl-appendix.xml

if ENABLE_SCROLLKEEPER
include $(top_srcdir)/xmldocs.make
dist-hook: app-dist-hook
else
# here we should
# a) invoke xslproc, if available
# stylesheet=/opt/gnome/share/sgml/docbook/yelp/docbook/html/docbook.xsl
# xsltproc --nonet $(stylesheet) $(docname).xml
# b) simple install pregenerated html (pdf)
endif

