#!/usr/bin/env python

import json
import time
import pickle
import requests

selected_namespaces = ["Animation", "Anime", "AudioPlay", "ComicBook", "ComicStrip", "Film", "Franchise", "LetsPlay", "LightNovel", "Literature", "Machinima", "Manga", "Manhua", "Manhwa", "Podcast", "Radio", "Series", "Theatre", "VideoGame", "VisualNovel", "WebAnimation", "Webcomic", "WebOriginal", "WebVideo", "WesternAnimation"]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36", "Content-Type": "application/json; charset=UTF-8", "Accept": "application/json, text/javascript, */*; q=0.01", "Referer": "http://tvtropes.org/pmwiki/browse.php"}


empty = 0
#pageNum = 1
#pageNum = 220
pageNum = 479

f = open('alltropes.pkl', 'a')

#missed 219
    #{'group': u'Film', 'name': u'Hello Mary Lou Prom Night II', 'key': u'383812', 'title': u'HelloMaryLouPromNightII'}
    #{'group': u'Literature', 'name': u'Heretics Of Dune', 'key': u'497943', 'title': u'HereticsOfDune'}

#missed 478
    #{'group': u'WesternAnimation', 'name': u'Superman Shazam The Return Of Black Adam', 'key': u'351964', 'title': u'SupermanShazamTheReturnOfBlackAdam'}
    #{'group': u'VideoGame', 'name': u'Super Robot Wars W', 'key': u'384069', 'title': u'SuperRobotWarsW'}

   
while empty == 0:
    print pageNum
    data = json.dumps({"selected_namespaces": selected_namespaces, "page": pageNum, "sort": "A", "randomize": 0})
    q = requests.post("http://tvtropes.org/ajax/browse.api.php", headers=headers, data=data)
    qj = q.json()
    
    empty = qj.get('empty')
    
    if empty == 0:
        res = qj.get('results')
        
        #total_list = []
        for k,r in res.iteritems():
        	group = r.get('groupname')
        	title = r.get('title')
        	name  = r.get('spaced_title')
        	key   = r.get('article_id')
        
        	entry = {'group': group, 'title': title, 'name': name, 'key': key}
        	print entry
        
        	#total_list.append(entry)
        	pickle.dump(entry, f)
        
        #pickle.dump(total_list, f)
        
        pageNum += 1       
        
        time.sleep(1)

print 'Done'

f.close()
