gtkdoc_unit_tests = [
  'check',
  'common',
  'highlight',
  'mkdb',
  'mk-to-db',
  'mkhtml2',
  'scan',
]

foreach test_name: gtkdoc_unit_tests
  test(
    'test-unit-@0@'.format(test_name),
    python_prg,
    env: ['PYTHONPATH=@0@'.format(builddir)],
    args: [
      join_paths(
        srcdir,
        'tests',
        '@0@.py'.format(test_name.underscorify()),
      )
    ],
  )
endforeach

subdir('helpers')

if get_option('tests') == true
  glib_dep = dependency('glib-2.0', version: glib_req)
  gobject_dep = dependency('gobject-2.0', version: glib_req)

  glib_prefix = glib_dep.get_pkgconfig_variable('prefix')
  glib_docpath = join_paths(glib_prefix, 'share', 'gtk-doc', 'html')

  gobject_prefix = gobject_dep.get_pkgconfig_variable('prefix')
  gobject_docpath = join_paths(gobject_prefix, 'share', 'gtk-doc', 'html')

  subdir('annotations')
  subdir('bugs')
  subdir('empty')
  subdir('fail')
  subdir('gobject')
  subdir('program')
endif
