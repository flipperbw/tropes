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
def load_prev():
    with open(trope_filename, "rb") as o:
        while True:
            try:
                yield pickle.load(o)
            except EOFError:
                break

prev_pickle = list(load_prev())
prev_pickle_names = [x['name'] for x in prev_pickle]

# -------

#selected_namespaces = [
#    "Animation", "Anime", "AudioPlay", "ComicBook", "ComicStrip", "Film", "Franchise", "LetsPlay", "LightNovel", "Literature", "Machinima", "Manga", "Manhua", "Manhwa",
#    "Music", "Podcast", "Radio", "Series", "Theatre", "VideoGame", "VisualNovel", "WebAnimation", "Webcomic", "WebOriginal", "WebVideo", "WesternAnimation"
#]

#selected_namespaces = ["Music", "Radio"]
# disney?
selected_namespaces = [
   "Animation", "Anime", "AudioPlay", "ComicBook", "ComicStrip", "Film", "Franchise", "LetsPlay", "LightNovel", "Literature", "Machinima", "Manga", "Manhua", "Manhwa",
   "Podcast", "Series", "Theatre", "VideoGame", "VisualNovel", "WebAnimation", "Webcomic", "WebOriginal", "WebVideo", "WesternAnimation"
]

lower_selected_namespaces = [x.lower() for x in selected_namespaces]


minPageNum = 1
maxPageNum = 0

#todo why are the below returning blank? go one at a time and find the broken ones?

# 564
# "Series",
# {'group': 'WesternAnimation', 'title': 'HeManAndTheMastersOfTheUniverse1983', 'name': 'He Man And The Masters Of The Universe 1983', 'key': '442200'}
# {'group': 'WesternAnimation', 'title': 'HeManAndTheMastersOfTheUniverse2002', 'name': 'He Man And The Masters Of The Universe 2002', 'key': '442203'}
# {'group': 'ComicBook', 'title': 'HeManThundercats', 'name': 'He Man Thundercats', 'key': '576300'}
# ---
# {'group': 'Manga', 'title': 'HentaiKamen', 'name': 'Hentai Kamen', 'key': '305494'}
# {'group': 'Manga', 'title': 'HenZemi', 'name': 'Hen Zemi', 'key': '501346'}
# {'group': 'VideoGame', 'title': 'HEPH', 'name': 'HEPH', 'key': '765499'}

# 1229
# "WebAnimation"
# {'group': 'VideoGame', 'title': 'SuperMarioBrosDimensions', 'name': 'Super Mario Bros Dimensions', 'key': '601662'}
# {'group': 'WebAnimation', 'title': 'SuperMarioBrosDX', 'name': 'Super Mario Bros DX', 'key': '818133'}
# {'group': 'WebAnimation', 'title': 'SuperMarioBrosHeroesOfTheStars', 'name': 'Super Mario Bros Heroes Of The Stars', 'key': '599059'}
# ---
# {'group': 'Series', 'title': 'SupermarketSweep', 'name': 'Supermarket Sweep', 'key': '455411'}
# {'group': 'VideoGame', 'title': 'SuperMash', 'name': 'Super Mash', 'key': '789435'}
# {'group': 'Webcomic', 'title': 'SupermassiveBlackHoleAStar', 'name': 'Supermassive Black Hole A Star', 'key': '343978'}

# -------

empty = 0
stored: list = []
with open(trope_filename, 'ab') as f:
    pageNum = minPageNum
    while empty == 0:
        print(pageNum)
        if 0 < maxPageNum <= pageNum:
            logger.warning('Max page hit ({})'.format(maxPageNum))
            break

        data = json.dumps({"selected_namespaces": selected_namespaces, "page": pageNum, "sort": "A", "randomize": 0, 'has_image': 0})
        q = session.post("https://tvtropes.org/ajax/browse.api.php", data=data)

        if not q.text:
            logger.error(f'Empty response [{pageNum}]')
            pageNum += 1
            continue

        try:
            qj = q.json()
        except Exception as e:
            logger.error(f'problem pulling: [{pageNum}] | [{q.text}]')
            logger.error(e)
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
