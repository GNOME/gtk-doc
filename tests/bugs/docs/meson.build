bugs_test_source_dir = join_paths(
  srcdir,
  'tests',
  'bugs',
  'src'
)

bugs_test_docs_dir = join_paths(
  srcdir,
  'tests',
  'bugs',
  'docs'
)

bugs_test_output_dir = join_paths(
  builddir,
  'tests',
  'bugs',
  'docs'
)

bugs_test_html_data = []

subdir('xml')

fs.copyfile(join_paths(bugs_test_docs_dir, 'tester-sections.txt'))

test(
  'test-bugs-scan',
  python_prg,
  workdir: bugs_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_scan_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(bugs_test_output_dir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(bugs_test_source_dir),
    '--ignore-headers=config.h',
    '--deprecated-guards=GTKDOC_TESTER_DISABLE_DEPRECATED',
    '--ignore-decorators=GLIB_VAR|GTKDOC_GNUC_CONST|BUG_711598_DEPRECATED_FOR()|MY_DEPRECATED_FOR()',
    '--rebuild-types',
  ],
)

test(
  'test-bugs-mkdb',
  python_prg,
  workdir: bugs_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkdb_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(bugs_test_source_dir),
    '--main-sgml-file=@0@'.format('tester-docs.xml'),
    '--output-format=xml',
    '--xml-mode',
  ],
)

foreach style_data: gtkdoc_style_data
  bugs_test_html_data += join_paths(srcdir, 'style', style_data)
endforeach

test(
  'test-bugs-mkhtml',
  python_prg,
  workdir: bugs_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkhtml_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(join_paths(bugs_test_output_dir, 'html')),
    '--html-assets=@0@'.format('@@'.join(bugs_test_html_data)),
    '@0@'.format('tester'),
    '@0@'.format(join_paths('..', 'tester-docs.xml')),
    '--uninstalled',
    '--path=@0@'.format(':'.join([
      bugs_test_docs_dir,
      srcdir])
    ),
  ],
)

test(
  'test-bugs-fixxref',
  python_prg,
  workdir: bugs_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_fixxref_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--module=@0@'.format('tester'),
    '--module-dir=@0@'.format('html'),
    '--extra-dir=@0@'.format(glib_docpath),
  ],
)

test(
  'test-bugs-check',
  python_prg,
  workdir: bugs_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_check_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--input-dir=@0@'.format(bugs_test_docs_dir),
    '--output-dir=@0@'.format(bugs_test_output_dir),
  ],
)
