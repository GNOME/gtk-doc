gtkdoc_help_sources = [
  'index.docbook',
  'fdl-appendix.xml',
]

gnome.yelp(
  package_name,
  sources: gtkdoc_help_sources,
)

conf_data = configuration_data()
conf_data.set('VERSION', version)

configure_file(input : 'version.ent.in',
               output : 'version.ent',
               configuration : conf_data)
