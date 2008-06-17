#!/usr/bin/env python
"""
e2.py - Phenny everything2 Module
"""

import urllib

def e2(phenny, input):
   keyword = input.group(2)
   keyword = urllib.quote(keyword)
   msg = "e2: http://everything2.com/index.pl?node=%s" % (keyword,)
   phenny.say(msg)
e2.commands = ['e2']
e2.example = '.e2 pies'
