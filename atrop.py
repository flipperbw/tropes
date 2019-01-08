#!/usr/bin/env python3

from datetime import datetime
import logging
import re
import requests
import sys
from time import sleep

# noinspection PyProtectedMember
from bs4 import BeautifulSoup, SoupStrainer, Comment
import htmlmin
import psycopg2
from psycopg2.extras import RealDictCursor


file_handler = logging.FileHandler(filename='atrop.log')
stdout_handler = logging.StreamHandler(sys.stdout)

file_handler.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

file_handler.setFormatter(logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


# ./indices.py > indices.txt
# for i in $(cat indices.txt); do echo $i; echo "======="; ./missing.py $i; sleep 1; done;

if len(sys.argv) < 2:
    print('Input search type (index|url|fix|all) and urls (,)')
    sys.exit(1)

search_type = sys.argv[1]
if search_type not in ('index', 'url', 'fix', 'all'):
    print('Search type must be index, url, fix, or all')
    sys.exit(1)

if search_type in ('index', 'url') and len(sys.argv) < 3:
    print('Input url')
    sys.exit(1)


# -- globals

domain_base = 'https://tvtropes.org'
uri_base = '/pmwiki/pmwiki.php/'

atoz = re.compile('Tropes(.|No)(To.)*$')
strainer = SoupStrainer('div', {'id': 'main-article'})

wanted_groups = (
    "Animation", "Anime", "AudioPlay", "ComicBook", "ComicStrip", "Disney", "Film", "Franchise", "LetsPlay", "LightNovel", "Literature", "Machinima", "Manga", "Manhua", "Manhwa",
    "Music", "Podcast", "Radio", "Series", "Theatre", "VideoGame", "VisualNovel", "WebAnimation", "Webcomic", "WebOriginal", "WebVideo", "WesternAnimation"
)

sleep_delay = 0.5

# --

lower_wanted_groups = tuple([g.lower() for g in wanted_groups])

cp1252 = {
    # from http://www.microsoft.com/typography/unicode/1252.htm
    u"\x80": u"\u20AC",  # EURO SIGN
    u"\x82": u"\u201A",  # SINGLE LOW-9 QUOTATION MARK
    u"\x83": u"\u0192",  # LATIN SMALL LETTER F WITH HOOK
    u"\x84": u"\u201E",  # DOUBLE LOW-9 QUOTATION MARK
    u"\x85": u"\u2026",  # HORIZONTAL ELLIPSIS
    u"\x86": u"\u2020",  # DAGGER
    u"\x87": u"\u2021",  # DOUBLE DAGGER
    u"\x88": u"\u02C6",  # MODIFIER LETTER CIRCUMFLEX ACCENT
    u"\x89": u"\u2030",  # PER MILLE SIGN
    u"\x8A": u"\u0160",  # LATIN CAPITAL LETTER S WITH CARON
    u"\x8B": u"\u2039",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    u"\x8C": u"\u0152",  # LATIN CAPITAL LIGATURE OE
    u"\x8E": u"\u017D",  # LATIN CAPITAL LETTER Z WITH CARON
    u"\x91": u"\u2018",  # LEFT SINGLE QUOTATION MARK
    u"\x92": u"\u2019",  # RIGHT SINGLE QUOTATION MARK
    u"\x93": u"\u201C",  # LEFT DOUBLE QUOTATION MARK
    u"\x94": u"\u201D",  # RIGHT DOUBLE QUOTATION MARK
    u"\x95": u"\u2022",  # BULLET
    u"\x96": u"\u2013",  # EN DASH
    u"\x97": u"\u2014",  # EM DASH
    u"\x98": u"\u02DC",  # SMALL TILDE
    u"\x99": u"\u2122",  # TRADE MARK SIGN
    u"\x9A": u"\u0161",  # LATIN SMALL LETTER S WITH CARON
    u"\x9B": u"\u203A",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    u"\x9C": u"\u0153",  # LATIN SMALL LIGATURE OE
    u"\x9E": u"\u017E",  # LATIN SMALL LETTER Z WITH CARON
    u"\x9F": u"\u0178",  # LATIN CAPITAL LETTER Y WITH DIAERESIS
}


def kill_gremlins(text):
    if re.search(u"[\x80-\x9f]", text):
        def fixup(m):
            ss = m.group(0)
            return cp1252.get(ss, ss)
        text = re.sub(u"[\x80-\x9f]", fixup, text)
    return text


url_base = domain_base + uri_base

if search_type not in ('index', 'url'):
    search_urls = None
else:
    search_urls = sys.argv[2].split(',')
    search_urls = [url_base + v if url_base not in v else v for v in search_urls]

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor(cursor_factory=RealDictCursor)


last_request = None
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36",
    "agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36",
    "content-type": "application/json; charset=UTF-8",
    "accept": "application/json, text/javascript, */*; q=0.01",
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://tvtropes.org',
    "referer": "https://tvtropes.org/pmwiki/browse.php",
    'authority': 'tvtropes.org',
    'x-requested-with': 'XMLHttpRequest'
}
session = requests.Session()
session.headers.update(headers)


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

    txt = session.get(href).text

    last_request = datetime.now()

    return txt


