#!/usr/local/bin/python2.7

import requests
import time
import psycopg2
import pickle

baseurl = 'http://tvtropes.org/pmwiki/pmwiki.php/'

db = psycopg2.connect(host="localhost", user="postgres", password="", database="tropes")
cursor = db.cursor()

filelist = ['Anime.pkl', 'Film.pkl', 'Franchise.pkl', 'LightNovel.pkl', 'Literature.pkl', 'Manga.pkl', 'Series.pkl', 'VideoGame.pkl', 'VisualNovel.pkl', 'Webcomic.pkl', 'WebVideo.pkl', 'WesternAnimation.pkl']

for f in filelist:
    op = open(f, 'rb')
    linkList = pickle.load(op)
    op.close()
        
    for link in linkList:
        link = link.replace('/pmwiki/pmwiki.php/', '')
        print link
        
        cursor.execute("""select 1 from media where link = %s;""", (link,))
        if cursor.rowcount != 0:
            pass
        else:
            htmlData = requests.get(baseurl + link).text
            try:
                cursor.execute("""INSERT INTO media VALUES (%s, %s);""", (link, htmlData))
                db.commit()
            except:
                print 'Error: %s' % link

        time.sleep(1)

db.close()
