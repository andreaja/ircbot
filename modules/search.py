#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

class Grab(web.urllib.URLopener):
   def __init__(self, *args):
      self.version = 'Mozilla/5.0 (Phenny)'
      web.urllib.URLopener.__init__(self, *args)
      self.addheader('Referer', 'https://github.com/sbp/phenny')
   def http_error_default(self, url, fp, errcode, errmsg, headers):
      return web.urllib.addinfourl(fp, [headers, errcode], "http:" + url)

def google_ajax(query): 
   """Search using AjaxSearch, and return its JSON."""
   if isinstance(query, unicode): 
      query = query.encode('utf-8')
   uri = 'http://ajax.googleapis.com/ajax/services/search/web'
   args = '?v=1.0&safe=off&q=' + web.urllib.quote(query)
   handler = web.urllib._urlopener
   web.urllib._urlopener = Grab()
   bytes = web.get(uri + args)
   web.urllib._urlopener = handler
   return web.json(bytes)

def google_search(query): 
   results = google_ajax(query)
   try: return results['responseData']['results'][0]['unescapedUrl']
   except IndexError: return None
   except TypeError: 
      print results
      return False

def google_count(query): 
   results = google_ajax(query)
   if not results.has_key('responseData'): return '0'
   if not results['responseData'].has_key('cursor'): return '0'
   if not results['responseData']['cursor'].has_key('estimatedResultCount'): 
      return '0'
   return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n): 
   """Format a number with beautiful commas."""
   parts = list(str(n))
   for i in range((len(parts) - 3), 0, -3):
      parts.insert(i, ',')
   return ''.join(parts)

def old_gc(query):
   return formatnumber(google_count(query))

def g(phenny, input): 
   """Queries Google for the specified input."""
   query = input.group(2)
   if not query: 
      return phenny.reply('.g what?')
   query = query.encode('utf-8')
   uri = google_search(query)
   if uri: 
      phenny.reply(uri)
      if not hasattr(phenny.bot, 'last_seen_uri'):
         phenny.bot.last_seen_uri = {}
      phenny.bot.last_seen_uri[input.sender] = uri
   elif uri is False: phenny.reply("Problem getting data from Google.")
   else: phenny.reply("No results found for '%s'." % query)
g.commands = ['g']
g.priority = 'high'
g.example = '.g swhack'

def oldgc(phenny, input): 
   """Returns the number of Google results for the specified input."""
   query = input.group(2)
   if not query: 
      return phenny.reply('.gc what?')
   query = query.encode('utf-8')
   num = formatnumber(google_count(query))
   phenny.say(query + ': ' + num)
oldgc.commands = ['ogc', 'oldgc']
oldgc.example = '.oldgc extrapolate'

