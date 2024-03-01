project('gtk-doc', 'c',
  version: '1.33.2',
  license: 'GPL2+',
  meson_version: '>= 0.50.0', # needed for https://mesonbuild.com/Python-module.html#path
)

gnome = import('gnome')
python = import('python') # Meson new Python module https://mesonbuild.com/Python-module.html

python3 = python.find_installation('python3')

# Paths
srcdir = meson.current_source_dir()
builddir = meson.current_build_dir()

bindir = get_option('prefix') / get_option('bindir')
libdir = get_option('prefix') / get_option('libdir')

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name() / 'data'
pkgpythondir = get_option('prefix') / get_option('datadir') / meson.project_name() / 'python'

# Dependencies
glib_req = '>= 2.38.0'

python_prg = python3

# Python 3 required modules
python3_required_modules = ['pygments']

foreach p : python3_required_modules
  # Source: https://docs.python.org/3/library/importlib.html#checking-if-a-module-can-be-imported
  script = 'import importlib.util; import sys; exit(1) if importlib.util.find_spec(\''+ p +'\') is None else exit(0)'
  if run_command(python3, '-c', script, check: false).returncode() != 0
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

binary_in.set('PACKAGE', meson.project_name())
binary_in.set('PACKAGE_BUGREPORT', 'https://gitlab.gnome.org/GNOME/gtk-doc/issues')
binary_in.set('PACKAGE_NAME', meson.project_name())
binary_in.set('PACKAGE_STRING', meson.project_name())
binary_in.set('PACKAGE_TARNAME', meson.project_name())
binary_in.set('PACKAGE_URL', 'https://gitlab.gnome.org/GNOME/gtk-doc')
binary_in.set('PACKAGE_VERSION', meson.project_version())
binary_in.set('VERSION', meson.project_version())

foreach binary: gtkdoc_binaires
  prog = configure_file(
    input: '@0@.in'.format(binary),
    output: binary,
    configuration: binary_in,
    install: true,
    install_dir: bindir,
  )
  meson.override_find_program(binary, prog)
endforeach

configure_file(
  input: 'gtkdoc_uninstalled.py.in',
  output: 'gtkdoc_uninstalled.py',
  configuration: {
    'sourcedir': meson.current_source_dir(),
    'builddir': meson.current_build_dir(),
  },
)

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
gtkdoc_pc.set('prefix', get_option('prefix'))
gtkdoc_pc.set('exec_prefix', '${prefix}')
gtkdoc_pc.set('datadir', join_paths('${prefix}', get_option('datadir')))

gtkdoc_pc.set('PACKAGE', meson.project_name())
gtkdoc_pc.set('VERSION', meson.project_version())

configure_file(
  input: 'gtk-doc.pc.in',
  output: 'gtk-doc.pc',
  configuration: gtkdoc_pc,
  install: true,
  install_dir: get_option('datadir') / 'pkgconfig',
)

subdir('help')
if get_option('tests')
  subdir('tests')
endif

# A dummy dependency object that to use gtkdoc as subproject fallback
# To be used as: dependency('gtk-doc', fallback : ['gtk-doc', 'dummy_dep'])
dummy_dep = declare_dependency()

summary = [
  '',
  '------',
  'gtk-doc @0@'.format(meson.project_version()),
  '',
  'Directories:',
  '             prefix: @0@'.format(get_option('prefix')),
  '             bindir: @0@'.format(bindir),
  '             libdir: @0@'.format(libdir),
  '            datadir: @0@'.format(get_option('prefix') / get_option('datadir')),
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
