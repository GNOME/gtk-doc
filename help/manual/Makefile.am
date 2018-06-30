NULL =

if HAVE_YELP_TOOLS
@YELP_HELP_RULES@
endif

$(srcdir)/C/version.ent: $(srcdir)/version.ent.in Makefile
	echo "To: $@"
	echo "From: $<"
	$(AM_V_GEN)sed \
               -e "s|\@VERSION\@|$(PACKAGE_VERSION)|" \
               $< > $@

HELP_ID = gtk-doc-manual

HELP_FILES = \
    index.docbook \
    fdl-appendix.xml

C/html/index.html: Makefile
	$(AM_V_GEN)xsltproc --nonet \
             --xinclude \
             --output $(srcdir)/C/html/ \
             --stringparam gtkdoc.bookname gtk-doc-manual \
             --stringparam gtkdoc.version $(VERSION) \
             $(top_srcdir)/gtk-doc.xsl \
             $(srcdir)/C/index.docbook

HELP_EXTRA = \
    version.ent \
    html/index.html \
    $(NULL)

install-data-local:
	@installfiles=`echo $(srcdir)/C/html/*`; \
	if test "$$installfiles" = '$(srcdir)/C/html/*'; \
	then echo 1>&2 'Nothing to install' ; \
	else \
	  installdir="$(DESTDIR)$(datadir)/gtk-doc/html/$(HELP_ID)"; \
	  $(mkinstalldirs) $${installdir} ; \
	  for i in $$installfiles; do \
	    echo ' $(INSTALL_DATA) '$$i $$installdir; \
	    $(INSTALL_DATA) $$i $${installdir}; \
	  done; \
	  $(GTKDOC_REBASE) --relative --dest-dir=$(DESTDIR) --html-dir=$${installdir}; \
	fi

uninstall-local:
	@if test -n "$(DOC_MODULE_VERSION)"; then \
	  installdir="$(DESTDIR)$(TARGET_DIR)-$(DOC_MODULE_VERSION)"; \
	else \
	  installdir="$(DESTDIR)$(TARGET_DIR)"; \
	fi; \
	rm -rf $${installdir}

HELP_LINGUAS = bn_IN cs de el en_GB es fr gl gu pt_BR sl sv ta te zh_CN

CLEANFILES = $(_HELP_LC_FILES) $(_HELP_LC_STAMPS) $(_HELP_MOFILES)

GITIGNOREFILES = C/html C/version.ent ??_??/$(HELP_ID).xml ??/$(HELP_ID).xml

-include $(top_srcdir)/git.mk