r_query = re.compile(
   r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(phenny, input): 
   if not input.group(2):
      return phenny.reply("Nothing to compare.")
   queries = r_query.findall(input.group(2))
   if len(queries) > 6: 
      return phenny.reply('Sorry, can only compare up to six things.')

   results = []
   for i, query in enumerate(queries): 
      query = query.strip('[]')
      query = query.encode('utf-8')
      n = int((formatnumber(google_count(query)) or '0').replace(',', ''))
      results.append((n, query))
      if i >= 2: __import__('time').sleep(0.25)
      if i >= 4: __import__('time').sleep(0.25)

   results = [(term, n) for (n, term) in reversed(sorted(results))]
   reply = ', '.join('%s (%s)' % (t, formatnumber(n)) for (t, n) in results)
   phenny.say(reply)
gcs.commands = ['gcs', 'comp']

r_bing = re.compile(r'<h3><a href="([^"]+)"')

def bing_search(query, lang='en-GB'): 
   query = web.urllib.quote(query)
   base = 'http://www.bing.com/search?mkt=%s&q=' % lang
   bytes = web.get(base + query)
   for result in r_bing.findall(bytes):
      if "r.msn.com/" in result: continue
      return result

def bing(phenny, input): 
   """Queries Bing for the specified input."""
   query = input.group(2)
   if query.startswith(':'): 
      lang, query = query.split(' ', 1)
      lang = lang[1:]
   else: lang = 'en-GB'
   if not query:
      return phenny.reply('.bing what?')

   query = query.encode('utf-8')
   uri = bing_search(query, lang)
   if uri: 
      phenny.reply(uri)
      if not hasattr(phenny.bot, 'last_seen_uri'):
         phenny.bot.last_seen_uri = {}
      phenny.bot.last_seen_uri[input.sender] = uri
   else: phenny.reply("No results found for '%s'." % query)
bing.commands = ['bing']
bing.example = '.bing swhack'

r_duck = re.compile(r'nofollow" class="[^"]+" href="(.*?)">')

def duck_search(query): 
   query = query.replace('!', '')
   query = web.urllib.quote(query)
   uri = 'http://duckduckgo.com/html/?q=%s&kl=uk-en' % query
   bytes = web.get(uri)
   m = r_duck.search(bytes)
   if m: return web.decode(m.group(1))

def duck(phenny, input): 
   query = input.group(2)
   if not query: return phenny.reply('.ddg what?')

   query = query.encode('utf-8')
   uri = duck_search(query)
   if uri: 
      phenny.reply(uri)
      if not hasattr(phenny.bot, 'last_seen_uri'):
         phenny.bot.last_seen_uri = {}
      phenny.bot.last_seen_uri[input.sender] = uri
   else: phenny.reply("No results found for '%s'." % query)
duck.commands = ['duck', 'ddg']

def search(phenny, input): 
   if not input.group(2): 
      return phenny.reply('.search for what?')
   query = input.group(2).encode('utf-8')
   gu = google_search(query) or '-'
   bu = bing_search(query) or '-'
   du = duck_search(query) or '-'

   if (gu == bu) and (bu == du): 
      result = '%s (g, b, d)' % gu
   elif (gu == bu): 
      result = '%s (g, b), %s (d)' % (gu, du)
   elif (bu == du): 
      result = '%s (b, d), %s (g)' % (bu, gu)
   elif (gu == du): 
      result = '%s (g, d), %s (b)' % (gu, bu)
   else: 
      if len(gu) > 250: gu = '(extremely long link)'
      if len(bu) > 150: bu = '(extremely long link)'
      if len(du) > 150: du = '(extremely long link)'
      result = '%s (g), %s (b), %s (d)' % (gu, bu, du)

   phenny.reply(result)
search.commands = ['search']

def suggest(phenny, input): 
   if not input.group(2):
      return phenny.reply("No query term.")
   query = input.group(2).encode('utf-8')
   uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
   answer = web.get(uri + web.urllib.quote(query).replace('+', '%2B'))
   if answer: 
      phenny.say(answer)
   else: phenny.reply('Sorry, no result.')
suggest.commands = ['suggest']

def new_gc(query):
   uri = 'https://www.google.com/search?hl=en&q='
   uri = uri + web.urllib.quote(query).replace('+', '%2B')
   # if '"' in query: uri += '&tbs=li:1'
   bytes = web.get(uri)
   if "did not match any documents" in bytes:
      return "0"
   for result in re.compile(r'(?ims)([0-9,]+) results?').findall(bytes):
      return result
   return None

def newest_gc(query):
   uri = 'https://www.google.com/search?hl=en&q='
   uri = uri + web.urllib.quote(query).replace('+', '%2B')
   bytes = web.get(uri + '&tbs=li:1')
   if "did not match any documents" in bytes:
      return "0"
   for result in re.compile(r'(?ims)([0-9,]+) results?').findall(bytes):
      return result
   return None

def newerest_gc(query):
   uri = 'https://www.google.com/search?hl=en&q='
   uri = uri + web.urllib.quote(query).replace('+', '%2B')
   bytes = web.get(uri + '&prmd=imvns&start=950')
   if "did not match any documents" in bytes:
      return "0"
   for result in re.compile(r'(?ims)([0-9,]+) results?').findall(bytes):
      return result
   return None

def ngc(phenny, input):
   if not input.group(2):
      return phenny.reply("No query term.")
   query = input.group(2).encode('utf-8')
   result = new_gc(query)
   if result:
      phenny.say(query + ": " + result)
   else: phenny.reply("Sorry, couldn't get a result.")

ngc.commands = ['ngc']
ngc.priority = 'high'
ngc.example = '.ngc extrapolate'

def gc(phenny, input):
   if not input.group(2):
      return phenny.reply("No query term.")
   query = input.group(2).encode('utf-8')
   result = query + ": "
   result += (old_gc(query) or "?") + " (api)"
   result += ", " + (newerest_gc(query) or "?") + " (end)"
   result += ", " + (new_gc(query) or "?") + " (site)"
   if '"' in query:
      result += ", " + (newest_gc(query) or "?") + " (verbatim)"
   phenny.say(result)

gc.commands = ['gc']
gc.priority = 'high'
gc.example = '.gc extrapolate'

if __name__ == '__main__': 
   print __doc__.strip()
