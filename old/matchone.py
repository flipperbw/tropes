#!/usr/bin/env python

import psycopg2
import sys

db = psycopg2.connect(host="localhost", user="postgres", password="", database="tropes")
cursor = db.cursor()

tropeData = {}

cursor.execute("""select * from tropelist;""")
results = cursor.fetchall()
for row in results:
    link = row[0]
    tropes = row[1]

    tropeData[link] = tropes

allMatchList = []

k = sys.argv[1]
v = tropeData[k]

if not v:
    print('No tropes found')
    exit(1)

cursor.execute("""select match_link from matches where link = %s;""", (k,))
prevMatches = cursor.fetchall()
preMatchList = [m[0] for m in prevMatches]

for k2, v2 in tropeData.items():
    if k2 in preMatchList:
        pass
    else:
        if k != k2 and v2:
            totalList = set(v + v2)
            similarList = list(set(v) & set(v2))

            totalCnt = len(totalList)
            similarCnt = len(similarList)
            similarPct = (similarCnt * 1.0 / len(v))
            matchPct = (similarCnt * 1.0 / len(v2))
            totalSimilarPct = (similarCnt * 1.0 / totalCnt)

            #print k, k2, len(v), len(v2), similarCnt, similarPct

            allMatchList.append((k, k2, len(v), len(v2), similarCnt, similarPct, matchPct, totalSimilarPct, similarList))

try:
    cursor.executemany("""INSERT INTO matches VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", allMatchList)
    db.commit()
except:
    print('Error inserting many')

db.close()
