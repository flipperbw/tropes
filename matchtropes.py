#!/usr/bin/env python3

import psycopg2
import sys

db = psycopg2.connect(host="localhost", user="postgres", password="", database="tropes")
cursor = db.cursor()

tropeData = {}

cursor.execute("""select * from troperows where link = %s;""", (sys.argv[1],))
results = cursor.fetchall()
for row in results:
    link = row[0]
    tropes = row[1]

    tropeData[link] = tropes

allMatchData = {}
allMatchList = []

for k, v in tropeData.items():
    allMatchData[k] = {}
    for k2, v2 in tropeData.items():
        cursor.execute("""select 1 from matches where link = %s and match_link = %s;""", (k, k2))
        if cursor.rowcount != 0:
            pass
        else:
            if k != k2:
                test = allMatchData.get(k2, {}).get(k)
                if test:
                    similarCnt = test[2]
                    similarPct = test[3]
                    similarList = []
                else:
                    totalList = set(v + v2)
                    similarList = list(set(v) & set(v2))

                    totalCnt = len(totalList)
                    similarCnt = len(similarList)
                    similarPct = (similarCnt * 1.0 / totalCnt)

                    print(k, k2, len(v), len(v2), similarCnt, similarPct)

                allMatchData[k][k2] = (len(v), len(v2), similarCnt, similarPct)
                allMatchList.append((k, k2, len(v), len(v2), similarCnt, similarPct, similarList))

try:
    cursor.executemany("""INSERT INTO matches VALUES (%s, %s, %s, %s, %s, %s, %s);""", allMatchList)
    db.commit()
except:
    print('Error with many')

db.close()

#lookingfor = 'WebAnimation/CharlieTheUnicorn'
#top = 5
#sorted_pct = sorted(allMatchData[lookingfor].items(), key=lambda x: (x[1][3], x[1][2]), reverse=True)[0:top]
#sorted_cnt = sorted(allMatchData[lookingfor].items(), key=lambda x: (x[1][2], x[1][3]), reverse=True)[0:top]

#print sorted_pct
#print sorted_cnt

#select * from matches where link = 'WebAnimation/AngelicateAvenue' order by similar_pct desc, similar_count desc;
#select * from matches where link = 'WebAnimation/AngelicateAvenue' order by similar_count desc, similar_pct desc;
