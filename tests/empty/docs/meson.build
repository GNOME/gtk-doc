empty_test_source_dir = join_paths(
  srcdir,
  'tests',
  'empty',
  'src'
)

empty_test_docs_dir = join_paths(
  srcdir,
  'tests',
  'empty',
  'docs'
)

empty_test_output_dir = join_paths(
  builddir,
  'tests',
  'empty',
  'docs'
)

empty_test_html_data = []

subdir('xml')

test(
  'test-empty-scan',
  python_prg,
  workdir: empty_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_scan_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(empty_test_output_dir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(empty_test_source_dir),
    '--ignore-headers=config.h',
    '--deprecated-guards=GTKDOC_TESTER_DISABLE_DEPRECATED',
    '--rebuild-sections',
  ],
)

test(
  'test-empty-mkdb',
  python_prg,
  workdir: empty_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkdb_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(empty_test_source_dir),
    '--main-sgml-file=@0@'.format('tester-docs.xml'),
    '--output-format=xml',
    '--xml-mode',
  ],
)

foreach style_data: gtkdoc_style_data
  empty_test_html_data += join_paths(srcdir, 'style', style_data)
endforeach

test(
  'test-empty-mkhtml',
  python_prg,
  workdir: empty_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkhtml_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(join_paths(empty_test_output_dir, 'html')),
    '--html-assets=@0@'.format('@@'.join(empty_test_html_data)),
    '@0@'.format('tester'),
    '@0@'.format(join_paths('..', 'tester-docs.xml')),
    '--uninstalled',
    '--path=@0@'.format(':'.join([
      empty_test_docs_dir,
      srcdir])
    ),
  ],
)

test(
  'test-empty-fixxref',
  python_prg,
  workdir: empty_test_output_dir,
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
  'test-empty-check',
  python_prg,
  workdir: empty_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_check_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--input-dir=@0@'.format(empty_test_docs_dir),
    '--output-dir=@0@'.format(empty_test_output_dir),
  ],
)