bugs_test_public_h = [
  'tester.h',
]

bugs_test_c = [
  'tester.c',
]

bugs_test_deps = [
  glib_dep,
]

bugs_test_lib = shared_library(
  'bugstester',
  sources: bugs_test_c,
  dependencies: bugs_test_deps,
  install: false,
)

bugs_test_dep = declare_dependency(
  link_with: bugs_test_lib,
  include_directories: include_directories('.'),
  dependencies: bugs_test_deps,
  sources: bugs_test_public_h,
)