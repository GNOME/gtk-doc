gobject_test_source_dir = join_paths(
  srcdir,
  'tests',
  'gobject',
  'src'
)

gobject_test_docs_dir = join_paths(
  srcdir,
  'tests',
  'gobject',
  'docs'
)

gobject_test_output_dir = join_paths(
  builddir,
  'tests',
  'gobject',
  'docs'
)

gobject_test_html_data = []

subdir('xml')

fs.copyfile(join_paths(gobject_test_docs_dir, 'tester-sections.txt'))

test(
  'test-gobject-scan',
  python_prg,
  workdir: gobject_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_scan_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(gobject_test_output_dir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(gobject_test_source_dir),
    '--ignore-headers=config.h',
    '--deprecated-guards=GTKDOC_TESTER_DISABLE_DEPRECATED',
    '--rebuild-types',
  ],
)

sanitizer_args = []

if get_option('b_sanitize') == 'address' or get_option('b_sanitize') == 'address,undefined'
  sanitizer_args += [
    '--extra-cflags=-fsanitize=address',
    '--ldflags=-fsanitize=address',
  ]
endif

if get_option('b_sanitize') == 'undefined' or get_option('b_sanitize') == 'address,undefined'
  sanitizer_args += [
    '--extra-cflags=-fsanitize=undefined',
    '--ldflags=-fsanitize=undefined',
  ]
endif

test(
  'test-gobject-scangobj',
  python_prg,
  workdir: gobject_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_scangobj_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--pkg-config=@0@'.format(pkgconfig_prg_path),
    '--extra-pkg=@0@'.format('glib-2.0'),
    '--extra-pkg=@0@'.format('gobject-2.0'),
    '--extra-lib=@0@'.format(gobject_test_lib.full_path()),
    '--module=@0@'.format('tester'),
  ] + sanitizer_args,
  env: [
    'ASAN_OPTIONS=detect_leaks=0',
  ],
)

test(
  'test-gobject-mkdb',
  python_prg,
  workdir: gobject_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkdb_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(gobject_test_source_dir),
    '--main-sgml-file=@0@'.format('tester-docs.xml'),
    '--output-format=xml',
    '--xml-mode',
  ],
)

foreach style_data: gtkdoc_style_data
  gobject_test_html_data += join_paths(srcdir, 'style', style_data)
endforeach

subdir('images') # Appends to gobject_test_html_data

test(
  'test-gobject-mkhtml',
  python_prg,
  workdir: gobject_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkhtml_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(join_paths(gobject_test_output_dir, 'html')),
    '--html-assets=@0@'.format('@@'.join(gobject_test_html_data)),
    '@0@'.format('tester'),
    '@0@'.format(join_paths('..', 'tester-docs.xml')),
    '--uninstalled',
    '--path=@0@'.format(':'.join([
      gobject_test_docs_dir,
      srcdir,
      ])
    ),
  ],
)

test(
  'test-gobject-fixxref',
  python_prg,
  workdir: gobject_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_fixxref_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--module=@0@'.format('tester'),
    '--module-dir=@0@'.format('html'),
    '--extra-dir=@0@'.format(glib_docpath),
    '--extra-dir=@0@'.format(gobject_docpath),
  ],
)

test(
  'test-gobject-check',
  python_prg,
  workdir: gobject_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_check_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--input-dir=@0@'.format(gobject_test_docs_dir),
    '--output-dir=@0@'.format(gobject_test_output_dir),
  ],
)
