if HAVE_GNOME_DOC_UTILS
include $(top_srcdir)/gnome-doc-utils.make
dist-hook: doc-dist-hook
else
dist-hook:
	@echo "*** gnome-doc-utils must be installed and enabled in order to make dist"
	@false
endif

DOC_MODULE = gtk-doc-manual
DOC_ENTITIES = fdl-appendix.xml
DOC_INCLUDES =
DOC_FIGURES =
DOC_LINGUAS = bn_IN de el en_GB es fr gu sl sv ta te

-include $(top_srcdir)/git.mk
