program_test_source_dir = join_paths(
  srcdir,
  'tests',
  'program',
  'src'
)

program_test_docs_dir = join_paths(
  srcdir,
  'tests',
  'program',
  'docs'
)

program_test_output_dir = join_paths(
  builddir,
  'tests',
  'program',
  'docs'
)

program_test_html_data = []

subdir('xml')

test(
  'test-program-scan',
  python_prg,
  workdir: program_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_scan_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(program_test_output_dir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(program_test_source_dir),
    '--ignore-headers=config.h',
    '--deprecated-guards=GTKDOC_TESTER_DISABLE_DEPRECATED',
    '--rebuild-types',
  ],
)

test(
  'test-program-mkdb',
  python_prg,
  workdir: program_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkdb_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--module=@0@'.format('tester'),
    '--source-dir=@0@'.format(program_test_source_dir),
    '--main-sgml-file=@0@'.format('tester-docs.xml'),
    '--output-format=xml',
    '--xml-mode',
  ],
)

foreach style_data: gtkdoc_style_data
  program_test_html_data += join_paths(srcdir, 'style', style_data)
endforeach

test(
  'test-program-mkhtml',
  python_prg,
  workdir: program_test_output_dir,
  is_parallel: false,
  args: [
    gtkdoc_mkhtml_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--change-dir=@0@'.format(join_paths(program_test_output_dir, 'html')),
    '--html-assets=@0@'.format('@@'.join(program_test_html_data)),
    '@0@'.format('tester'),
    '@0@'.format(join_paths('..', 'tester-docs.xml')),
    '--uninstalled',
    '--path=@0@'.format(':'.join([
      program_test_docs_dir,
      srcdir])
    ),
  ],
)

test(
  'test-program-fixxref',
  python_prg,
  workdir: program_test_output_dir,
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
  'test-program-check',
  python_prg,
  workdir: program_test_docs_dir,
  is_parallel: false,
  args: [
    gtkdoc_check_runner_script,
    '--binary-dir=@0@'.format(builddir),
    '--input-dir=@0@'.format(program_test_docs_dir),
    '--output-dir=@0@'.format(program_test_output_dir),
  ],
)