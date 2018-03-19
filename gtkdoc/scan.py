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

"""
Extracts declarations of functions, macros, enums, structs and unions from
header files.

It is called with a module name, an optional source directory, an optional
output directory, and the header files to scan.

It outputs all declarations found to a file named '$MODULE-decl.txt', and the
list of decarations to another file '$MODULE-decl-list.txt'.

This second list file is typically copied to '$MODULE-sections.txt' and
organized into sections ready to output the XML pages.
"""

from __future__ import print_function
from six import iteritems, iterkeys

import logging
import os
import re
import shutil

from . import common

# do not read files twice; checking it here permits to give both srcdir and
# builddir as --source-dir without fear of duplicities
seen_headers = {}


def Run(options):
    logging.info('options: %s', str(options.__dict__))

    if not os.path.isdir(options.output_dir):
        os.mkdir(options.output_dir)

    base_filename = os.path.join(options.output_dir, options.module)
    old_decl_list = base_filename + '-decl-list.txt'
    new_decl_list = base_filename + '-decl-list.new'
    old_decl = base_filename + '-decl.txt'
    new_decl = base_filename + '-decl.new'
    old_types = base_filename + '.types'
    new_types = base_filename + '.types.new'
    sections_file = base_filename + '-sections.txt'

    # If this is the very first run then we create the .types file automatically.
    if not os.path.exists(sections_file) and not os.path.exists(old_types):
        options.rebuild_types = True

    section_list = {}
    decl_list = []
    get_types = []

    for file in options.headers:
        ScanHeader(file, section_list, decl_list, get_types, options)

    for dir in options.source_dir:
        ScanHeaders(dir, section_list, decl_list, get_types, options)

    with common.open_text(new_decl_list, 'w') as f:
        for section in sorted(iterkeys(section_list)):
            f.write(section_list[section])

    with common.open_text(new_decl, 'w') as f:
        for decl in decl_list:
            f.write(decl)

    if options.rebuild_types:
        with common.open_text(new_types, 'w') as f:
            for func in sorted(get_types):
                f.write(func + '\n')

        # remove the file if empty
        if len(get_types) == 0:
            os.unlink(new_types)
            if os.path.exists(old_types):
                os.rename(old_types, old_types + '.bak')
        else:
            common.UpdateFileIfChanged(old_types, new_types, True)

    common.UpdateFileIfChanged(old_decl_list, new_decl_list, True)
    common.UpdateFileIfChanged(old_decl, new_decl, True)

    # If there is no MODULE-sections.txt file yet or we are asked to rebuild it,
    # we copy the MODULE-decl-list.txt file into its place. The user can tweak it
    # later if they want.
    if options.rebuild_sections or not os.path.exists(sections_file):
        new_sections_file = base_filename + '-sections.new'
        shutil.copyfile(old_decl_list, new_sections_file)
        common.UpdateFileIfChanged(sections_file, new_sections_file, False)

    # If there is no MODULE-overrides.txt file we create an empty one
    # because EXTRA_DIST in gtk-doc.make requires it.
    overrides_file = base_filename + '-overrides.txt'
    if not os.path.exists(overrides_file):
        open(overrides_file, 'w').close()


#
# Function    : ScanHeaders
# Description : This scans a directory tree looking for header files.
#
# Arguments   : $source_dir - the directory to scan.
#               $section_list - a reference to the hashmap of sections.
#

def ScanHeaders(source_dir, section_list, decl_list, get_types, options):
    logging.info('Scanning source directory: %s', source_dir)

    # This array holds any subdirectories found.
    subdirs = []

    for file in sorted(os.listdir(source_dir)):
        if file.startswith('.'):
            continue
        fullname = os.path.join(source_dir, file)
        if os.path.isdir(fullname):
            subdirs.append(file)
        elif file.endswith('.h'):
            ScanHeader(fullname, section_list, decl_list, get_types, options)

    # Now recursively scan the subdirectories.
    for dir in subdirs:
        matchstr = r'(\s|^)' + re.escape(dir) + r'(\s|$)'
        if re.search(matchstr, options.ignore_headers):
            continue
        ScanHeaders(os.path.join(source_dir, dir), section_list, decl_list,
                    get_types, options)


#
# Function    : ScanHeader
# Description : This scans a header file, looking for declarations of
#                functions, macros, typedefs, structs and unions, which it
#                outputs to the decl_list.
# Arguments   : $input_file - the header file to scan.
#               $section_list - a map of sections.
#               $decl_list - a list of declarations
# Returns     : it adds declarations to the appropriate list.
#

