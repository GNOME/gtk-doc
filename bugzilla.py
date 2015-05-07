#!/usr/bin/env python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4


# parse HTML from bugzilla.gnome.org to create a list of bugs for a given
# product, component and target_milestone

import re
import os
import sys
import codecs
import urllib
import HTMLParser

# a sample bug line we parse for future reference:
#<TR VALIGN=TOP ALIGN=LEFT CLASS="Nor" ><TD><A HREF="show_bug.cgi?id=78267">78267</A> <td class=severity><nobr>min</nobr></td><td class=priority><nobr>Nor</nobr></td><td class=owner><nobr>thomas@apestaart.org</nobr></td><td class=status><nobr>RESO</nobr></td><td class=resolution><nobr>FIXE</nobr></td><td class=summary>autogen.sh doesn't take --prefix and similar to configure</td></TR>

# a sample bug section after olav's updating of bugzilla
#    <td class="first-child">
#      <a href="show_bug.cgi?id=147641">147641</a>
#      <span style="display: none"></span>
#    </td>
#
#    <td style="white-space: nowrap">nor
#    </td>
#    <td style="white-space: nowrap">Nor
#    </td>
#    <td style="white-space: nowrap">Linu
#    </td>
#    <td style="white-space: nowrap">GStreamer
#    </td>
#    <td style="white-space: nowrap">RESO
#    </td>
#    <td style="white-space: nowrap">FIXE
#    </td>
#    <td >[docs] pydoc segfaults when viewing gst package doc
#    </td>
#
#  </tr>


URL = 'http://bugzilla.gnome.org/buglist.cgi?product=%s&component=%s&target_milestone=%s'

# reg = re.compile('<TR.*id=(\d+)".*summary>(.*)<\/td')

HEADER = ' Changes\n'
ITEM = ' o %s : %s'
FOOTER = '\n Contributors\n'

default_product = "gtk-doc"

TD_ID = 1
TD_SUMMARY = 7
# after Olav's changes, it's now number 8
#TD_SUMMARY = 8

# Horrible, don't look here
class HP(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.tr = 0
        self.td = 0
        self.bugs = []
        self.bugno = 0
        self.descr = ""

    def handle_starttag(self, tag, data):
        if tag == 'tr':
            self.tr = 1
            return
        # count td's
        elif self.tr and tag.startswith('td'):
            self.td += 1

    # all &gt; refs are handled through this method; append them to self.descr
    def handle_entityref(self, name):
        self.descr += " &%s; " % name

    # can be called more than once for one td
    def handle_data(self, data):
        if not self.tr:
            return
        data = data.strip()
        if not data:
            return
        
        #print self.td, self.tr, repr(data)

        # check what td it is in
        if self.td == TD_ID:
            try:
                self.bugno = int(data)
                #print "got id: ", self.bugno
            except ValueError:
                self.bugno = 0
        elif self.td == TD_SUMMARY:
            # the summary td
            self.descr += data
            #print "got descr: ", self.descr
        
    def handle_endtag(self, tag):
        if tag == 'tr':
            self.tr = 0
            self.td = 0
            #print "end tag: ", self.bugno, self.descr
            if self.bugno != 0:
                self.bugs.append((self.bugno, self.descr))
                self.bugno = 0
                self.descr = ""

def main(args):
    if len(args) < 3:
        print 'Usage: %s component milestone [product] [file]' % args[0]
        return 2

    component = args[1]
    milestone = args[2]

    if len(args) <= 3:
        product = default_product
    else:
        product = args[3]

    if len(args) <= 4:
        output = None
    else:
        output = args[4]

    url = URL % (product, urllib.quote(component), milestone)
    fd = urllib.urlopen(url)
    
    hp = HP()
    hp.feed(fd.read())
    
    lines = ["\n", ]
    lines.append(HEADER)
    for bug_id, summary in hp.bugs:
        lines.append(ITEM % (bug_id, summary))
    lines.append(FOOTER)
    bugs = "\n".join(lines)

    if not output:
        print bugs
    else:
        # get original
        #doc = codecs.open(output, "r", encoding='utf-8').read()
        doc = open(output, "r").read()
        matcher = re.compile('(.*)<bugs>.*</bugs>(.*)',
            re.DOTALL)
        match = matcher.search(doc)
        pre = match.expand('\\1')
        post = match.expand('\\2')

        backup = output + ".bugs.bak"
        os.rename(output, backup)
        handle = open(output, "w")
        handle.write(pre + bugs + post)
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))
