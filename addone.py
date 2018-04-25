#!/usr/bin/env python

import requests
from time import sleep
import re
import psycopg2
from psycopg2.extras import RealDictCursor
import htmlmin
from bs4 import BeautifulSoup, Comment

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor(cursor_factory=RealDictCursor)

baseurl = 'http://tvtropes.org/pmwiki/pmwiki.php/'

links = [
 ('Manga/MinamotoKunMonogatari','Minamoto Kun Monogatari'), ('Film/MinAndBill','Min And Bill'),
]

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

for link in links:
    full_link = link[0]
    group, title = full_link.split('/')
    name = link[1]
    
    print full_link
    
    cursor.execute("""select * from media where lower(type) = %s and lower(title) = %s;""", (group.lower(), title.lower()))

    if cursor.rowcount != 0:
        htmlData = cursor.fetchone()['data']
    else:
        req = requests.get(baseurl + full_link).text
        sleep(1)
        soup = BeautifulSoup(req, 'lxml')
        
        if not soup:
            print '* * * * Could not find any soup data for: {}'.format(full_link)
            continue
        
        name_div = soup.find('ul', {'class': 'breadcrumbs'})
        if not name_div:
            print '* * * * Could not find true name (soup) for: {}'.format(full_link)
        else:
            true_name_a = name_div.find_all('a')

            if len(true_name_a) == 0:
                print '* * * * Could not find true name (length) for: {}'.format(full_link)
            else:
                true_name = true_name_a[-1].get('href').replace('http://tvtropes.org','').replace('/pmwiki/pmwiki.php/','')

                if true_name != full_link:
                    true_type, true_title = true_name.split('/')
                    print '-> Setting old {}/{} to {}/{}'.format(group, title, true_type, true_title)
                    group = true_type
                    title = true_title
                    full_link = true_name

        for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
            script.extract()
        for x in soup.find_all(text=lambda text:isinstance(text, Comment)):
            x.extract() 

        htmlData = htmlmin.minify(unicode(soup), remove_empty_space=True)

        try:
            cursor.execute("""INSERT INTO media (type, title, name, data) VALUES (%s, %s, %s, %s);""", (group, title, name, htmlData))
            db.commit()
        except:
            print '\t===== Error with db: {} ====='.format(full_link)
        else:
            print 'Inserted: {}'.format(full_link)

    cursor.execute("""select 1 from tropelist where link = %s;""", (full_link,))
    
    if cursor.rowcount != 0:
        cursor.execute("""delete from tropelist where link = %s;""", (full_link,))
    
    #if cursor.rowcount == 0: #tab in, delete above
    print '\tPopulating...'
    
    alltropes = soupify(htmlData, [], False)

    try:
        cursor.execute("""INSERT INTO tropelist VALUES (%s, %s);""", (full_link, alltropes))
        db.commit()
    except:
        print '\t===== Error: {} ====='.format(full_link)

db.close()
