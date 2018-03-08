# -*- python -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 1998  Damon Chaplin
#               2007-2016  Stefan Sauer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

''"Fix cross-references in the HTML documentation.''"

# Support both Python 2 and 3
from __future__ import print_function

import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile

from . import common, config

# This contains all the entities and their relative URLs.
Links = {}

# failing link targets we don't warn about even once
NoLinks = {
    'char',
    'double',
    'float',
    'int',
    'long',
    'main',
    'signed',
    'unsigned',
    'va-list',
    'void',
    'GBoxed',
    'GEnum',
    'GFlags',
    'GInterface'
}


def Run(options):
    logging.info('options: %s', str(options.__dict__))

    LoadIndicies(options.module_dir, options.html_dir, options.extra_dir)
    ReadSections(options.module)
    FixCrossReferences(options.module_dir, options.module, options.src_lang)


# TODO(ensonic): try to refactor so that we get a list of path's and then just
# loop over them.
# - module_dir is by default 'html'
# - html_dir can be set by configure, defaults to $(docdir)
def LoadIndicies(module_dir, html_dir, extra_dirs):
    # Cache of dirs we already scanned for index files
    dir_cache = {}

    path_prefix = ''
    m = re.search(r'(.*?)/share/gtk-doc/html', html_dir)
    if m:
        path_prefix = m.group(1)
        logging.info('Path prefix: %s', path_prefix)
    prefix_match = r'^' + re.escape(path_prefix) + r'/'

    # We scan the directory containing GLib and any directories in GNOME2_PATH
    # first, but these will be overriden by any later scans.
    dir = common.GetModuleDocDir('glib-2.0')
    if dir and os.path.exists(dir):
        # Some predefined link targets to get links into type hierarchies as these
        # have no targets. These are always absolute for now.
        Links['GBoxed'] = dir + '/gobject/gobject-Boxed-Types.html'
        Links['GEnum'] = dir + '/gobject/gobject-Enumeration-and-Flag-Types.html'
        Links['GFlags'] = dir + '/gobject/gobject-Enumeration-and-Flag-Types.html'
        Links['GInterface'] = dir + '/gobject/GTypeModule.html'

        if dir != html_dir:
            logging.info('Scanning GLib directory: %s', dir)
            ScanIndices(dir, (re.search(prefix_match, dir) is None), dir_cache)

    path = os.environ.get('GNOME2_PATH')
    if path:
        for dir in path.split(':'):
            dir += 'share/gtk-doc/html'
            if os.path.exists(dir) and dir != html_dir:
                logging.info('Scanning GNOME2_PATH directory: %s', dir)
                ScanIndices(dir, (re.search(prefix_match, dir) is None), dir_cache)

    logging.info('Scanning HTML_DIR directory: %s', html_dir)
    ScanIndices(html_dir, False, dir_cache)
    logging.info('Scanning MODULE_DIR directory: %s', module_dir)
    ScanIndices(module_dir, False, dir_cache)

    # check all extra dirs, but skip already scanned dirs or subdirs of those
    for dir in extra_dirs:
        dir = dir.rstrip('/')
        logging.info('Scanning EXTRA_DIR directory: %s', dir)

        # If the --extra-dir option is not relative and is not sharing the same
        # prefix as the target directory of the docs, we need to use absolute
        # directories for the links
        if not dir.startswith('..') and re.search(prefix_match, dir) is None:
            ScanIndices(dir, True, dir_cache)
        else:
            ScanIndices(dir, False, dir_cache)


def ScanIndices(scan_dir, use_absolute_links, dir_cache):
    if not scan_dir or scan_dir in dir_cache:
        return
    dir_cache[scan_dir] = 1

    logging.info('Scanning index directory: %s, absolute: %d', scan_dir, use_absolute_links)

    # TODO(ensonic): this code is the same as in rebase.py
    if not os.path.isdir(scan_dir):
        logging.info('Cannot open dir "%s"', scan_dir)
        return

    subdirs = []
    for entry in sorted(os.listdir(scan_dir)):
        full_entry = os.path.join(scan_dir, entry)
        if os.path.isdir(full_entry):
            subdirs.append(full_entry)
            continue

        if entry.endswith('.devhelp2'):
            # if devhelp-file is good don't read index.sgml
            ReadDevhelp(full_entry, use_absolute_links)
        elif entry == "index.sgml.gz" and not os.path.exists(os.path.join(scan_dir, 'index.sgml')):
            # debian/ubuntu started to compress this as index.sgml.gz :/
            print(''' Please fix https://bugs.launchpad.net/ubuntu/+source/gtk-doc/+bug/77138 . For now run:
gunzip %s
''' % full_entry)
        elif entry.endswith('.devhelp2.gz') and not os.path.exists(full_entry[:-3]):
            # debian/ubuntu started to compress this as *devhelp2.gz :/
            print('''Please fix https://bugs.launchpad.net/ubuntu/+source/gtk-doc/+bug/1466210 . For now run:
gunzip %s
''' % full_entry)
        # we could consider supporting: gzip module

    # Now recursively scan the subdirectories.
    for subdir in subdirs:
        ScanIndices(subdir, use_absolute_links, dir_cache)


