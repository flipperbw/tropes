#!/usr/bin/env python3

import requests
from time import sleep
import psycopg2
from psycopg2.extras import RealDictCursor
import htmlmin
from bs4 import BeautifulSoup, Comment

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor(cursor_factory=RealDictCursor)

baseurl = 'http://tvtropes.org/pmwiki/pmwiki.php/'

#links = []
with open('fixlist.txt', 'r') as f:
    links = [line.strip() for line in f]

for link in links:
    print(link)

    group, title = link.split('/')

    cursor.execute("""select 1 from media where lower(type) = %s and lower(title) = %s;""", (group.lower(), title.lower()))

    if cursor.rowcount != 0:
        print('\tSkipping...')
    else:
        req = requests.get(baseurl + link).text
        sleep(1)

        if 'Inexact title. See the list below' in req:
            print('\t* * * Inexact title: {}'.format(link))
            continue

        if 'Unable to connect to database server' in req:
            print('\t* * * Server down: {}'.format(link))
            continue

        if 'If you want to start this new page, just click the edit button above' in req:
            print('\t* * * Page does not exist: {}'.format(link))
            continue

        soup = BeautifulSoup(req, 'lxml')

        if not soup:
            print('\t* * * Could not find any soup data for: {}'.format(link))
            continue

        for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
            script.extract()
        for x in soup.find_all(text=lambda text:isinstance(text, Comment)):
            x.extract()

        name_div = soup.find('ul', {'class': 'breadcrumbs'})
        if not name_div:
            print('\t* * * Could not find true name (soup) for: {}'.format(link))
        else:
            true_name_a = name_div.find_all('a')

            if len(true_name_a) == 0:
                print('\t* * * Could not find true name (length) for: {}'.format(link))
            else:
                true_name = true_name_a[-1].get('href').replace('http://tvtropes.org','').replace('/pmwiki/pmwiki.php/','')
                true_type, true_title = true_name.split('/')

                if true_type.lower() not in ("animation", "anime", "audioplay", "comicbook", "comicstrip", "disney", "film", "franchise", "letsplay", "lightnovel", "literature", "machinima", "manga", "manhua", "manhwa", "podcast", "radio", "series", "theatre", "videogame", "visualnovel", "webanimation", "webcomic", "weboriginal", "webvideo", "westernanimation"):
                    print('\tUnwanted group')
                    continue

                if true_type == 'Videogame':
                    true_type = 'VideoGame'
                elif true_type == 'Comicbook':
                    true_type = 'ComicBook'
                elif true_type == 'Webvideo':
                    true_type = 'WebVideo'
                elif true_type == 'WebComic':
                    true_type = 'Webcomic'
                elif true_type == 'Lightnovel':
                    true_type = 'LightNovel'

                true_name = '{}/{}'.format(true_type, true_title)

                if true_name != link:
                    print('\tSetting old {}/{} to {}/{}'.format(group, title, true_type, true_title))
                    group = true_type
                    title = true_title
                    link = true_name

                    cursor.execute("""select 1 from media where lower(type) = %s and lower(title) = %s;""", (group.lower(), title.lower()))
                    if cursor.rowcount != 0:
                        print('\tNew name already exists, skipping...')
                        continue

        htmlData = htmlmin.minify(str(soup), remove_empty_space=True)

        try:
            cursor.execute("""INSERT INTO media (type, title, data) VALUES (%s, %s, %s);""", (group, title, htmlData))
            db.commit()
        except:
            print('\t* * * Error with db: {}'.format(link))
        else:
            print('\tInserted: {}'.format(link))

db.close()
