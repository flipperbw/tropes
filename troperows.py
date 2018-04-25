#!/usr/bin/env python

import psycopg2
from psycopg2.extras import RealDictCursor
import re
import time
import requests
from bs4 import BeautifulSoup, SoupStrainer

atoz = re.compile('Tropes.To.$')
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
				print 'Found loop, skipping ' + href
        else:
            href = href.replace('http://tvtropes.org/pmwiki/pmwiki.php/', '')
            #maybe only allow Main/
            li.append(href)

    return li


with psycopg2.connect(host="localhost", user="brett", password="", database="tropes") as db:
    cursor = db.cursor('connector', cursor_factory=RealDictCursor, withhold=True)

    cursor.execute("""select type, title, data from media where type||'/'||title not in (select link from tropelist) and not (type = 'Franchise' and title = 'MassEffect');""")
    #cursor.execute("""select * from media where title = 'LooneyTunes' and type = 'WesternAnimation';""")
    
    for row in cursor:
        group = row['type']
        title = row['title']
        data  = row['data']
        
        link = '{}/{}'.format(group, title)

        print link
        
        cursor.execute("""select 1 from tropelist where link = %s;""", (link,))
        if cursor.rowcount != 0:
            print 'Skipping...'
        else:
            alltropes = soupify(data, [], False)

            with db.cursor() as c2:
                try:
                    c2.execute("""INSERT INTO tropelist VALUES (%s, %s);""", (link, alltropes))
                    db.commit()
                except:
                    print 'Error: {}'.format(link)