def ReadDevhelp(file, use_absolute_links):
    # Determine the absolute directory, to be added to links in $file
    # if we need to use an absolute link.
    # $file will be something like /prefix/gnome/share/gtk-doc/html/gtk/$file
    # We want the part up to 'html/.*' since the links in $file include
    # the rest.
    dir = "../"
    if use_absolute_links:
        # For uninstalled index files we'd need to map the path to where it
        # will be installed to
        if not file.startswith('./'):
            m = re.search(r'(.*\/)(.*?)\/.*?\.devhelp2', file)
            dir = m.group(1) + m.group(2) + '/'
    else:
        m = re.search(r'(.*\/)(.*?)\/.*?\.devhelp2', file)
        if m:
            dir += m.group(2) + '/'
        else:
            dir = ''

    logging.info('Scanning index file=%s, absolute=%d, dir=%s', file, use_absolute_links, dir)

    for line in common.open_text(file):
        m = re.search(r' link="([^#]*)#([^"]*)"', line)
        if m:
            link = m.group(1) + '#' + m.group(2)
            logging.debug('Found id: %s href: %s', m.group(2), link)
            Links[m.group(2)] = dir + link


def ReadSections(module):
    """We don't warn on missing links to non-public sysmbols."""
    for line in common.open_text(module + '-sections.txt'):
        m1 = re.search(r'^<SUBSECTION\s*(.*)>', line)
        if line.startswith('#') or line.strip() == '':
            continue
        elif line.startswith('<SECTION>'):
            subsection = ''
        elif m1:
            subsection = m1.group(1)
        elif line.startswith('<SUBSECTION>') or line.startswith('</SECTION>'):
            continue
        elif re.search(r'^<TITLE>(.*)<\/TITLE>', line):
            continue
        elif re.search(r'^<FILE>(.*)<\/FILE>', line):
            continue
        elif re.search(r'^<INCLUDE>(.*)<\/INCLUDE>', line):
            continue
        else:
            symbol = line.strip()
            if subsection == "Standard" or subsection == "Private":
                NoLinks.add(common.CreateValidSGMLID(symbol))


def FixCrossReferences(module_dir, module, src_lang):
    # TODO(ensonic): use glob.glob()?
    for entry in sorted(os.listdir(module_dir)):
        full_entry = os.path.join(module_dir, entry)
        if os.path.isdir(full_entry):
            continue
        elif entry.endswith('.html') or entry.endswith('.htm'):
            FixHTMLFile(src_lang, module, full_entry)