def clean_soup(soup):
    for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
        script.extract()
    for x in soup.find_all(text=lambda text: isinstance(text, Comment)):
        x.extract()
    return soup


def soupify(d, li, loop=False):
    soup = clean_soup(BeautifulSoup(d, 'lxml', parse_only=strainer))
    trope_list = soup.select('ul a[title^="https://"], ul a[title^="/pmwiki"], ol a[title^="https://"], ol a[title^="/pmwiki"]')
    for t in trope_list:
        href = t.get('href')
        if atoz.search(href):
            if not loop:
                print('=> Found new link: ' + href)
                if domain_base not in href:
                    href = domain_base + href
                hrefdata = wait_request(href)
                soupify(hrefdata, li, True)
            else:
                print('--> Found loop, skipping ' + href)
        else:
            href = href.replace(domain_base, '').replace(uri_base, '')
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
    def __init__(self, group, title, name=None, data=None, media_id=None, key=None):
        self.group = group
        self.title = title
        self.name = name
        self.data = data
        self.media_id = media_id
        self.key = key

    def get_link(self):
        return '{}/{}'.format(self.group, self.title)

    def get_url(self):
        return url_base + self.get_link()

    def __str__(self):
        return self.get_link()

    def delete(self):
        if self.media_id:
            try:
                print('\t=> Deleting {} ({}) from database...'.format(self.get_link(), self.media_id))
                cursor.execute("""DELETE FROM media WHERE id = %s;""", (self.media_id,))
                db.commit()
            except:
                logger.error('\t=> Error with db(media): {}'.format(self.get_link()))
        else:
            logger.warning('Cannot delete entry from DB (no ID)')

    def insert_media(self):
        if self.group.lower() not in lower_wanted_groups:
            logger.warning('\tUnwanted group: {} for {}'.format(self.group, self.get_link()))
            return False

        cursor.execute("""select id, data from media where type = %s and title = %s;""", (self.group, self.title))

        if cursor.rowcount != 0:
            row_data = cursor.fetchone()
            self.media_id = row_data['id']
            self.data = row_data['data']
            return True
        else:
            print('\tInserting into media...')

            href = self.get_url()
            self.data = wait_request(href)

            return self.fix_media()  # move out?

    def fix_media(self):
        soup = clean_soup(BeautifulSoup(self.data, 'lxml'))

        if 'Unable to connect to database server' in self.data:
            logger.warning('\t=> Error, Server down: {}'.format(self.get_link()))
            return False

        if '504: Gateway time-out' in self.data:
            logger.warning('\t=> Error, 504 timeout: {}'.format(self.get_link()))
            return False

        if 'Inexact title. See the list below' in self.data:
            orig_link = self.get_link()

            print('\t=> Inexact title: {}'.format(orig_link))

            found = False
            poss_list = soup.find('div', {'id': 'main-article'}).select('ul a[href^="https://"], ul a[href^="/pmwiki"]')  # put ol here?

            for t in poss_list:
                href = t.get('href')
                group, title = get_link_data(href)
                if not (group and title):
                    logger.warning('\t=> Could not find proper group and title: {}'.format(href))
                    continue

                new_media = Media(group, title)

                inex_res = new_media.insert_media()
                if inex_res:
                    found = True

            if not found:
                logger.warning('\t=> Error, could not find correct title: {}'.format(orig_link))
                #delete?
                return False

            self.delete()

            return True

        if 'If you want to start this new page, just click the edit button above' in self.data:
            logger.warning('\t=> Error, Page does not exist: {}'.format(self.get_link()))
            return False

        changed = False

        true_type = soup.find('input', {'id': 'groupname-hidden'})
        true_title = soup.find('input', {'id': 'title-hidden'})
        true_key = soup.find('input', {'id': 'article_id'})

        if not true_type or not true_type.get('value'):
            logger.warning('\t=> Could not find true type for {}'.format(self.get_link()))
            true_type = self.group
        else:
            true_type = true_type.get('value')

        if true_type.lower() not in lower_wanted_groups:
            logger.warning('\tUnwanted group: {} for {}'.format(true_type, self.get_link()))
            self.delete()
            return False

        if true_type not in wanted_groups:
            newgroup = wanted_groups[lower_wanted_groups.index(true_type.lower())]
            print('--> Fixing group {} -> {}'.format(true_type, newgroup))
            true_type = newgroup

        if not true_title or not true_title.get('value'):
            logger.warning('\t=> Could not find true title for {}'.format(self.get_link()))
            true_title = self.title
        else:
            true_title = true_title.get('value')

        true_name = '{}/{}'.format(true_type, true_title)
        if true_name != self.get_link():
            print('\t-> Switching old {}/{} to {}/{}'.format(self.group, self.title, true_type, true_title))
            self.group = true_type
            self.title = true_title
            changed = True

            cursor.execute("""select 1 from media where type = %s and title = %s limit 1;""", (self.group, self.title))
            if cursor.rowcount != 0:
                print('\tNew name already exists, skipping...')
                self.delete()
                return False

        if not true_key or not true_key.get('value'):
            logger.warning('\t=> Could not find true key for {}'.format(self.get_link()))
            true_key = self.key
        else:
            true_key = true_key.get('value')

        if true_key != self.key:
            print('\t-> Switching old key from {} to {}'.format(self.key, true_key))
            self.key = true_key
            changed = True

        title_div = soup.find('h1', {'itemprop': 'headline'})
        if not title_div:
            logger.warning('\t=> Error, could not find name: {}'.format(self.get_link()))
        else:
            media_name_split = [x.strip() for x in title_div.text.split('/')]
            if not media_name_split or len(media_name_split) < 2:
                logger.warning('\t=> Error, could not find name ({}) for: {}'.format(media_name_split, self.get_link()))

            media_name_spl = [media_name_split[0], '/'.join(media_name_split[1:])]
            media_name_fetch = kill_gremlins(media_name_spl[1])

            if not media_name_spl or len(media_name_spl) != 2:
                logger.warning('\t=> Error, could not find name ({}) for: {}'.format(media_name_spl, self.get_link()))
            elif self.name != media_name_fetch:
                print('-> Changing name from {} to {}'.format(self.name, media_name_fetch))
                self.name = media_name_fetch
                changed = True

        if self.media_id:
            if not changed:
                #print('-> No changes required.')
                try:
                    cursor.execute("""UPDATE media SET valid = true WHERE id = %s;""", (self.media_id,))
                    db.commit()
                except:
                    logger.error('\t=> Error with db(media): {}'.format(self.get_link()))
                    return False
                else:
                    return True
            else:
                print('-> Updating data for {} ({})'.format(self.get_link(), self.media_id))
                try:
                    cursor.execute("""UPDATE media SET type = %s, title = %s, name = %s, key = %s, valid = true WHERE id = %s;""",
                                   (self.group, self.title, self.name, self.key, self.media_id))
                    db.commit()
                except:
                    logger.error('\t=> Error with db(media): {}'.format(self.get_link()))
                    return False
                else:
                    return True
        else:
            soup_str = kill_gremlins(str(soup))
            self.data = htmlmin.minify(soup_str, remove_empty_space=True)

            print('-> Inserting new media entry for {}'.format(self.get_link()))
            try:
                cursor.execute("""INSERT INTO media (type, title, name, data, key, valid) VALUES (%s, %s, %s, %s, %s, true) RETURNING id;""",
                               (self.group, self.title, self.name, self.data, self.key))
                db.commit()
            except:
                logger.error('\t=> Error with db(media): {}'.format(self.get_link()))
                return False
            else:
                self.media_id = cursor.fetchone()['id']
                return True

    def insert_tropes(self):
        res = self._insert_tropes()
        if res is True:
            cursor.execute("""UPDATE media SET parsed = true WHERE id = %s AND parsed is false;""", (self.media_id,))
            db.commit()

    def _insert_tropes(self):
        if not self.data:
            logger.warning('\t=> Error (tropes), missing data: {}'.format(self.get_link()))
            return False

        cursor.execute("""select 1 from troperows where media_id = %s limit 1;""", (self.media_id,))
        if cursor.rowcount != 0:
            return True

        print('\tInserting into tropes...')

        alltropes = soupify(self.data, set(), False)

        if len(alltropes) == 0:
            logger.warning('\t=> No tropes found (media_len={}): {}'.format(len(self.data), self.get_link()))
            return True

        insert_data = [(self.media_id, a.split('/')[0], a.split('/')[1]) for a in alltropes]

        try:
            cursor.executemany("""INSERT INTO troperows (media_id, trope_type, trope_name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;""", insert_data)
            db.commit()
        except:
            logger.error('\t=> Error with db(tropes): {}'.format(self.get_link()))
            return False

        return True


