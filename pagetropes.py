#!/usr/bin/env python

import requests
import time
import psycopg2
import pickle
import htmlmin
from bs4 import BeautifulSoup, Comment

baseurl = 'http://tvtropes.org/pmwiki/pmwiki.php'

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor()

def loadall():
    with open('alltropes.pkl', "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

items = loadall()

for item in items:
    group = item.get('group')
    title = item.get('title')
    name  = item.get('name')
    key   = item.get('key')
    
    if not (group and title):
        print 'Error: {}, {}'.format(group, title)
        continue
    
    cursor.execute("""select 1 from media where type = %s and title = %s;""", (group, title))
    if cursor.rowcount != 0:
        pass
    else:
        link = '{}/{}/{}'.format(baseurl, group, title)
        print link
        
        try:
            htmlData = requests.get(link).text
            soup = BeautifulSoup(htmlData, 'lxml')
            
            for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
                script.extract()
            for x in soup.find_all(text=lambda text:isinstance(text, Comment)):
                x.extract() 
            
            htmlData = htmlmin.minify(unicode(soup), remove_empty_space=True)
        except:
            print 'Error with fetching: %s' % link
        else:
            try:
                cursor.execute("""INSERT INTO media (type, title, name, key, data) VALUES (%s, %s, %s, %s, %s);""", (group, title, name, key, htmlData))
                db.commit()
            except:
                print 'Error with db: %s' % link

        time.sleep(1)

db.close()
