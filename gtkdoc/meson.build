config_py = configuration_data()
config_py.set('prefix', get_option('prefix'))
config_py.set('datarootdir', join_paths('${prefix}', get_option('datadir')))
config_py.set('datadir', '${datarootdir}')

config_py.set('DBLATEX', dblatex_prg_path)
config_py.set('FOP', fop_prg_path)
config_py.set('PKG_CONFIG', pkgconfig_prg_path)
config_py.set('XSLTPROC', xsltproc_prg_path)

config_py.set('VERSION', version)
config_py.set('EXEEXT', '')

configure_file(
  input: 'config.py.in',
  output: 'config.py',
  configuration: config_py,
  install: true,
  install_dir: join_paths(
    pkgpythondir,
    'gtkdoc',
  ),
)

gtkdoc_sources = [
  '__init__.py',
  'check.py',
  'common.py',
  'fixxref.py',
  'highlight.py',
  'md_to_db.py',
  'mkdb.py',
  'mkhtml.py',
  'mkhtml2.py',
  'mkman.py',
  'mkpdf.py',
  'rebase.py',
  'scan.py',
  'scangobj.py',
]

custom_target(
  'gtkdoc',
  input: gtkdoc_sources,
  output: gtkdoc_sources,
  build_by_default: true,
  command: ['cp', '-f', '@INPUT@', '@OUTDIR@'],
  install: true,
  install_dir: join_paths(
    pkgpythondir,
    'gtkdoc',
  ),
)