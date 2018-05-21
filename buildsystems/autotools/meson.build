custom_target(
  'gtk-doc.flat.make',
  input: 'gtk-doc.make',
  output: 'gtk-doc.flat.make',
  install: true,
  install_dir: pkgdatadir,
  capture: true,
  command: [
    'sed',
    '-e',
    's/EXTRA_DIST =/EXTRA_DIST +=/',
    '@INPUT@',
  ]
)

custom_target(
  'gtk-doc.m4',
  input: 'gtk-doc.m4',
  output: 'gtk-doc.m4',
  install: true,
  install_dir: autoconfdatadir,
  command: [
    'cp',
    '-f',
    '@INPUT@',
    '@OUTPUT@',
  ],
)
