#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

q = requests.get('http://tvtropes.org/pmwiki/index_report.php').text
soup = BeautifulSoup(q, 'lxml')

for s in soup.select('ul a[title^="/pmwiki/pmwiki.php"]'):
    href= s.get('href')
    testhref = href.replace('/pmwiki/pmwiki.php/','').replace('http://tvtropes.org', '')
    print(testhref)