def FixHTMLFile(src_lang, module, file):
    logging.info('Fixing file: %s', file)

    content = common.open_text(file).read()

    if config.highlight:
        # FIXME: ideally we'd pass a clue about the example language to the highligher
        # unfortunately the "language" attribute is not appearing in the html output
        # we could patch the customization to have <code class="xxx"> inside of <pre>
        if config.highlight.endswith('vim'):
            def repl_func(m):
                return HighlightSourceVim(src_lang, m.group(1), m.group(2))
            content = re.sub(
                r'<div class=\"(example-contents|informalexample)\"><pre class=\"programlisting\">(.*?)</pre></div>',
                repl_func, content, flags=re.DOTALL)
        else:
            def repl_func(m):
                return HighlightSource(src_lang, m.group(1), m.group(2))
            content = re.sub(
                r'<div class=\"(example-contents|informalexample)\"><pre class=\"programlisting\">(.*?)</pre></div>',
                repl_func, content, flags=re.DOTALL)

        content = re.sub(r'\&lt;GTKDOCLINK\s+HREF=\&quot;(.*?)\&quot;\&gt;(.*?)\&lt;/GTKDOCLINK\&gt;',
                         r'\<GTKDOCLINK\ HREF=\"\1\"\>\2\</GTKDOCLINK\>', content, flags=re.DOTALL)

        # From the highlighter we get all the functions marked up. Now we can turn them into GTKDOCLINK items
        def repl_func(m):
            return MakeGtkDocLink(m.group(1), m.group(2), m.group(3))
        content = re.sub(r'(<span class=\"function\">)(.*?)(</span>)', repl_func, content, flags=re.DOTALL)
        # We can also try the first item in stuff marked up as 'normal'
        content = re.sub(
            r'(<span class=\"normal\">\s*)(.+?)((\s+.+?)?\s*</span>)', repl_func, content, flags=re.DOTALL)

    lines = content.rstrip().split('\n')

    def repl_func_with_ix(i):
        def repl_func(m):
            return MakeXRef(module, file, i + 1, m.group(1), m.group(2))
        return repl_func

    for i in range(len(lines)):
        lines[i] = re.sub(r'<GTKDOCLINK\s+HREF="([^"]*)"\s*>(.*?)</GTKDOCLINK\s*>', repl_func_with_ix(i), lines[i])
        if 'GTKDOCLINK' in lines[i]:
            logging.info('make xref failed for line %d: "%s"', i, lines[i])

    new_file = file + '.new'
    content = '\n'.join(lines)
    with common.open_text(new_file, 'w') as h:
        h.write(content)

    os.unlink(file)
    os.rename(new_file, file)


def MakeXRef(module, file, line, id, text):
    href = Links.get(id)

    # This is a workaround for some inconsistency we have with CreateValidSGMLID
    if not href and ':' in id:
        href = Links.get(id.replace(':', '--'))
    # poor mans plural support
    if not href and id.endswith('s'):
        tid = id[:-1]
        href = Links.get(tid)
        if not href:
            href = Links.get(tid + '-struct')
    if not href:
        href = Links.get(id + '-struct')

    if href:
        # if it is a link to same module, remove path to make it work uninstalled
        m = re.search(r'^\.\./' + module + '/(.*)$', href)
        if m:
            href = m.group(1)
            logging.info('Fixing link to uninstalled doc: %s, %s, %s', id, href, text)
        else:
            logging.info('Fixing link: %s, %s, %s', id, href, text)
        return "<a href=\"%s\">%s</a>" % (href, text)
    else:
        logging.info('no link for: %s, %s', id, text)

        # don't warn multiple times and also skip blacklisted (ctypes)
        if id in NoLinks:
            return text
        # if it's a function, don't warn if it does not contain a "_"
        # (transformed to "-")
        # - gnome coding style would use '_'
        # - will avoid wrong warnings for ansi c functions
        if re.search(r' class=\"function\"', text) and '-' not in id:
            return text
        # if it's a 'return value', don't warn (implicitly created link)
        if re.search(r' class=\"returnvalue\"', text):
            return text
        # if it's a 'type', don't warn if it starts with lowercase
        # - gnome coding style would use CamelCase
        if re.search(r' class=\"type\"', text) and id[0].islower():
            return text
        # don't warn for self links
        if text == id:
            return text

        common.LogWarning(file, line, 'no link for: "%s" -> (%s).' % (id, text))
        NoLinks.add(id)
        return text


def MakeGtkDocLink(pre, symbol, post):
    id = common.CreateValidSGMLID(symbol)

    # these are implicitely created links in highlighed sources
    # we don't want warnings for those if the links cannot be resolved.
    NoLinks.add(id)

    return pre + '<GTKDOCLINK HREF="' + id + '">' + symbol + '</GTKDOCLINK>' + post