def ScanHeader(input_file, section_list, decl_list, get_types, options):
    global seen_headers
    slist = []                 # Holds the resulting list of declarations.
    title = ''                 # Holds the title of the section
    in_comment = 0             # True if we are in a comment.
    in_declaration = ''        # The type of declaration we are in, e.g.
                               #   'function' or 'macro'.
    skip_block = 0             # True if we should skip a block.
    symbol = None              # The current symbol being declared.
    decl = ''                  # Holds the declaration of the current symbol.
    ret_type = None            # For functions and function typedefs this
                               #   holds the function's return type.
    pre_previous_line = ''     # The pre-previous line read in - some Gnome
                               #   functions have the return type on one
                               #   line, the function name on the next,
                               #   and the rest of the declaration after.
    previous_line = ''         # The previous line read in - some Gnome
                               #   functions have the return type on one line
                               #   and the rest of the declaration after.
    first_macro = 1            # Used to try to skip the standard #ifdef XXX
                               # define XXX at the start of headers.
    level = None               # Used to handle structs/unions which contain
                               #   nested structs or unions.
    internal = 0               # Set to 1 for internal symbols, we need to
                               #   fully parse, but don't add them to docs
    forward_decls = {}         # Dict of forward declarations, we skip
                               #   them if we find the real declaration
                               #   later.
    doc_comments = {}          # Dict of doc-comments we found.
                               # The key is lowercase symbol name, val=1.

    file_basename = None

    deprecated_conditional_nest = 0
    ignore_conditional_nest = 0

    deprecated = ''
    doc_comment = ''

    # Don't scan headers twice
    canonical_input_file = os.path.realpath(input_file)
    if canonical_input_file in seen_headers:
        logging.info('File already scanned: %s', input_file)
        return

    seen_headers[canonical_input_file] = 1

    file_basename = os.path.split(input_file)[1][:-2]  # filename ends in .h

    # Check if the basename is in the list of headers to ignore.
    matchstr = r'(\s|^)' + re.escape(file_basename) + r'\.h(\s|$)'
    if re.search(matchstr, options.ignore_headers):
        logging.info('File ignored: %s', input_file)
        return

    # Check if the full name is in the list of headers to ignore.
    matchstr = r'(\s|^)' + re.escape(input_file) + r'(\s|$)'
    if re.search(matchstr, options.ignore_headers):
        logging.info('File ignored: %s', input_file)
        return

    if not os.path.exists(input_file):
        logging.warning('File does not exist: %s', input_file)
        return

    logging.info('Scanning %s', input_file)

    for line in common.open_text(input_file):
        # If this is a private header, skip it.
        if re.search(r'^\s*/\*\s*<\s*private_header\s*>\s*\*/', line):
            return

        # Skip to the end of the current comment.
        if in_comment:
            logging.info('Comment: %s', line.strip())
            doc_comment += line
            if re.search(r'\*/', line):
                m = re.search(r'\* ([a-zA-Z][a-zA-Z0-9_]+):', doc_comment)
                if m:
                    doc_comments[m.group(1).lower()] = 1
                in_comment = 0
                doc_comment = ''
            continue

        # Keep a count of #if, #ifdef, #ifndef nesting,
        # and if we enter a deprecation-symbol-bracketed
        # zone, take note.
        m = re.search(r'^\s*#\s*if(?:n?def\b|\s+!?\s*defined\s*\()\s*(\w+)', line)
        if m:
            define_name = m.group(1)
            if deprecated_conditional_nest < 1 and re.search(options.deprecated_guards, define_name):
                deprecated_conditional_nest = 1
            elif deprecated_conditional_nest >= 1:
                deprecated_conditional_nest += 1
            if ignore_conditional_nest == 0 and '__GTK_DOC_IGNORE__' in define_name:
                ignore_conditional_nest = 1
            elif ignore_conditional_nest > 0:
                ignore_conditional_nest = 1

        elif re.search(r'^\s*#\sif', line):
            if deprecated_conditional_nest >= 1:
                deprecated_conditional_nest += 1

            if ignore_conditional_nest > 0:
                ignore_conditional_nest += 1
        elif re.search(r'^\s*#endif', line):
            if deprecated_conditional_nest >= 1:
                deprecated_conditional_nest -= 1

            if ignore_conditional_nest > 0:
                ignore_conditional_nest -= 1

        # If we find a line containing _DEPRECATED, we hope that this is
        # attribute based deprecation and also treat this as a deprecation
        # guard, unless it's a macro definition.
        if deprecated_conditional_nest == 0 and '_DEPRECATED' in line:
            m = re.search(r'^\s*#\s*(if*|define)', line)
            if not (m or in_declaration == 'enum'):
                logging.info('Found deprecation annotation (decl: "%s"): "%s"',
                             in_declaration, line.strip())
                deprecated_conditional_nest += 0.1

        # set flag that is used later when we do AddSymbolToList
        if deprecated_conditional_nest > 0:
            deprecated = '<DEPRECATED/>\n'
        else:
            deprecated = ''

        if ignore_conditional_nest:
            continue

        if not in_declaration:
            # Skip top-level comments.
            m = re.search(r'^\s*/\*', line)
            if m:
                re.sub(r'^\s*/\*', '', line)
                if re.search(r'\*/', line):
                    logging.info('Found one-line comment: %s', line.strip())
                else:
                    in_comment = 1
                    doc_comment = line
                    logging.info('Found start of comment: %s', line.strip())
                continue

            logging.info('no decl: %s', line.strip())

            # avoid generating regex with |'' (matching no string)
            ignore_decorators = ''
            if options.ignore_decorators:
                ignore_decorators = '|' + options.ignore_decorators

            m = re.search(r'^\s*#\s*define\s+(\w+)', line)
            #                   $1                                $3            $4             $5
            m2 = re.search(
                r'^\s*typedef\s+((const\s+|G_CONST_RETURN\s+)?\w+)(\s+const)?\s*(\**)\s*\(\*\s*(\w+)\)\s*\(', line)
            #                    $1                                $3            $4             $5
            m3 = re.search(r'^\s*((const\s+|G_CONST_RETURN\s+)?\w+)(\s+const)?\s*(\**)\s*\(\*\s*(\w+)\)\s*\(', line)
            #                    $1            $2
            m4 = re.search(r'^\s*(\**)\s*\(\*\s*(\w+)\)\s*\(', line)
            #                              $1                                $3
            m5 = re.search(r'^\s*typedef\s*((const\s+|G_CONST_RETURN\s+)?\w+)(\s+const)?\s*', previous_line)
            #                                              $1                                $3            $4             $5
            m6 = re.search(
                r'^\s*(?:\b(?:extern|G_INLINE_FUNC%s)\s*)*((const\s+|G_CONST_RETURN\s+)?\w+)(\s+const)?\s*(\**)\s*\(\*\s*(\w+)\)\s*\(' % ignore_decorators, line)
            m7 = re.search(r'^\s*enum\s+_?(\w+)\s+\{', line)
            m8 = re.search(r'^\s*typedef\s+enum', line)
            m9 = re.search(r'^\s*typedef\s+(struct|union)\s+_(\w+)\s+\2\s*;', line)
            m10 = re.search(r'^\s*(struct|union)\s+(\w+)\s*;', line)
            m11 = re.search(r'^\s*typedef\s+(struct|union)\s*\w*\s*{', line)
            m12 = re.search(r'^\s*typedef\s+(?:struct|union)\s+\w+[\s\*]+(\w+)\s*;', line)
            m13 = re.search(r'^\s*(G_GNUC_EXTENSION\s+)?typedef\s+(.+[\s\*])(\w+)(\s*\[[^\]]+\])*\s*;', line)
            m14 = re.search(
                r'^\s*(extern|[A-Za-z_]+VAR%s)\s+((const\s+|signed\s+|unsigned\s+|long\s+|short\s+)*\w+)(\s+\*+|\*+|\s)\s*(const\s+)*([A-Za-z]\w*)\s*;' % ignore_decorators, line)
            m15 = re.search(
                r'^\s*((const\s+|signed\s+|unsigned\s+|long\s+|short\s+)*\w+)(\s+\*+|\*+|\s)\s*(const\s+)*([A-Za-z]\w*)\s*\=', line)
            m16 = re.search(r'.*G_DECLARE_(FINAL_TYPE|DERIVABLE_TYPE|INTERFACE)\s*\(', line)
            #                                             $1                                                                                                    $2                                                     $3
            m17 = re.search(
                r'^\s*(?:\b(?:extern|G_INLINE_FUNC%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|long\s+|short\s+|struct\s+|union\s+|enum\s+)*\w+)([\s*]+(?:\s*(?:\*+|\bconst\b|\bG_CONST_RETURN\b))*)\s*(_[A-Za-z]\w*)\s*\(' % ignore_decorators, line)
            #                                             $1                                                                                                    $2                                                     $3
            m18 = re.search(
                r'^\s*(?:\b(?:extern|G_INLINE_FUNC%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|long\s+|short\s+|struct\s+|union\s+|enum\s+)*\w+)([\s*]+(?:\s*(?:\*+|\bconst\b|\bG_CONST_RETURN\b))*)\s*([A-Za-z]\w*)\s*\(' % ignore_decorators, line)
            m19 = re.search(r'^\s*([A-Za-z]\w*)\s*\(', line)
            m20 = re.search(r'^\s*\(', line)
            m21 = re.search(r'^\s*struct\s+_?(\w+)', line)
            m22 = re.search(r'^\s*union\s+_(\w+)', line)

            # MACROS

            if m:
                symbol = m.group(1)
                decl = line
                # We assume all macros which start with '_' are private.
                # We also try to skip the first macro if it looks like the
                # standard #ifndef HEADER_FILE #define HEADER_FILE etc.
                # And we only want TRUE & FALSE defined in GLib.
                if not symbol.startswith('_') \
                    and (not re.search(r'#ifndef\s+' + symbol, previous_line)
                         or first_macro == 0) \
                    and ((symbol != 'TRUE' and symbol != 'FALSE')
                         or options.module == 'glib'):
                    in_declaration = 'macro'
                    logging.info('Macro: "%s"', symbol)
                else:
                    logging.info('skipping Macro: "%s"', symbol)
                    in_declaration = 'macro'
                    internal = 1
                first_macro = 0

            # TYPEDEF'D FUNCTIONS (i.e. user functions)
            elif m2:
                p3 = m2.group(3) or ''
                ret_type = "%s%s %s" % (m2.group(1), p3, m2.group(4))
                symbol = m2.group(5)
                decl = line[m2.end():]
                in_declaration = 'user_function'
                logging.info('user function (1): "%s", Returns: "%s"', symbol, ret_type)

            elif re.search(r'^\s*typedef\s*', previous_line) and m3:
                p3 = m3.group(3) or ''
                ret_type = '%s%s %s' % (m3.group(1), p3, m3.group(4))
                symbol = m3.group(5)
                decl = line[m3.end():]
                in_declaration = 'user_function'
                logging.info('user function (2): "%s", Returns: "%s"', symbol, ret_type)

            elif re.search(r'^\s*typedef\s*', previous_line) and m4:
                ret_type = m4.group(1)
                symbol = m4.group(2)
                decl = line[m4.end():]
                if m5:
                    p3 = m5.group(3) or ''
                    ret_type = "%s%s %s" % (m5.group(1), p3, ret_type)
                    in_declaration = 'user_function'
                    logging.info('user function (3): "%s", Returns: "%s"', symbol, ret_type)

            # FUNCTION POINTER VARIABLES
            elif m6:
                p3 = m6.group(3) or ''
                ret_type = '%s%s %s' % (m6.group(1), p3, m6.group(4))
                symbol = m6.group(5)
                decl = line[m6.end():]
                in_declaration = 'user_function'
                logging.info('function pointer variable: "%s", Returns: "%s"', symbol, ret_type)

            # ENUMS

            elif m7:
                re.sub(r'^\s*enum\s+_?(\w+)\s+\{', r'enum \1 {', line)
                # We assume that 'enum _<enum_name> {' is really the
                # declaration of enum <enum_name>.
                symbol = m7.group(1)
                decl = line
                in_declaration = 'enum'
                logging.info('plain enum: "%s"', symbol)

            elif re.search(r'^\s*typedef\s+enum\s+_?(\w+)\s+\1\s*;', line):
                # We skip 'typedef enum <enum_name> _<enum_name>;' as the enum will
                # be declared elsewhere.
                logging.info('skipping enum typedef: "%s"', line)
            elif m8:
                symbol = ''
                decl = line
                in_declaration = 'enum'
                logging.info('typedef enum: -')

            # STRUCTS AND UNIONS

            elif m9:
                # We've found a 'typedef struct _<name> <name>;'
                # This could be an opaque data structure, so we output an
                # empty declaration. If the structure is actually found that
                # will override this.
                structsym = m9.group(1).upper()
                logging.info('%s typedef: "%s"', structsym, m9.group(2))
                forward_decls[m9.group(2)] = '<%s>\n<NAME>%s</NAME>\n%s</%s>\n' % (
                    structsym, m9.group(2), deprecated, structsym)

            elif re.search(r'^\s*(?:struct|union)\s+_(\w+)\s*;', line):
                # Skip private structs/unions.
                logging.info('private struct/union')

            elif m10:
                # Do a similar thing for normal structs as for typedefs above.
                # But we output the declaration as well in this case, so we
                # can differentiate it from a typedef.
                structsym = m10.group(1).upper()
                logging.info('%s:%s', structsym, m10.group(2))
                forward_decls[m10.group(2)] = '<%s>\n<NAME>%s</NAME>\n%s%s</%s>\n' % (
                    structsym, m10.group(2), line, deprecated, structsym)

            elif m11:
                symbol = ''
                decl = line
                level = 0
                in_declaration = m11.group(1)
                logging.info('typedef struct/union "%s"', in_declaration)

            # OTHER TYPEDEFS

            elif m12:
                logging.info('Found struct/union(*) typedef "%s": "%s"', m12.group(1), line)
                if AddSymbolToList(slist, m12.group(1)):
                    decl_list.append('<TYPEDEF>\n<NAME>%s</NAME>\n%s%s</TYPEDEF>\n' % (m12.group(1), deprecated, line))

            elif m13:
                if m13.group(2).split()[0] not in ('struct', 'union'):
                    logging.info('Found typedef: "%s"', line)
                    if AddSymbolToList(slist, m13.group(3)):
                        decl_list.append(
                            '<TYPEDEF>\n<NAME>%s</NAME>\n%s%s</TYPEDEF>\n' % (m13.group(3), deprecated, line))
            elif re.search(r'^\s*typedef\s+', line):
                logging.info('Skipping typedef: "%s"', line)

            # VARIABLES (extern'ed variables)

            elif m14:
                symbol = m14.group(6)
                line = re.sub(r'^\s*([A-Za-z_]+VAR)\b', r'extern', line)
                decl = line
                logging.info('Possible extern var "%s": "%s"', symbol, decl)
                if AddSymbolToList(slist, symbol):
                    decl_list.append('<VARIABLE>\n<NAME>%s</NAME>\n%s%s</VARIABLE>\n' % (symbol, deprecated, decl))

            # VARIABLES

            elif m15:
                symbol = m15.group(5)
                decl = line
                logging.info('Possible global var" %s": "%s"', symbol, decl)
                if AddSymbolToList(slist, symbol):
                    decl_list.append('<VARIABLE>\n<NAME>%s</NAME>\n%s%s</VARIABLE>\n' % (symbol, deprecated, decl))

            # G_DECLARE_*

            elif m16:
                in_declaration = 'g-declare'
                symbol = 'G_DECLARE_' + m16.group(1)
                decl = line[m16.end():]

            # FUNCTIONS

            # We assume that functions which start with '_' are private, so
            # we skip them.
            elif m17:
                ret_type = m17.group(1)
                if m17.group(2):
                    ret_type += ' ' + m17.group(2)
                symbol = m17.group(3)
                decl = line[m17.end():]
                logging.info('internal Function: "%s", Returns: "%s""%s"', symbol, m17.group(1), m17.group(2))
                in_declaration = 'function'
                internal = 1
                if line.strip().startswith('G_INLINE_FUNC'):
                    logging.info('skip block after inline function')
                    # now we we need to skip a whole { } block
                    skip_block = 1

            elif m18:
                ret_type = m18.group(1)
                if m18.group(2):
                    ret_type += ' ' + m18.group(2)
                symbol = m18.group(3)
                decl = line[m18.end():]
                logging.info('Function (1): "%s", Returns: "%s""%s"', symbol, m18.group(1), m18.group(2))
                in_declaration = 'function'
                if line.strip().startswith('G_INLINE_FUNC'):
                    logging.info('skip block after inline function')
                    # now we we need to skip a whole { } block
                    skip_block = 1

            # Try to catch function declarations which have the return type on
            # the previous line. But we don't want to catch complete functions
            # which have been declared G_INLINE_FUNC, e.g. g_bit_nth_lsf in
            # glib, or 'static inline' functions.
            elif m19:
                symbol = m19.group(1)
                decl = line[m19.end():]

                previous_line_strip = previous_line.strip()
                previous_line_words = previous_line_strip.split()

                if not previous_line_strip.startswith('G_INLINE_FUNC'):
                    if not previous_line_words or previous_line_words[0] != 'static':
                        #                                          $ 1                                                                                                   $2
                        pm = re.search(r'^\s*(?:\b(?:extern%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|long\s+|short\s+|struct\s+|union\s+|enum\s+)*\w+)((?:\s*(?:\*+|\bconst\b|\bG_CONST_RETURN\b))*)\s*$' %
                                       ignore_decorators, previous_line)
                        if pm:
                            ret_type = pm.group(1)
                            if pm.group(2):
                                ret_type += ' ' + pm.group(2)
                            logging.info('Function  (2): "%s", Returns: "%s"', symbol, ret_type)
                            in_declaration = 'function'
                    else:
                        logging.info('skip block after inline function')
                        # now we we need to skip a whole { } block
                        skip_block = 1
                        #                                                        $1                                                                                                    $2
                        pm = re.search(r'^\s*(?:\b(?:extern|static|inline%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|long\s+|short\s+|struct\s+|union\s+|enum\s+)*\w+)((?:\s*(?:\*+|\bconst\b|\bG_CONST_RETURN\b))*)\s*$' %
                                       ignore_decorators, previous_line)
                        if pm:
                            ret_type = pm.group(1)
                            if pm.group(2):
                                ret_type += ' ' + pm.group(2)
                            logging.info('Function  (3): "%s", Returns: "%s"', symbol, ret_type)
                            in_declaration = 'function'
                else:
                    if not previous_line_words or previous_line_words[0] != 'static':
                        logging.info('skip block after inline function')
                        # now we we need to skip a whole { } block
                        skip_block = 1
                        #                                                         $1                                                                                                   $2
                        pm = re.search(r'^\s*(?:\b(?:extern|G_INLINE_FUNC%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|long\s+|short\s+|struct\s+|union\s+|enum\s+)*\w+)((?:\s*(?:\*+|\bconst\b|\bG_CONST_RETURN\b))*)\s*$' %
                                       ignore_decorators, previous_line)
                        if pm:
                            ret_type = pm.group(1)
                            if pm.group(2):
                                ret_type += ' ' + pm.group(2)
                            logging.info('Function (4): "%s", Returns: "%s"', symbol, ret_type)
                            in_declaration = 'function'

            # Try to catch function declarations with the return type and name
            # on the previous line(s), and the start of the parameters on this.
            elif m20:
                decl = line[m20.end():]
                pm = re.search(
                    r'^\s*(?:\b(?:extern|G_INLINE_FUNC%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|enum\s+)*\w+)(\s+\*+|\*+|\s)\s*([A-Za-z]\w*)\s*$' % ignore_decorators, previous_line)
                ppm = re.search(r'^\s*(?:\b(?:extern|G_INLINE_FUNC%s)\s*)*((?:const\s+|G_CONST_RETURN\s+|signed\s+|unsigned\s+|struct\s+|union\s+|enum\s+)*\w+(?:\**\s+\**(?:const|G_CONST_RETURN))?(?:\s+|\s*\*+))\s*$' %
                                ignore_decorators, pre_previous_line)
                if pm:
                    ret_type = pm.group(1) + ' ' + pm.group(2)
                    symbol = pm.group(3)
                    in_declaration = 'function'
                    logging.info('Function (5): "%s", Returns: "%s"', symbol, ret_type)

                elif re.search(r'^\s*\w+\s*$', previous_line) and ppm:
                    ret_type = ppm.group(1)
                    ret_type = re.sub(r'\s*\n', '', ret_type, flags=re.MULTILINE)
                    in_declaration = 'function'

                    symbol = previous_line
                    symbol = re.sub(r'^\s+', '', symbol)
                    symbol = re.sub(r'\s*\n', '', symbol, flags=re.MULTILINE)
                    logging.info('Function (6): "%s", Returns: "%s"', symbol, ret_type)

            # } elsif (m/^extern\s+/) {
                # print "DEBUG: Skipping extern: $_"

            # STRUCTS
            elif re.search(r'^\s*struct\s+_?(\w+)\s*\*', line):
                # Skip 'struct _<struct_name> *', since it could be a
                # return type on its own line.
                pass
            elif m21:
                # We assume that 'struct _<struct_name>' is really the
                # declaration of struct <struct_name>.
                symbol = m21.group(1)
                decl = line
                # we will find the correct level as below we do $level += tr/{//
                level = 0
                in_declaration = 'struct'
                logging.info('Struct(_): "%s"', symbol)

            # UNIONS
            elif re.search(r'^\s*union\s+_(\w+)\s*\*', line):
                # Skip 'union _<union_name> *' (see above)
                pass
            elif m22:
                symbol = m22.group(1)
                decl = line
                level = 0
                in_declaration = 'union'
                logging.info('Union(_): "%s"', symbol)
        else:
            logging.info('in decl: skip=%s %s', skip_block, line.strip())
            # If we were already in the middle of a declaration, we simply add
            # the current line onto the end of it.
            if skip_block == 0:
                decl += line
            else:
                # Remove all nested pairs of curly braces.
                brace_remover = r'{[^{]*}'
                bm = re.search(brace_remover, line)
                while bm:
                    line = re.sub(brace_remover, '', line)
                    bm = re.search(brace_remover, line)
                # Then hope at most one remains in the line...
                bm = re.search(r'(.*?){', line)
                if bm:
                    if skip_block == 1:
                        decl += bm.group(1)
                    skip_block += 1
                elif '}' in line:
                    skip_block -= 1
                    if skip_block == 1:
                        # this is a hack to detect the end of declaration
                        decl += ';'
                        skip_block = 0
                        logging.info('2: ---')

                else:
                    if skip_block == 1:
                        decl += line

        if in_declaration == "g-declare":
            dm = re.search(r'\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\).*$', decl)
            # FIXME the original code does s// stuff here and we don't. Is it necessary?
            if dm:
                ModuleObjName = dm.group(1)
                module_obj_name = dm.group(2)
                if options.rebuild_types:
                    get_types.append(module_obj_name + '_get_type')
                forward_decls[ModuleObjName] = '<STRUCT>\n<NAME>%s</NAME>\n%s</STRUCT>\n' % (ModuleObjName, deprecated)
                if symbol.startswith('G_DECLARE_DERIVABLE'):
                    forward_decls[ModuleObjName + 'Class'] = '<STRUCT>\n<NAME>%sClass</NAME>\n%s</STRUCT>\n' % (
                        ModuleObjName, deprecated)
                if symbol.startswith('G_DECLARE_INTERFACE'):
                    forward_decls[ModuleObjName + 'Interface'] = '<STRUCT>\n<NAME>%sInterface</NAME>\n%s</STRUCT>\n' % (
                        ModuleObjName, deprecated)
                in_declaration = ''

        # Note that sometimes functions end in ') G_GNUC_PRINTF (2, 3);' or
        # ') __attribute__ (...);'.
        if in_declaration == 'function':
            regex = r'\)\s*(G_GNUC_.*|.*DEPRECATED.*%s\s*|__attribute__\s*\(.*\)\s*)*;.*$' % ignore_decorators
            pm = re.search(regex, decl, flags=re.MULTILINE)
            if pm:
                logging.info('scrubbing:[%s]', decl.strip())
                decl = re.sub(regex, '', decl, flags=re.MULTILINE)
                logging.info('scrubbed:[%s]', decl.strip())
                if internal == 0:
                    decl = re.sub(r'/\*.*?\*/', '', decl, flags=re.MULTILINE)   # remove comments.
                    decl = re.sub(r'\s*\n\s*(?!$)', ' ', decl, flags=re.MULTILINE)
                    # consolidate whitespace at start/end of lines.
                    decl = decl.strip()
                    ret_type = re.sub(r'/\*.*?\*/', '', ret_type)               # remove comments in ret type.
                    if AddSymbolToList(slist, symbol):
                        decl_list.append('<FUNCTION>\n<NAME>%s</NAME>\n%s<RETURNS>%s</RETURNS>\n%s\n</FUNCTION>\n' %
                                         (symbol, deprecated, ret_type, decl))
                        if options.rebuild_types:
                            # check if this looks like a get_type function and if so remember
                            if symbol.endswith('_get_type') and 'GType' in ret_type and re.search(r'^(void|)$', decl):
                                logging.info(
                                    "Adding get-type: [%s] [%s] [%s]\tfrom %s", ret_type, symbol, decl, input_file)
                                get_types.append(symbol)
                else:
                    internal = 0
                deprecated_conditional_nest = int(deprecated_conditional_nest)
                in_declaration = ''
                skip_block = 0

        if in_declaration == 'user_function':
            if re.search(r'\).*$', decl):
                decl = re.sub(r'\).*$', '', decl)
                if AddSymbolToList(slist, symbol):
                    decl_list.append('<USER_FUNCTION>\n<NAME>%s</NAME>\n%s<RETURNS>%s</RETURNS>\n%s</USER_FUNCTION>\n' %
                                     (symbol, deprecated, ret_type, decl))
                deprecated_conditional_nest = int(deprecated_conditional_nest)
                in_declaration = ''

        if in_declaration == 'macro':
            if not re.search(r'\\\s*$', decl):
                if internal == 0:
                    if AddSymbolToList(slist, symbol):
                        decl_list.append('<MACRO>\n<NAME>%s</NAME>\n%s%s</MACRO>\n' % (symbol, deprecated, decl))
                else:
                    internal = 0
                deprecated_conditional_nest = int(deprecated_conditional_nest)
                in_declaration = ''

        if in_declaration == 'enum':
            em = re.search(r'\}\s*(\w+)?;\s*$', decl)
            if em:
                if symbol == '':
                    symbol = em.group(1)
                if AddSymbolToList(slist, symbol):
                    decl_list.append('<ENUM>\n<NAME>%s</NAME>\n%s%s</ENUM>\n' % (symbol, deprecated, decl))
                deprecated_conditional_nest = int(deprecated_conditional_nest)
                in_declaration = ''

        # We try to handle nested stucts/unions, but unmatched brackets in
        # comments will cause problems.
        if in_declaration == 'struct' or in_declaration == 'union':
            sm = re.search(r'\n\}\s*(\w*);\s*$', decl)
            if level <= 1 and sm:
                if symbol == '':
                    symbol = sm.group(1)

                bm = re.search(r'^(\S+)(Class|Iface|Interface)\b', symbol)
                if bm:
                    objectname = bm.group(1)
                    logging.info('Found object: "%s"', objectname)
                    title = '<TITLE>%s</TITLE>' % objectname

                logging.info('Store struct: "%s"', symbol)
                if AddSymbolToList(slist, symbol):
                    structsym = in_declaration.upper()
                    decl_list.append('<%s>\n<NAME>%s</NAME>\n%s%s</%s>\n' %
                                     (structsym, symbol, deprecated, decl, structsym))
                    if symbol in forward_decls:
                        del forward_decls[symbol]
                deprecated_conditional_nest = int(deprecated_conditional_nest)
                in_declaration = ''
            else:
                # We use tr to count the brackets in the line, and adjust
                # $level accordingly.
                level += line.count('{')
                level -= line.count('}')
                logging.info('struct/union level : %d', level)

        pre_previous_line = previous_line
        previous_line = line

    # print remaining forward declarations
    for symbol in sorted(iterkeys(forward_decls)):
        if forward_decls[symbol]:
            AddSymbolToList(slist, symbol)
            decl_list.append(forward_decls[symbol])

    # add title
    slist = [title] + slist

    logging.info("Scanning %s done", input_file)

    # Try to separate the standard macros and functions, placing them at the
    # end of the current section, in a subsection named 'Standard'.
    # do this in a loop to catch object, enums and flags
    klass = lclass = prefix = lprefix = None
    standard_decl = []
    liststr = '\n'.join(s for s in slist if s) + '\n'
    while True:
        m = re.search(r'^(\S+)_IS_(\S*)_CLASS\n', liststr, flags=re.MULTILINE)
        m2 = re.search(r'^(\S+)_IS_(\S*)\n', liststr, flags=re.MULTILINE)
        m3 = re.search(r'^(\S+?)_(\S*)_get_type\n', liststr, flags=re.MULTILINE)
        if m:
            prefix = m.group(1)
            lprefix = prefix.lower()
            klass = m.group(2)
            lclass = klass.lower()
            logging.info("Found gobject type '%s_%s' from is_class macro", prefix, klass)
        elif m2:
            prefix = m2.group(1)
            lprefix = prefix.lower()
            klass = m2.group(2)
            lclass = klass.lower()
            logging.info("Found gobject type '%s_%s' from is_ macro", prefix, klass)
        elif m3:
            lprefix = m3.group(1)
            prefix = lprefix.upper()
            lclass = m3.group(2)
            klass = lclass.upper()
            logging.info("Found gobject type '%s_%s' from get_type function", prefix, klass)
        else:
            break

        cclass = lclass
        cclass = cclass.replace('_', '')
        mtype = lprefix + cclass

        liststr, standard_decl = replace_once(liststr, standard_decl, r'^%sPrivate\n' % mtype)

        # We only leave XxYy* in the normal section if they have docs
        if mtype not in doc_comments:
            logging.info("  Hide instance docs for %s", mtype)
            liststr, standard_decl = replace_once(liststr, standard_decl, r'^%s\n' % mtype)

        if mtype + 'class' not in doc_comments:
            logging.info("  Hide class docs for %s", mtype)
            liststr, standard_decl = replace_once(liststr, standard_decl, r'^%sClass\n' % mtype)

        if mtype + 'interface' not in doc_comments:
            logging.info("  Hide iface docs for %s", mtype)
            liststr, standard_decl = replace_once(liststr, standard_decl, r'%sInterface\n' % mtype)

        if mtype + 'iface' not in doc_comments:
            logging.info("  Hide iface docs for " + mtype)
            liststr, standard_decl = replace_once(liststr, standard_decl, r'%sIface\n' % mtype)

        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_IS_%s\n' % klass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_TYPE_%s\n' % klass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_%s_get_type\n' % lclass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_%s_CLASS\n' % klass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_IS_%s_CLASS\n' % klass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_%s_GET_CLASS\n' % klass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_%s_GET_IFACE\n' % klass)
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_%s_GET_INTERFACE\n' % klass)
        # We do this one last, otherwise it tends to be caught by the IS_$class macro
        liststr, standard_decl = replace_all(liststr, standard_decl, r'^\S+_%s\n' % klass)

    logging.info('Decl:%s---', liststr)
    logging.info('Std :%s---', ''.join(sorted(standard_decl)))
    if len(standard_decl):
        # sort the symbols
        liststr += '<SUBSECTION Standard>\n' + ''.join(sorted(standard_decl))

    if liststr != '':
        if file_basename not in section_list:
            section_list[file_basename] = ''
        section_list[file_basename] += "<SECTION>\n<FILE>%s</FILE>\n%s</SECTION>\n\n" % (file_basename, liststr)


def replace_once(liststr, standard_decl, regex):
    mre = re.search(regex, liststr,  flags=re.IGNORECASE | re.MULTILINE)
    if mre:
        standard_decl.append(mre.group(0))
        liststr = re.sub(regex, '', liststr, flags=re.IGNORECASE | re.MULTILINE)
    return liststr, standard_decl


def replace_all(liststr, standard_decl, regex):
    mre = re.search(regex, liststr, flags=re.MULTILINE)
    while mre:
        standard_decl.append(mre.group(0))
        liststr = re.sub(regex, '', liststr, flags=re.MULTILINE)
        mre = re.search(regex, liststr, flags=re.MULTILINE)
    return liststr, standard_decl


def AddSymbolToList(slist, symbol):
    """ Adds symbol to list of declaration if not already present.

    Args:
        slist: The list of symbols.
        symbol: The symbol to add to the list.
    """
    if symbol in slist:
        # logging.info('Symbol %s already in list. skipping', symbol)
        # we return False to skip outputting another entry to -decl.txt
        # this is to avoid redeclarations (e.g. in conditional sections).
        return False
    slist.append(symbol)
    return True
