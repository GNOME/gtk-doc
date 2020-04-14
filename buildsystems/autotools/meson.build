configure_file(
  input: 'gtkdocize.in',
  output: 'gtkdocize',
  configuration: binary_in,
  install: true,
  install_dir: bindir,
)

foreach mode : ['', 'no-xslt']
  if mode == ''
    nested = ''
    flat = '.flat'
  else
    nested = '.' + mode
    flat = nested + '-flat'
  endif

  replace_string_cmd = '''
import fileinput
import sys

with open(sys.argv[1], 'r') as f:
    for l in f:
        print(l.replace('EXTRA_DIST =', 'EXTRA_DIST +='), end='')
'''

  custom_target(
    'gtk-doc' + flat + '.make',
    input: 'gtk-doc' + nested + '.make',
    output: 'gtk-doc' + flat + '.make',
    install: true,
    install_dir: pkgdatadir,
    capture: true,
    command: [
      python3, '-c',
      replace_string_cmd,
      '@INPUT@',
    ]
  )

  install_data(
    ['gtk-doc' + nested + '.make'],
    install_dir: pkgdatadir,
  )
endforeach

copy_file_cmd = '''
import shutil
import sys

shutil.copyfile(sys.argv[1], sys.argv[2])
'''

custom_target(
  'gtk-doc.m4',
  input: 'gtk-doc.m4',
  output: 'gtk-doc.m4',
  install: true,
  install_dir: autoconfdatadir,
  command: [
    python3, '-c',
    copy_file_cmd,
    '@INPUT@',
    '@OUTPUT@',
  ],
)