def create_media(href):
    group, title = get_link_data(href)

    if not (group and title):
        logger.warning('\t=> Could not find proper group and title: {}'.format(href))
        return False

    this_media = Media(group, title)

    print(this_media.get_link())

    med_ins_res = this_media.insert_media()
    if not med_ins_res:
        logger.warning('\t=> Error with media {}'.format(this_media.get_link()))
        return False

    return True


if search_type in ('index', 'url'):
    for u in search_urls:
        q = wait_request(u)
        _soup = clean_soup(BeautifulSoup(q, 'lxml'))

        if search_type == 'url':
            create_media(u)
        else:
            for s in _soup.select('ul a[title*="pmwiki/pmwiki.php"], ol a[title*="pmwiki/pmwiki.php"]'):
                shref = s.get('href')
                create_media(shref)

elif search_type == 'fix':
    with db.cursor('all_fix', cursor_factory=RealDictCursor, withhold=True) as c_fix:
        c_fix.execute("""
            select id, type, title, name, key, data from media where valid is false
            --limit 100
        ;""")

        for row in c_fix:
            _this_media = Media(row['type'], row['title'], name=row['name'], data=row['data'], media_id=row['id'], key=row['key'])

            print('{} ({})'.format(_this_media.get_link(), _this_media.media_id))

            _this_media.fix_media()

elif search_type == 'all':
    with db.cursor('all_search', cursor_factory=RealDictCursor, withhold=True) as c2:
        c2.execute("""
            select id, type, title, name, key, data from media m where parsed is false and valid is true
            --limit 20
        ;""")

        for row in c2:
            _this_media = Media(row['type'], row['title'], name=row['name'], data=row['data'], media_id=row['id'], key=row['key'])

            print('{} ({})'.format(_this_media.get_link(), _this_media.media_id))

            _this_media.insert_tropes()

        cursor.execute('''REFRESH MATERIALIZED VIEW trope_count;''')


cursor.close()
db.close()
