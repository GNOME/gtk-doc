configure_file(
  input: 'gtkdocize.in',
  output: 'gtkdocize',
  configuration: binary_in,
  install: true,
  install_dir: get_option('bindir'),
)

foreach mode : ['', 'no-xslt']
  if mode == ''
    nested = ''
    flat = '.flat'
  else
    nested = '.' + mode
    flat = nested + '-flat'
  endif

  custom_target(
    'gtk-doc' + flat + '.make',
    input: 'gtk-doc' + nested + '.make',
    output: 'gtk-doc' + flat + '.make',
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

  install_data(
    ['gtk-doc' + nested + '.make'],
    install_dir: pkgdatadir,
  )
endforeach

custom_target(
  'gtk-doc.m4',
  input: 'gtk-doc.m4',
  output: 'gtk-doc.m4',
  install: true,
  install_dir: get_option('datadir') / 'aclocal',
  command: [
    'cp',
    '-f',
    '@INPUT@',
    '@OUTPUT@',
  ],
)
