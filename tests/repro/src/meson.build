repro_test_public_h = [
  'tester.h',
]

repro_test_c = [
  'tester.c',
]

repro_test_deps = [
  glib_dep,
]

repro_test_lib = shared_library(
  'reprotester',
  sources: repro_test_c,
  dependencies: repro_test_deps,
  install: false,
)

repro_test_dep = declare_dependency(
  link_with: repro_test_lib,
  include_directories: include_directories('.'),
  dependencies: repro_test_deps,
  sources: repro_test_public_h,
)