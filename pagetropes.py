#!/usr/bin/env python

import requests
import time
import psycopg2
import pickle
import htmlmin
import sys
# noinspection PyProtectedMember
from bs4 import BeautifulSoup, Comment
import logging


file_handler = logging.FileHandler(filename='pagetropes.log')
stdout_handler = logging.StreamHandler(sys.stdout)

file_handler.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

file_handler.setFormatter(logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


baseurl = 'https://tvtropes.org/pmwiki/pmwiki.php'

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
        print('==>: Error: {}, {}'.format(group, title))
        continue

    # if want to do fresh...
    cursor.execute("""select 1 from media where type = %s and title = %s;""", (group, title))
    if cursor.rowcount != 0:
        logger.warning('Skipping {}/{}'.format(group, title))
    else:
        link = '{}/{}/{}'.format(baseurl, group, title)
        print(link)

        try:
            htmlData = session.get(link).text
            soup = BeautifulSoup(htmlData, 'lxml')

            for script in soup(["script", "link", "style", "noscript", "img", "meta"]):
                script.extract()
            for x in soup.find_all(text=lambda text: isinstance(text, Comment)):
                x.extract()

            htmlData = htmlmin.minify(str(soup), remove_empty_space=True)
        except:
            logger.error('Error with fetching: %s' % link)
        else:
            try:
                cursor.execute("""INSERT INTO media (type, title, name, key, data) VALUES (%s, %s, %s, %s, %s);""", (group, title, name, key, htmlData))
                db.commit()
            except:
                logger.error('Error with db: %s' % link)

        time.sleep(0.34)

db.close()
