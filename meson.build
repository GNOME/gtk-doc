project('gtk-doc', 'c',
  version: '1.29.1',
  license: 'GPL2+',
  meson_version: '>= 0.41.0',
)

gnome = import('gnome')
python = import('python3')

# Versioning
version = meson.project_version()
version_arr = version.split('.')
version_major = version_arr[0].to_int()
version_minor = version_arr[1].to_int()
version_micro = version_arr[2].to_int()

package_name = meson.project_name()

# Paths
srcdir = meson.source_root()
builddir = meson.build_root()

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
libdir = join_paths(prefix, get_option('libdir'))
datadir = join_paths(prefix, get_option('datadir'))

cmakedatadir = join_paths(libdir, 'cmake')

autoconfdatadir = join_paths(datadir, 'aclocal')
pkgdir = join_paths(datadir, package_name)
pkgdatadir = join_paths(pkgdir, 'data')
pkgpythondir = join_paths(pkgdir, 'python')
pkgconfigdir = join_paths(datadir, 'pkgconfig')

# Dependencies
glib_req = '>= 2.38.0'
python3_req = '>= 3.4.0'

glib_dep = dependency('glib-2.0', version: glib_req)
gobject_dep = dependency('gobject-2.0', version: glib_req)
python3_dep = dependency('python3', version: python3_req)

python_prg = python.find_python()

pkgconfig_prg = find_program('pkg-config', required: true)
xsltproc_prg = find_program('xsltproc', required: true)
dblatex_prg = find_program('dblatex', required: false)
fop_prg = find_program('fop', required: false)

source_highlight_prg = find_program('source-highlight', required: false)
highlight_prg = find_program('highlight', required: false)
vim_prg = find_program('vim', required: false)

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

highlight_prg_path = ''
highlight_prg_args = ''
if source_highlight_prg.found()
  highlight_prg_path = join_paths(source_highlight_prg.path())
  highlight_prg_args = [
    '-t4',
    '-s$SRC_LANG',
    '-cstyle.css',
    '--no-doc',
    '-i',
  ]
elif highlight_prg.found()
  highlight_prg_path = join_paths(highlight_prg.path())
  highlight_prg_args = [
    '--syntax=$SRC_LANG',
    '--out-format=xhtml',
    '-f',
    '--class-name=gtkdoc',
  ]
elif vim_prg.found()
  highlight_prg_path = join_paths(vim_prg.path())
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
  '------',
]

message('\n'.join(summary))
