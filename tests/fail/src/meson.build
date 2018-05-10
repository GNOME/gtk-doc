fail_test_public_h = [
  'tester.h',
]

fail_test_c = [
  'tester.c',
]

fail_test_deps = [
  glib_dep,
]

fail_test_lib = shared_library(
  'failtester',
  sources: fail_test_c,
  dependencies: fail_test_deps,
  install: false,
)

fail_test_dep = declare_dependency(
  link_with: fail_test_lib,
  include_directories: include_directories('.'),
  dependencies: fail_test_deps,
  sources: fail_test_public_h,
)