def HighlightSource(src_lang, type, source):
    # write source to a temp file
    # FIXME: use .c for now to hint the language to the highlighter
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.c') as f:
        temp_source_file = HighlightSourcePreProcess(f, source)
        highlight_options = config.highlight_options.replace('$SRC_LANG', src_lang)

        logging.info('running %s %s %s', config.highlight, highlight_options, temp_source_file)

        # format source
        highlighted_source = subprocess.check_output(
            [config.highlight] + shlex.split(highlight_options) + [temp_source_file]).decode('utf-8')
        logging.debug('result: [%s]', highlighted_source)
        if config.highlight.endswith('/source-highlight'):
            highlighted_source = re.sub(r'^<\!-- .*? -->', '', highlighted_source, flags=re.MULTILINE | re.DOTALL)
            highlighted_source = re.sub(
                r'<pre><tt>(.*?)</tt></pre>', r'\1', highlighted_source, flags=re.MULTILINE | re.DOTALL)
        elif config.highlight.endswith('/highlight'):
            # need to rewrite the stylesheet classes
            highlighted_source = highlighted_source.replace('<span class="gtkdoc com">', '<span class="comment">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc dir">', '<span class="preproc">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc kwd">', '<span class="function">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc kwa">', '<span class="keyword">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc line">', '<span class="linenum">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc num">', '<span class="number">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc str">', '<span class="string">')
            highlighted_source = highlighted_source.replace('<span class="gtkdoc sym">', '<span class="symbol">')
            # maybe also do
            # highlighted_source = re.sub(r'</span>(.+)<span', '</span><span class="normal">\1</span><span')

    return HighlightSourcePostprocess(type, highlighted_source)


def HighlightSourceVim(src_lang, type, source):
    # write source to a temp file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.h') as f:
        temp_source_file = HighlightSourcePreProcess(f, source)

        # format source
        # TODO(ensonic): use p.communicate()
        script = "echo 'let html_number_lines=0|let html_use_css=1|let html_use_xhtml=1|e %s|syn on|set syntax=%s|run! plugin/tohtml.vim|run! syntax/2html.vim|w! %s.html|qa!' | " % (
            temp_source_file, src_lang, temp_source_file)
        script += "%s -n -e -u NONE -T xterm >/dev/null" % config.highlight
        subprocess.check_call([script], shell=True)

        highlighted_source = common.open_text(temp_source_file + ".html").read()
        highlighted_source = re.sub(r'.*<pre\b[^>]*>\n', '', highlighted_source, flags=re.DOTALL)
        highlighted_source = re.sub(r'</pre>.*', '', highlighted_source, flags=re.DOTALL)

        # need to rewrite the stylesheet classes
        highlighted_source = highlighted_source.replace('<span class="Comment">', '<span class="comment">')
        highlighted_source = highlighted_source.replace('<span class="PreProc">', '<span class="preproc">')
        highlighted_source = highlighted_source.replace('<span class="Statement">', '<span class="keyword">')
        highlighted_source = highlighted_source.replace('<span class="Identifier">', '<span class="function">')
        highlighted_source = highlighted_source.replace('<span class="Constant">', '<span class="number">')
        highlighted_source = highlighted_source.replace('<span class="Special">', '<span class="symbol">')
        highlighted_source = highlighted_source.replace('<span class="Type">', '<span class="type">')

        # remove temp files
        os.unlink(temp_source_file + '.html')

    return HighlightSourcePostprocess(type, highlighted_source)


def HighlightSourcePreProcess(f, source):
    # chop of leading and trailing empty lines, leave leading space in first real line
    source = source.strip(' ')
    source = source.strip('\n')
    source = source.rstrip()

    # cut common indent
    m = re.search(r'^(\s+)', source)
    if m:
        source = re.sub(r'^' + m.group(1), '', source, flags=re.MULTILINE)
    # avoid double entity replacement
    source = source.replace('&lt;', '<')
    source = source.replace('&gt;', '>')
    source = source.replace('&amp;', '&')
    if sys.version_info < (3,):
        source = source.encode('utf-8')
    f.write(source)
    f.flush()
    return f.name


def HighlightSourcePostprocess(type, highlighted_source):
    # chop of leading and trailing empty lines
    highlighted_source = highlighted_source.strip()

    # turn common urls in comments into links
    highlighted_source = re.sub(r'<span class="url">(.*?)</span>',
                                r'<span class="url"><a href="\1">\1</a></span>',
                                highlighted_source, flags=re.DOTALL)

    # we do own line-numbering
    line_count = highlighted_source.count('\n')
    source_lines = '\n'.join([str(i) for i in range(1, line_count + 2)])

    return """<div class="%s">
  <table class="listing_frame" border="0" cellpadding="0" cellspacing="0">
    <tbody>
      <tr>
        <td class="listing_lines" align="right"><pre>%s</pre></td>
        <td class="listing_code"><pre class="programlisting">%s</pre></td>
      </tr>
    </tbody>
  </table>
</div>
""" % (type, source_lines, highlighted_source)
