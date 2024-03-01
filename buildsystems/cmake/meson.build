cmake_in = configuration_data()
cmake_in.set('PACKAGE_VERSION', meson.project_version())

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
  'GtkDocConfig.cmake',
  'GtkDocScanGObjWrapper.cmake',
]

install_data(
  gtkdoc_cmake_data,
  install_dir: join_paths(
    cmakedatadir,
    'GtkDoc',
  )
)
