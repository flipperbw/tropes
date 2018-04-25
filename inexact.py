#!/usr/bin/env python

import psycopg2
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup, SoupStrainer

strainer = SoupStrainer('div', {'class': 'page-content'})
baseurl = 'http://tvtropes.org/pmwiki/pmwiki.php/'

goodlist = ("disney", "animation", "anime", "audioplay", "comicbook", "comicstrip", "film", "franchise", "letsplay", "lightnovel", "literature", "machinima", "manga", "manhua", "manhwa", "podcast", "radio", "series", "theatre", "videogame", "visualnovel", "webanimation", "webcomic", "weboriginal", "webvideo", "westernanimation")

unknown = open('unknown.txt', 'w')
tofix   = open('fixlist.txt', 'w')

with psycopg2.connect(host="localhost", user="brett", password="", database="tropes") as db:
    cursor = db.cursor('connector', cursor_factory=RealDictCursor, withhold=True)

    #cursor.execute("""select type, title, data from media where data like '%Inexact title. See the list below%' order by 2,1;""")
    cursor.execute("""select type, title, data from media where data like '%Ambiguity Index%' and length(data) < 60000 order by 2,1;""")
    
    for row in cursor:
        group = row['type']
        title = row['title']
        data  = row['data']
        
        link = '{}/{}'.format(group, title)
        print link

        soup = BeautifulSoup(data, 'lxml', parse_only=strainer)

        if not soup:
            print '\t* * * * Could not find true name (no soup) for: {}'.format(link)
            continue
                  
        poss_list = soup.select('ul a[href^="http://"], ul a[href^="/pmwiki"]')
        
        found = False
        for t in poss_list:
            href = t.get('href')
            tot_title = href.replace('http://tvtropes.org','').replace('/pmwiki/pmwiki.php/','')
            href_group, href_title = tot_title.split('/')
            
            if href_group.lower() in goodlist:
                found = True
                print '\t{}'.format(tot_title)
                tofix.write('{}\n'.format(tot_title))
        
        if not found:
            unknown.write('{}\n'.format(link))
                
                #with db.cursor() as c2:
                #    c2.execute("""update media set type = %s, title = %s where type = %s and title = %s;""", (true_type, true_title, group, title))
                #db.commit()


unknown.close()
tofix.close()
