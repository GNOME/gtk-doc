project('gtk-doc', 'c',
  version: '1.31',
  license: 'GPL2+',
  meson_version: '>= 0.50.0', # needed for https://mesonbuild.com/Python-module.html#path
)

gnome = import('gnome')
python = import('python') # Meson new Python module https://mesonbuild.com/Python-module.html

python3 = python.find_installation('python3')

version = meson.project_version()
package_name = meson.project_name()

# Paths
srcdir = meson.source_root()
builddir = meson.build_root()

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
libdir = join_paths(prefix, get_option('libdir'))
datadir = join_paths(prefix, get_option('datadir'))

cmakedatadir = join_paths(datadir, 'cmake')

autoconfdatadir = join_paths(datadir, 'aclocal')
pkgdir = join_paths(datadir, package_name)
pkgdatadir = join_paths(pkgdir, 'data')
pkgpythondir = join_paths(pkgdir, 'python')
pkgconfigdir = join_paths(datadir, 'pkgconfig')

# Dependencies
glib_req = '>= 2.38.0'
python3_req = '>= 3.4.0'

python3_dep = dependency('python3', version: python3_req)

python_prg = python3

# Python 3 required modules
python3_required_modules = ['pygments']

foreach p : python3_required_modules
  # Source: https://docs.python.org/3/library/importlib.html#checking-if-a-module-can-be-imported
  script = 'import importlib.util; import sys; exit(1) if importlib.util.find_spec(\''+ p +'\') is None else exit(0)'
  if run_command(python3, '-c', script).returncode() != 0
    error('Required Python3 module \'' + p + '\' not found')
  endif
endforeach

pkgconfig_prg = find_program('pkg-config', required: true)
xsltproc_prg = find_program('xsltproc', required: true)
dblatex_prg = find_program('dblatex', required: false)
fop_prg = find_program('fop', required: false)

python_prg_path = join_paths(python_prg.path())
pkgconfig_prg_path = join_paths(pkgconfig_prg.path())
xsltproc_prg_path = join_paths(xsltproc_prg.path())

dblatex_prg_path = ''
if dblatex_prg.found()
  dblatex_prg_path = join_paths(dblatex_prg.path())
endif

fop_prg_path = ''
if fop_prg.found()
  fop_prg_path = join_paths(fop_prg.path())
endif

# Options
generate_pdf_output = true
if not dblatex_prg.found() and not fop_prg.found()
  generate_pdf_output = false
endif

# Code
subdir('gtkdoc')

gtkdoc_binaires = [
  'gtkdoc-check',
  'gtkdoc-depscan',
  'gtkdoc-fixxref',
  'gtkdoc-mkdb',
  'gtkdoc-mkhtml',
  'gtkdoc-mkhtml2',
  'gtkdoc-mkman',
  'gtkdoc-mkpdf',
  'gtkdoc-rebase',
  'gtkdoc-scan',
  'gtkdoc-scangobj',
]

binary_in = configuration_data()
binary_in.set('PYTHON', python_prg_path)
binary_in.set('PKG_CONFIG', pkgconfig_prg_path)

binary_in.set('PYTHON_PACKAGE_DIR', pkgpythondir)

binary_in.set('prefix', get_option('prefix'))
binary_in.set('datarootdir', join_paths('${prefix}', get_option('datadir')))
binary_in.set('datadir', '${datarootdir}')

binary_in.set('PACKAGE', package_name)

binary_in.set('VERSION', version)

foreach binary: gtkdoc_binaires
  configure_file(
    input: '@0@.in'.format(binary),
    output: binary,
    configuration: binary_in,
    install: true,
    install_dir: bindir,
  )
endforeach

# Data
gtkdoc_data = [
  'devhelp2.xsd',
  'devhelp2.xsl',
  'gtk-doc.xsl',
  'version-greater-or-equal.xsl',
]

install_data(
  gtkdoc_data,
  install_dir: pkgdatadir,
)

subdir('style')

if get_option('autotools_support') == true
  subdir('buildsystems/autotools')
endif

if get_option('cmake_support') == true
  subdir('buildsystems/cmake')
endif

gtkdoc_pc = configuration_data()
gtkdoc_pc.set('prefix', prefix)
gtkdoc_pc.set('exec_prefix', '${prefix}')
gtkdoc_pc.set('datadir', join_paths('${prefix}', get_option('datadir')))

gtkdoc_pc.set('PACKAGE', package_name)
gtkdoc_pc.set('VERSION', version)

configure_file(
  input: 'gtk-doc.pc.in',
  output: 'gtk-doc.pc',
  configuration: gtkdoc_pc,
  install: true,
  install_dir: pkgconfigdir,
)

subdir('help')
subdir('tests')

summary = [
  '',
  '------',
  'gtk-doc @0@'.format(version),
  '',
  'Directories:',
  '             prefix: @0@'.format(prefix),
  '             bindir: @0@'.format(bindir),
  '             libdir: @0@'.format(libdir),
  '            datadir: @0@'.format(datadir),
  '',
  'Configuration:',
  '  Autotools support: @0@'.format(get_option('autotools_support')),
  '      CMake support: @0@'.format(get_option('cmake_support')),
  '         PDF output: @0@'.format(generate_pdf_output),
  '        User manual: @0@'.format(get_option('yelp_manual')),
  '         Test suite: @0@'.format(get_option('tests')),
  '------',
]

message('\n'.join(summary))
