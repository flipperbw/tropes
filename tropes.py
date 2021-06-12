#!/usr/bin/env python

import json
import logging
import pickle
import requests
import sys
from time import sleep


file_handler = logging.FileHandler(filename='trope_scrape.log')
stdout_handler = logging.StreamHandler(sys.stdout)

file_handler.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

file_handler.setFormatter(logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


#selected_namespaces = [
#    "Anime", "Animation", "AudioPlay", "ComicBook", "ComicStrip", "Disney", "Film", "Franchise", "LetsPlay", "LightNovel", "Literature", "Machinima", "Manga", "Manhua", "Manhwa",
#    "Music", "Podcast", "Radio", "Series", "Theatre", "VideoGame", "VisualNovel", "WebAnimation", "Webcomic", "WebOriginal", "WebVideo", "WesternAnimation"
#]
selected_namespaces = ["Disney", "Music"]
lower_selected_namespaces = [x.lower() for x in selected_namespaces]

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

trope_filename = 'alltropes.pkl'

empty = 0
#minPageNum = 1
#minPageNum = 452
#minPageNum = 982
maxPageNum = 0
#maxPageNum = 453

minPageNum = 26

def load_prev():
    with open(trope_filename, "rb") as o:
        while True:
            try:
                yield pickle.load(o)
            except EOFError:
                break


prev_pickle = list(load_prev())
prev_pickle_names = [x['name'] for x in prev_pickle]

stored = []
with open(trope_filename, 'ab') as f:
    pageNum = minPageNum
    while empty == 0:
        print(pageNum)
        if 0 < maxPageNum <= pageNum:
            logger.warning('Max page hit ({})'.format(maxPageNum))
            break

        data = json.dumps({"selected_namespaces": selected_namespaces, "page": pageNum, "sort": "A", "randomize": 0, 'has_image': 0})
        q = session.post("https://tvtropes.org/ajax/browse.api.php", data=data)

        try:
            qj = q.json()
        except:
            logger.error(pageNum)
            logger.error(q.text)
            logger.error('problem pulling')
            sys.exit(1)

        empty = qj.get('empty')

        if empty != 0:
            logger.warning('==> empty')
            break
        else:
            res = qj.get('results')

            for k, r in res.items():
                group = r.get('groupname')
                title = r.get('title')
                name  = r.get('spaced_title')
                key   = r.get('article_id')

                if name in prev_pickle_names:
                    print('==> {} already in list'.format(name))
                    continue

                group_typo = False
                if group not in selected_namespaces and group.lower() in lower_selected_namespaces:
                    group_typo = True

                if group in selected_namespaces or group_typo:
                    if group_typo:
                        newgroup = selected_namespaces[lower_selected_namespaces.index(group.lower())]
                        print('--> Fixing group {} -> {}'.format(group, newgroup))
                        group = newgroup

                    if len([el for el in stored if el['name'].lower() == name.lower() and el['group'] == group]):
                        print(' ==> Duplicate name: {}/{}'.format(group, name))
                        continue

                    entry = {'group': group, 'title': title, 'name': name, 'key': key}
                    print(entry)
                    stored.append(entry)
                    pickle.dump(entry, f)
                else:
                    print('==> skipping: {}'.format(group))

            pageNum += 1

            sleep(1)

print('Done')

f.close()
