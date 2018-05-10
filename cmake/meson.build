cmake_in = configuration_data()
cmake_in.set('PACKAGE_VERSION', version)
cmake_in.set('bindir', bindir)

configure_file(
  input: 'GtkDocConfig.cmake.in',
  output: 'GtkDocConfig.cmake',
  configuration: cmake_in,
  install: true,
  install_dir: join_paths(
    cmakedatadir,
    'GtkDoc',
  )
)

configure_file(
  input: 'GtkDocConfigVersion.cmake.in',
  output: 'GtkDocConfigVersion.cmake',
  configuration: cmake_in,
  install: true,
  install_dir: join_paths(
    cmakedatadir,
    'GtkDoc',
  )
)

gtkdoc_cmake_data = [
  'GtkDocScanGObjWrapper.cmake',
]

install_data(
  gtkdoc_cmake_data,
  install_dir: join_paths(
    cmakedatadir,
    'GtkDoc',
  )
)