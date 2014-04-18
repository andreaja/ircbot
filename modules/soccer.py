#!/usr/bin/env python
# coding=utf-8
"""
soccer.py - Phenny scorespro Module
Copyright 2008, Andreas Jacobsen
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

SOURCE = "http://www.scorespro.com/rss/live-soccer.xml"

import urllib, re
from lxml import etree

def soccer(phenny, input):
    text = urllib.unquote(input.group(2)) or "."
    regexp = re.compile("^.*%s.*$" % text, re.IGNORECASE)

    dom = etree.parse(urllib.urlopen(SOURCE))

    matches = 0
    for entry in dom.xpath('.//item'):
        title = entry.find('title')
        if regexp.match(title.text):
            matches += 1
            description = entry.find('description')
            message = "%s (%s)" % (title.text, description.text)
            phenny.say(message.encode("utf-8"))
        if matches > 2:
            return

soccer.command = ['soccer']
soccer.priority = 'low'
soccer.example = '.soccer portsmouth'
soccer.thread = True

if __name__ == '__main__':
   print __doc__.strip()
