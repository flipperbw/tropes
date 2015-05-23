#!/usr/local/bin/python2.7

import psycopg2
import re
import time
import requests
from bs4 import BeautifulSoup

atoz = re.compile('Tropes.To.$')

def soupify(d, loop=False):
    soup = BeautifulSoup(d)
    tropeList = soup.select('ul a[title^="http://"]')
    for t in tropeList:
        href = t.get('href')
        if atoz.search(href):
			if not loop:
				print '=> Found new link: ' + href
				hrefdata = requests.get(href).text
				time.sleep(1)
				soupify(hrefdata, True)
			else:
				print 'Found loop, skipping ' + href
        else:
            href = href.replace('http://tvtropes.org/pmwiki/pmwiki.php/', '')
            alltropes.append(href)


db = psycopg2.connect(host="localhost", user="postgres", password="", database="tropes")
cursor = db.cursor()

#cursor.execute("""select * from media;""")
cursor.execute("""select * from media where link in ('WesternAnimation/ScoobyDooMysteryIncorporated', 'Manga/Berserk', 'VideoGame/TheLastOfUs', 'Literature/ASongOfIceAndFire', 'Series/Angel', 'Manga/DragonBall', 'VideoGame/MassEffect2', 'Literature/TheWheelOfTime', 'WesternAnimation/TotalDrama', 'Literature/TheLordOfTheRings', 'Series/DoctorWho', 'VideoGame/DarkSouls', 'VideoGame/StarWarsTheOldRepublic', 'VideoGame/MassEffect3', 'Manga/Bleach', 'Series/Supernatural', 'WesternAnimation/JusticeLeague', 'WesternAnimation/EdEddNEddy', 'WesternAnimation/KimPossible', 'Series/TheWalkingDead', 'WebVideo/TheNostalgiaCritic', 'Series/Arrow', 'Manga/AttackOnTitan', 'VideoGame/DissidiaFinalFantasy', 'Webcomic/QuestionableContent', 'VideoGame/Borderlands2', 'Series/PersonOfInterest', 'VideoGame/DragonAgeOrigins', 'WesternAnimation/AmericanDad', 'WebAnimation/DeathBattle', 'Series/Seinfeld', 'WesternAnimation/HeyArnold', 'WesternAnimation/TheSimpsons', 'WesternAnimation/TransformersPrime', 'VideoGame/DiabloIII', 'Series/BurnNotice', 'Literature/TheDresdenFiles', 'Series/TheBigBangTheory', 'VideoGame/FalloutNewVegas', 'Manga/Beelzebub', 'Series/GameOfThrones', 'Manga/OnePiece', 'Series/Castle', 'Series/EverybodyLovesRaymond', 'WesternAnimation/Megamind', 'Series/Friends', 'WesternAnimation/MyLittlePonyFriendshipIsMagic', 'WebVideo/DragonBallZAbridged', 'Manga/HayateTheCombatButler', 'Videogame/BioShockInfinite', 'Series/OnceUponATime', 'Manga/FairyTail', 'WesternAnimation/Wakfu', 'Franchise/ScoobyDoo', 'VideoGame/WorldOfWarcraft', 'WesternAnimation/SpongeBobSquarePants', 'Series/Heroes', 'Franchise/Pokemon', 'WesternAnimation/DannyPhantom', 'WebAnimation/ZeroPunctuation', 'VideoGame/Minecraft', 'WebVideo/AtopTheFourthWall', 'WesternAnimation/YoungJustice', 'VideoGame/X', 'Series/Leverage', 'Series/StarTrekDeepSpaceNine', 'WebVideo/YuGiOhTheAbridgedSeries', 'Series/TopGear', 'WesternAnimation/TheLegendOfKorra', 'VideoGame/NeverwinterNights2', 'WesternAnimation/DanVs', 'Series/BuffyTheVampireSlayer', 'WesternAnimation/PhineasAndFerb', 'WesternAnimation/FamilyGuy', 'WesternAnimation/StarWarsTheCloneWars', 'VideoGame/TheElderScrollsVSkyrim', 'WesternAnimation/RegularShow', 'WesternAnimation/ThePowerpuffGirls', 'Webcomic/GirlGenius', 'WesternAnimation/TomAndJerry', 'Series/Farscape', 'Series/ICarly', 'WesternAnimation/SouthPark', 'Manga/MahouSenseiNegima', 'Series/BabylonFive', 'Webcomic/TheOrderOfTheStick', 'Literature/Animorphs', 'VideoGame/TeamFortress2', 'WesternAnimation/ThunderCats2011', 'WebVideo/TheCinemaSnob', 'Literature/HonorHarrington', 'Webcomic/Homestuck', 'WebVideo/TheNostalgiaChick', 'Manga/FistOfTheNorthStar', 'VideoGame/RuneScape', 'Manga/FullmetalAlchemist', 'Series/Merlin', 'VideoGame/Earthbound', 'Franchise/MassEffect', 'WesternAnimation/CourageTheCowardlyDog', 'Webcomic/ElGoonishShive', 'WesternAnimation/Futurama', 'WesternAnimation/AvatarTheLastAirbender', 'WebVideo/TheAngryVideoGameNerd', 'WesternAnimation/TheFairlyOddParents', 'Series/Monk', 'WesternAnimation/AdventureTime', 'WesternAnimation/AvengersEarthsMightiestHeroes', 'LightNovel/HaruhiSuzumiya', 'Series/WhoseLineIsItAnyway');""")

results = cursor.fetchall()
for row in results:
    link = row[0]
    data = row[1]

    print link

    alltropes = []
    
    soupify(data)

    print alltropes
    
    cursor.execute("""select 1 from tropelist where link = %s;""", (link,))
    if cursor.rowcount != 0:
        pass
    else:
        try:
            cursor.execute("""INSERT INTO tropelist VALUES (%s, %s);""", (link, alltropes))
            db.commit()
        except:
            print 'Error: %s' % link

db.close()
