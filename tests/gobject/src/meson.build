gobject_test_public_h = [
  'giface.h',
  'gobject.h',
  'gtypes.h',
]

gobject_test_c = [
  'giface.c',
  'gobject.c',
  'gtypes.c',
]

gobject_test_deps = [
  glib_dep,
  gobject_dep,
]

gobject_test_lib = shared_library(
  'gobjecttester',
  sources: gobject_test_c,
  dependencies: gobject_test_deps,
  install: false,
)

gobject_test_dep = declare_dependency(
  link_with: gobject_test_lib,
  include_directories: include_directories('.'),
  dependencies: gobject_test_deps,
  sources: gobject_test_public_h,
)