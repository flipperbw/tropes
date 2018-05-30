#!/usr/bin/env python

import re
import requests
import sys
from time import sleep
import psycopg2
from psycopg2.extras import RealDictCursor
import htmlmin
from bs4 import BeautifulSoup, SoupStrainer, Comment
from datetime import datetime

# ./indices.py > indices.txt
# for i in $(cat indices.txt); do echo $i; echo "======="; ./missing.py $i; sleep 1; done;

if len(sys.argv) < 2:
    print 'Input search type (index|url|all) and urls (,)'
    sys.exit(1)

search_type = sys.argv[1]
if search_type not in ('index', 'url', 'all'):
    print 'Search type must be index, url, or all'
    sys.exit(1)

if search_type != 'all' and len(sys.argv) < 3:
    print 'Input url'
    sys.exit(1)

# -- globals
domain_base = 'http://tvtropes.org'
uri_base = '/pmwiki/pmwiki.php/'

atoz = re.compile('Tropes(.|No)(To.)*$')
strainer = SoupStrainer('div', {'class': 'page-content'})

wanted_groups = ("animation", "anime", "audioplay", "comicbook", "comicstrip", "disney", "film", "franchise", "letsplay", "lightnovel", "literature", "machinima", "manga", "manhua", "manhwa", "music", "podcast", "radio", "series", "theatre", "videogame", "visualnovel", "webanimation", "webcomic", "weboriginal", "webvideo", "westernanimation")

sleep_delay = 1
# --

url_base = domain_base + uri_base

if search_type == 'all':
    search_urls = None
else:
    search_urls = sys.argv[2].split(',')
    search_urls = [url_base + v if url_base not in v else v for v in search_urls]

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor(cursor_factory=RealDictCursor)

last_request = None


def wait_request(href):
    global last_request
    if not last_request:
        sdiff = 1
    else:
        curr_time = datetime.now()
        sdiff = (curr_time - last_request).total_seconds()

    sleep_time = sleep_delay - sdiff
    if sleep_time > 0:
        sleep(sleep_time)

    txt = requests.get(href).text

    last_request = datetime.now()

    return txt


def clean_soup(soup):
    for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
        script.extract()
    for x in soup.find_all(text=lambda text: isinstance(text, Comment)):
        x.extract()
    return soup


def soupify(d, li=set(), loop=False):
    soup = clean_soup(BeautifulSoup(d, 'lxml', parse_only=strainer))
    tropeList = soup.select('ul a[title^="http://"]')  # check this for /pmwiki and if title is necessary
    for t in tropeList:
        href = t.get('href')
        if atoz.search(href):
            if not loop:
                print '=> Found new link: ' + href
                hrefdata = wait_request(href)
                soupify(hrefdata, li, True)
            else:
                print '--> Found loop, skipping ' + href
        else:
            href = href.replace(url_base, '')
            # maybe only allow Main/
            # todo: fix typos
            li.add(href)

    return li


def get_link_data(link):
    linkurl = link.replace(domain_base, '').replace(uri_base, '')
    link_spl = linkurl.split('/')

    if len(link_spl) != 2:
        link_spl = [False, False]

    return link_spl


