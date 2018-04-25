#!/usr/bin/env python

import requests
from time import sleep
import re
import psycopg2
import pickle
import htmlmin
from bs4 import BeautifulSoup, Comment
import sys
from psycopg2.extras import RealDictCursor

# ./indices.py > indices.txt
# for i in $(cat indices.txt); do echo $i; echo "======="; ./missing.py $i; sleep 1; done;

if len(sys.argv) < 2:
    print 'Input search index'
    sys.exit(1)

ind = sys.argv[1]
if 'http://tvtropes.org/pmwiki/pmwiki.php' not in ind:
    ind = 'http://tvtropes.org/pmwiki/pmwiki.php/' + ind

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor(cursor_factory=RealDictCursor)


q = requests.get(ind).text


atoz = re.compile('Tropes.To.$')

def soupify(d, li=[], loop=False):
    soup = BeautifulSoup(d, 'lxml')
    tropeList = soup.select('ul a[title^="http://"]')
    for t in tropeList:
        href = t.get('href')
        if atoz.search(href):
            if not loop:
                print '\tFound new link: ' + href
                hrefdata = requests.get(href).text
                sleep(1)
                li += soupify(hrefdata, li, True)
            else:
                print '\t\tFound loop, skipping ' + href
        else:
            href = href.replace('http://tvtropes.org/pmwiki/pmwiki.php/', '')
            #maybe only allow Main/
            li.append(href)
    return li

soup = BeautifulSoup(q, 'lxml')

for s in soup.select('ul a[title*="pmwiki/pmwiki.php"], ol a[title*="pmwiki/pmwiki.php"]'):
    href = s.get('href')
    testhref = href.replace('/pmwiki/pmwiki.php/','').replace('http://tvtropes.org', '')
    print testhref

    hr_split = testhref.split('/')
    group = hr_split[0]
    
    if group.lower() not in ("animation", "anime", "audioplay", "comicbook", "comicstrip", "disney", "film", "franchise", "letsplay", "lightnovel", "literature", "machinima", "manga", "manhua", "manhwa", "podcast", "radio", "series", "theatre", "videogame", "visualnovel", "webanimation", "webcomic", "weboriginal", "webvideo", "westernanimation"):
        print '\tUnwanted group'
        continue
    
    title = ''.join(hr_split[1:])
    name = s.text
    key = ''
    link = testhref

    if 'Mass Effect' in name or 'MassEffect' in title:
        print '\tSkipping Mass Effect'
        continue

    cursor.execute("""select * from media where type = %s and title = %s;""", (group, title))
    if cursor.rowcount == 0:
        print '\tInserting into media...'

        req = requests.get(href).text
        sleep(1)
        soup = BeautifulSoup(req, 'lxml')

        for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
            script.extract()
        for x in soup.find_all(text=lambda text:isinstance(text, Comment)):
            x.extract() 

        htmlData = htmlmin.minify(unicode(soup), remove_empty_space=True)

        try:
            cursor.execute("""INSERT INTO media (type, title, name, key, data) VALUES (%s, %s, %s, %s, %s);""", (group, title, name, key, htmlData))
            db.commit()
        except:
            print '\t===== Error with db: %s =====' % link

    else:
        htmlData = cursor.fetchone()['data']

    cursor.execute("""select 1 from tropelist where link = %s;""", (link,))

    if cursor.rowcount == 0:
        print '\tPopulating...'
        
        alltropes = soupify(htmlData, [], False)

        try:
            cursor.execute("""INSERT INTO tropelist VALUES (%s, %s);""", (link, alltropes))
            db.commit()
        except:
            print '\t===== Error: %s =====' % link
