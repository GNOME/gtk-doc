EXTRA_DIST = \
	GtkDocConfig.cmake.in \
	GtkDocConfigVersion.cmake.in	 \
	GtkDocScanGObjWrapper.cmake

CLEANFILES = \
  GtkDocConfig.cmake \
  GtkDocConfigVersion.cmake

# Generate this here rather than via configure.ac so that
# bindir is substituted as an expanded path rather than
# using ${exec_prefix} as it would if substituted via
# configure.ac.
GtkDocConfig.cmake: GtkDocConfig.cmake.in
	$(SED) -e 's|[@]bindir@|$(bindir)|g' < "$<" > "$@"

cmakedir = $(libdir)/cmake/GtkDoc
cmake_DATA = \
	GtkDocConfig.cmake \
	GtkDocConfigVersion.cmake \
	GtkDocScanGObjWrapper.cmake

-include $(top_srcdir)/git.mk
