#!/usr/local/bin/python2.7

import json
import time
import pickle
import requests
from bs4 import BeautifulSoup

selectors = ["VideoGame", "WebVideo", "Anime", "LightNovel", "VisualNovel", "WesternAnimation", "Literature", "Series", "WebAnimation", "Film", "Webcomic", "Franchise", "Manga"]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36", "Content-Type": "application/json; charset=UTF-8", "Accept": "application/json, text/javascript, */*; q=0.01", "Referer": "http://tvtropes.org/pmwiki/browse.php"}

for select in selectors:
    print '===> USING:   ' + select
    empty = 0
    pageNum = 1
    total_list = []

    while empty == 0:
        print pageNum
        data = json.dumps({"selected": [select], "page": pageNum, "sort": "A"})
        q = requests.post("http://tvtropes.org/include/php/browse.api.php", headers=headers, data=data)
        qj = q.json()
        
        empty = qj.get('empty')
        
        if empty == 0:
            soup = BeautifulSoup(''.join(qj.get('html')))
            alist = set([z['href'] for z in soup.find_all('a', href=True)])
            print alist
            
            total_list += alist
            pageNum += 1
            
            time.sleep(1)

    print 'Done'
    print total_list
    
    f = open(select + '.pkl', 'wb')
    pickle.dump(total_list, f)
    f.close()
