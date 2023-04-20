if HAVE_YELP_TOOLS
@YELP_HELP_RULES@
endif

HELP_ID = gtk-doc-manual

HELP_FILES = \
    index.docbook \
    fdl-appendix.xml

HELP_LINGUAS = bn_IN cs de el en_GB es eu fr gl gu hu pt_BR sl sv ta te zh_CN

CLEANFILES = $(_HELP_LC_FILES) $(_HELP_LC_STAMPS) $(_HELP_MOFILES)

GITIGNOREFILES = ??_??/$(HELP_ID).xml ??/$(HELP_ID).xml

EXTRA_DIST = meson.build

-include $(top_srcdir)/git.mk
