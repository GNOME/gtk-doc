# Makefile
# just to document how to build the manual
# (just type `make`, and see what happens)
#

all: html pdf

# HTML
html: gtk-doc-manual.html

gtk-doc-manual.html: gtk-doc-manual.xml fdl-appendix.xml
	xmlto html-nochunks gtk-doc-manual.xml


# PDF is not (yet?) supported
pdf: gtk-doc-manual.pdf

gtk-doc-manual.pdf: gtk-doc-manual.xml fdl-appendix.xml
	touch gtk-doc-manual.pdf


clean:
	rm -f *.html *.pdf
