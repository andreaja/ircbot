#!/usr/bin/env python
# coding=utf-8
"""
lastfm.py - Phenny Last.fm Module
Copyright 2008, Andreas Jacobsen
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

API_URI = "http://ws.audioscrobbler.com/2.0/"

import urllib
from lxml import etree

def lastfm(phenny, input):
    if hasattr(phenny.config, 'last_fm_api_key'):
        api_key = phenny.config.last_fm_api_key
    else:
        phenny.say("last.fm not configured")
        return

    user = input.group(2)
    query = urllib.urlencode({
        "method": "user.recenttracks",
        "api_key": api_key,
        "user": user})
    url = API_URI + "?" + query

    try:
        content = urllib.urlopen(url)
    except Exception, err:
        phenny.say("No user details found.")
        return

    dom = etree.parse(content)

    tracks = dom.xpath(".//track")
    if len(tracks) < 1:
        phenny.say("No tracks found.")
        return

    track = tracks[0]

    if track.get("nowplaying") == "true":
        status = "Now playing "
    else:
        status = "Last played "

    message = status
    try:
        message += "%s" % track.find("artist").text
    except:
        pass
    try:
        message += " - %s" % track.find("name").text
    except:
        pass
    try:
        message += " (Album: %s)" % track.find("album").text
    except:
        pass
    if not message:
         phenny.say("No track information found.")
    else:
        phenny.say(message.encode("utf8"))

lastfm.rule = (['lastfm'], r'(\S+)')
lastfm.priority = 'low'
lastfm.example = '.lastfm username'

if __name__ == '__main__':
   print __doc__.strip()

