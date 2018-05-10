empty_test_public_h = [
  'tester.h',
]

empty_test_c = [
  'tester.c',
]

empty_test_deps = [
  glib_dep,
  gobject_dep,
]

empty_test_lib = shared_library(
  'emptytester',
  sources: empty_test_c,
  dependencies: empty_test_deps,
  install: false,
)

empty_test_dep = declare_dependency(
  link_with: empty_test_lib,
  include_directories: include_directories('.'),
  dependencies: empty_test_deps,
  sources: empty_test_public_h,
)