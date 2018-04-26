#!/usr/bin/env python

import psycopg2
from psycopg2.extras import RealDictCursor
import re
import time
import requests
from bs4 import BeautifulSoup, SoupStrainer

atoz = re.compile('Tropes(.|No)(To.)*$')
strainer = SoupStrainer('div', {'class': 'page-content'})

def soupify(d, li=[], loop=False):
    soup = BeautifulSoup(d, 'lxml', parse_only=strainer)
    tropeList = soup.select('ul a[title^="http://"]') #check this for /pmwiki and if title is necessary
    for t in tropeList:
        href = t.get('href')
        if atoz.search(href):
			if not loop:
				print '=> Found new link: ' + href
				hrefdata = requests.get(href).text
				time.sleep(1)
				soupify(hrefdata, li, True)
			else:
				print '--> Found loop, skipping ' + href
        else:
            href = href.replace('http://tvtropes.org/pmwiki/pmwiki.php/', '')
            #maybe only allow Main/
            li.append(href)

    return li


with psycopg2.connect(host="localhost", user="brett", password="", database="tropes") as db:
    cursor = db.cursor('connector', cursor_factory=RealDictCursor, withhold=True)

    cursor.execute("""select id, type, title, data from media m where not exists (select media_id from troperows tr WHERE m.id = tr.media_id);""")
    #cursor.execute("""select id, type, title, data from media where type = 'Anime' and title = 'RebuildOfEvangelion';""")
    
    for row in cursor:
        media_id = row['id']
        group    = row['type']
        title    = row['title']
        data     = row['data']
        
        link = '{}/{}'.format(group, title)

        print link
        
        alltropes = soupify(data, [], False)
        
        insert_data = [(group, title, a.split('/')[0], a.split('/')[1], media_id) for a in set(alltropes)]

        with db.cursor() as c2:
            try:
                c2.executemany("""INSERT INTO troperows (media_type, media_name, trope_type, trope_name, media_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""", insert_data)
                db.commit()
            except:
                print '=> Error: {}'.format(link)

