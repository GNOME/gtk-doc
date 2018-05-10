annotations_test_public_h = [
  'tester.h',
]

annotations_test_c = [
  'tester.c',
]

annotations_test_deps = [
  glib_dep,
  gobject_dep,
]

annotations_test_lib = shared_library(
  'annotationstester',
  sources: annotations_test_c,
  dependencies: annotations_test_deps,
  install: false,
)

annotations_test_dep = declare_dependency(
  link_with: annotations_test_lib,
  include_directories: include_directories('.'),
  dependencies: annotations_test_deps,
  sources: annotations_test_public_h,
)