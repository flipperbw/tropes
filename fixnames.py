#!/usr/bin/env python3

import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup, SoupStrainer

strainer = SoupStrainer('ul', {'class': 'breadcrumbs'})

with psycopg2.connect(host="localhost", user="brett", password="", database="tropes") as db:
    cursor = db.cursor('connector', cursor_factory=RealDictCursor, withhold=True)

    #cursor.itersize = 100

    cursor.execute("""select type,title,data from media where lower(title) similar to '[0-9w-z]%' order by 2, 1;""")

    for row in cursor:
        group = row['type']
        title = row['title']
        data  = row['data']

        link = '{}/{}'.format(group, title)

        sys.stdout.write('\r' + link)
        sys.stdout.write("\033[K")
        sys.stdout.flush()

        soup = BeautifulSoup(data, 'lxml', parse_only=strainer)

        if not soup:
            print('\n* * * * Could not find true name (no soup) for: {}'.format(link))
            continue

        true_name_a = soup.find_all('a')

        if len(true_name_a) == 0:
            print('\n* * * * Could not find true name (length) for: {}'.format(link))
            continue

        true_name = true_name_a[-1].get('href').replace('http://tvtropes.org','').replace('/pmwiki/pmwiki.php/','')
        true_type, true_title = true_name.split('/')

        if true_type == 'Videogame':
            true_type = 'VideoGame'
        elif true_type == 'Comicbook':
            true_type = 'ComicBook'
        elif true_type == 'Webvideo':
            true_type = 'WebVideo'
        elif true_type == 'WebComic':
            true_type = 'Webcomic'

        true_name = '{}/{}'.format(true_type, true_title)

        if true_name != link:
            print('\nSetting old {}/{} to {}/{}'.format(group, title, true_type, true_title))

            with db.cursor() as c2:
                c2.execute("""update media set type = %s, title = %s where type = %s and title = %s;""", (true_type, true_title, group, title))
            db.commit()

print()
