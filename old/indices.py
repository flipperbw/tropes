#!/usr/bin/env python

import requests
# noinspection PyProtectedMember
from bs4 import BeautifulSoup, SoupStrainer

strainer = SoupStrainer('div', {'id': 'main-article'})

q = requests.get('https://tvtropes.org/pmwiki/index_report.php').text
soup = BeautifulSoup(q, 'lxml', parse_only=strainer)

for s in soup.select('a[href^="/pmwiki/pmwiki.php"]'):
    href = s.get('href')
    testhref = href.replace('/pmwiki/pmwiki.php/', '').replace('https://tvtropes.org', '')
    print(testhref)
