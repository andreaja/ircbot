#!/usr/bin/env python
# coding=utf-8
"""
cur.py - Phenny Currency Module
Copyright 2008, Rus Hughes www.idimmu.net
Licensed under the unicorn license.

http://inamidst.com/phenny/
"""

import re, urllib
from lxml import etree

def cur(phenny, input):
	a, b, c =  input.group(2).split()
	XE_URL = 'http://www.xe.com/tmi/xe-output.php?appid=ffxtn-1.0&from_amount=%s&from=%s&to=%s'
	url = XE_URL % (a, b, c)
	dom = etree.parse(urllib.urlopen(url))
	if dom.xpath('/xe-output/headers/status')[0].text == '0':
		phenny.say('%s %s is %s %s' %(dom.xpath('/xe-output/conversion/from-amount')[0].text, dom.xpath('/xe-output/conversion/from-currency-name')[0].text, dom.xpath('/xe-output/conversion/converted-amount')[0].text, dom.xpath('/xe-output/conversion/to-currency-name')[0].text))
	else:
		phenny.say(dom.xpath('/xe-output/headers/description')[0].text)

cur.commands = ['cur']
cur.priority = 'high'
cur.example = '.cur 1 usd gbp'

if __name__ == '__main__':
	print __doc__.strip()
