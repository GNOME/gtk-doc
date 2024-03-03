config_py = configuration_data()
config_py.set('prefix', get_option('prefix'))
config_py.set('datarootdir', join_paths('${prefix}', get_option('datadir')))
config_py.set('datadir', '${datarootdir}')

config_py.set('DBLATEX', dblatex_prg_path)
config_py.set('FOP', fop_prg_path)
config_py.set('PKG_CONFIG', pkgconfig_prg_path)
config_py.set('XSLTPROC', xsltproc_prg_path)

config_py.set('VERSION', meson.project_version())
config_py.set('EXEEXT', '')

configure_file(
  input: 'config_data.py.in',
  output: 'config_data.py',
  configuration: config_py,
  install: true,
  install_dir: pkgpythondir / 'gtkdoc',
)

gtkdoc_sources = [
  '__init__.py',
  'check.py',
  'common.py',
  'config.py',
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

install_data(gtkdoc_sources,
  install_dir: pkgpythondir / 'gtkdoc',
)