class Media(object):
    def __init__(self, group, title, name=None, data=None, media_id=None):
        self.group = group
        self.title = title
        self.name = name
        self.data = data
        self.media_id = media_id

    def get_link(self):
        return '{}/{}'.format(self.group, self.title)

    def get_url(self):
        return url_base + self.get_link()

    def __str__(self):
        return self.get_link()

    def insert_media(self):
        if self.group.lower() not in wanted_groups:
            print '\tUnwanted group: {}'.format(self.group)
            return False

        cursor.execute("""select id, data from media where type = %s and title = %s;""", (self.group, self.title))

        if cursor.rowcount != 0:
            row_data = cursor.fetchone()
            self.media_id = row_data['id']
            self.data = row_data['data']
        else:
            print '\tInserting into media...'

            href = self.get_url()
            req = wait_request(href)

            soup = clean_soup(BeautifulSoup(req, 'lxml'))

            name_div = soup.find('ul', {'class': 'breadcrumbs'})
            if not name_div:
                print '\t=> Could not find true name (soup) for: {}'.format(self.get_link())
            else:
                true_name_a = name_div.find_all('a')

                if len(true_name_a) == 0:
                    print '\t=> Could not find true name (length) for: {}'.format(self.get_link())
                else:
                    true_name = true_name_a[-1].get('href').replace(domain_base, '').replace(uri_base, '')
                    true_type, true_title = true_name.split('/')

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

                    if true_type.lower() not in wanted_groups:
                        print '\tUnwanted group: {}'.format(true_type)
                        return False

                    true_name = '{}/{}'.format(true_type, true_title)
                    if true_name != self.get_link():
                        print '\t-> Switching old {}/{} to {}/{}'.format(self.group, self.title, true_type, true_title)
                        self.group = true_type
                        self.title = true_title

                        cursor.execute("""select 1 from media where type = %s and title = %s;""", (self.group, self.title))
                        if cursor.rowcount != 0:
                            print '\tNew name already exists, skipping...'
                            return False

                htmlData = htmlmin.minify(unicode(soup), remove_empty_space=True)
                self.data = htmlData

            title_divs = soup.select('.page-title')
            if not title_divs:
                print '\t=> Error, could not find name: {}'.format(self.get_link())
            else:
                media_name_spl = title_divs[0].text.split('/')
                if not media_name_spl:
                    print '\t=> Error, could not find name: {}'.format(self.get_link())
                else:
                    self.name = media_name_spl[-1].strip()

            if 'Unable to connect to database server' in self.data:
                print '\t=> Error, Server down: {}'.format(self.get_link())
                return False

            if 'Inexact title. See the list below' in self.data:
                orig_link = self.get_link()

                print '\t=> Inexact title: {}'.format(orig_link)

                found = False
                poss_list = soup.find('div', {'class': 'page-content'}).select('ul a[href^="http://"], ul a[href^="/pmwiki"]')

                for t in poss_list:
                    href = t.get('href')
                    group, title = get_link_data(href)
                    if not (group and title):
                        print '\t=> Could not find proper group and title: {}'.format(href)
                        continue

                    self.group = group
                    self.title = title

                    inex_res = self.insert_media()
                    if inex_res:
                        found = True

                if not found:
                    print '\t=> Error, could not find correct title: {}'.format(orig_link)
                    return False

                return True

            if 'If you want to start this new page, just click the edit button above' in self.data:
                print '\t=> Error, Page does not exist: {}'.format(self.get_link())
                return False

            try:
                cursor.execute("""INSERT INTO media (type, title, name, data) VALUES (%s, %s, %s, %s) RETURNING id;""", (self.group, self.title, self.name, self.data))
                db.commit()
            except:
                print '\t=> Error with db(media): {}'.format(self.get_link())
                return False
            else:
                self.media_id = cursor.fetchone()['id']

        return True

    def insert_tropes(self):
        if not self.data:
            print '\t=> Error (tropes), missing data: {}'.format(self.get_link())
            return False

        cursor.execute("""select 1 from troperows where media_type = %s and media_name = %s;""", (self.group, self.title))
        if cursor.rowcount != 0:
            return False

        print '\tInserting into tropes...'

        alltropes = soupify(self.data, set(), False)

        if len(alltropes) == 0:
            print '\t=> No tropes found (media_len={}): {}'.format(len(self.data), self.get_link())
            return False

        insert_data = [(self.group, self.title, a.split('/')[0], a.split('/')[1], self.media_id) for a in alltropes]

        try:
            cursor.executemany("""INSERT INTO troperows (media_type, media_name, trope_type, trope_name, media_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""", insert_data)
            db.commit()
        except:
            print '\t=> Error with db(tropes): {}'.format(self.get_link())
            return False

        return True


def create_media(href):
    group, title = get_link_data(href)

    if not (group and title):
        print '\t=> Could not find proper group and title: {}'.format(href)
        return False

    this_media = Media(group, title)

    print this_media.get_link()

    med_ins_res = this_media.insert_media()
    if not med_ins_res:
        print '\t=> Error with media, not setting tropes {}'.format(this_media.get_link())
        return False

    this_media.insert_tropes()

    return True


if search_type in ('index', 'url'):
    for u in search_urls:
        q = wait_request(u)
        soup = clean_soup(BeautifulSoup(q, 'lxml'))

        if search_type == 'url':
            create_media(u)
        else:
            for s in soup.select('ul a[title*="pmwiki/pmwiki.php"], ol a[title*="pmwiki/pmwiki.php"]'):
                href = s.get('href')
                create_media(href)

elif search_type == 'all':
    with db.cursor('all_search', cursor_factory=RealDictCursor, withhold=True) as c2:
        c2.execute("""select id, type, title, name, data from media m where not exists (select media_id from troperows tr WHERE m.id = tr.media_id);""")

        for row in c2:
            this_media = Media(row['type'], row['title'], row['name'], row['data'], row['id'])

            print this_media.get_link()

            this_media.insert_tropes()

# todo: refresh materialized view of tropes

cursor.close()
db.close()
