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

extra_cflags = []
if cc.get_argument_syntax() == 'msvc'
  if cc.get_id() == 'msvc'
    extra_cflags += '/FImsvc_recommended_pragmas.h'
    extra_cflags += cc.get_supported_arguments(['/utf-8'])
  endif
  extra_cflags += '/D_GTKDOC_TESTER_API=__declspec(dllexport)'
endif

gobject_test_lib = shared_library(
  'gobjecttester',
  sources: gobject_test_c,
  dependencies: gobject_test_deps,
  c_args: extra_cflags,
  install: false,
)

gobject_test_dep = declare_dependency(
  link_with: gobject_test_lib,
  include_directories: include_directories('.'),
  dependencies: gobject_test_deps,
  sources: gobject_test_public_h,
)