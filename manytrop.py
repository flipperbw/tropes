#!/usr/bin/env python

import psycopg2
import sys

#---------------------------

min_tot_tropes = 80
min_common_tropes = 1

pct_exp = 0.5 # lower is more punishing
sim_exp = 2.2
tro_exp = 1.3

desired_types = []

## CHANGE

#min_trope = 2
#media_list = """'WesternAnimation/HowToTrainYourDragon', 'WesternAnimation/Brave', 'Disney/Moana', 'WesternAnimation/FindingNemo', 'WesternAnimation/FindingNemo', 'WesternAnimation/InsideOut', 'WesternAnimation/WallE'"""

min_trope = 8 #'VideoGame/LostOdyssey',
media_list = """'VideoGame/TheWalkingDead','VideoGame/TalesOfXillia','VideoGame/Portal1','VideoGame/Portal2','Series/Lost','VideoGame/Catherine','VideoGame/TheLastOfUs','VisualNovel/NineHoursNinePersonsNineDoors','Anime/CodeGeass','VideoGame/FinalFantasyX','VideoGame/ValkyriaChronicles','VideoGame/ShinMegamiTenseiIV','VideoGame/Persona3','VideoGame/Persona4','VideoGame/Persona5','Anime/TengenToppaGurrenLagann','VideoGame/BravelyDefault','Series/GameOfThrones','Manga/DeathNote','VideoGame/PersonaQShadowOfTheLabyrinth','VideoGame/TheWolfAmongUs','VisualNovel/VirtuesLastReward','VisualNovel/Ever17','Manga/MyHeroAcademia','VisualNovel/HigurashiWhenTheyCry','VideoGame/Xenoblade','VideoGame/XenobladeChronicles2','LightNovel/SwordArtOnline','Manga/HunterXHunter','Film/Passengers2016','Series/SpartacusBloodAndSand','VideoGame/LifeIsStrange','VisualNovel/DanganRonpa','VisualNovel/SuperDanganRonpa2','VideoGame/PrinceOfPersiaTheSandsOfTime','VideoGame/SOMA','VisualNovel/ZeroTimeDilemma','VisualNovel/DokiDokiLiteratureClub','Series/Torchwood','Series/Homeland','Series/Sherlock','WesternAnimation/HowToTrainYourDragon','Manga/AttackOnTitan','Film/TheCabinInTheWoods','Series/JessicaJones2015','Series/FridayNightLights','Manga/Berserk','Literature/AngelsAndDemons','VideoGame/HorizonZeroDawn','Manga/FutureDiary','Disney/Zootopia','Series/AscensionMiniseries','Series/TheOA','Series/StrangerThings'"""

#min_trope = 1
#media_list = """'Series/ArrestedDevelopment','WesternAnimation/Archer','Series/AmericanVandal','Film/TeamAmericaWorldPolice','Series/WetHotAmericanSummerFirstDayOfCamp','Film/WetHotAmericanSummer','Music/FlightOfTheConchords'"""

#---------------------------

if len(sys.argv) > 1:
    media_group = sys.argv[1]
else:
    media_group = None

wanted_query = """
 select trope_type || '/' || trope_name, count(1)
 from troperows
 where media_type || '/' || media_name in ({})
 group by 1 having count(1) >= {};
""".format(media_list, min_trope)

#todo: prefer ones with higher counts

pct_query = """
 with a as
   (select count(1)*1.0 c from media)
 select b.trope_type||'/'||b.trope_name as tr, b.count / a.c as pct
 from tropes b, a
"""

if media_group:
    media_group_str = """AND media_type = '{}'""".format(media_group)
else:
    media_group_str = ''

trope_query = """
 select media_type || '/' || media_name, array_agg(trope_type || '/' || trope_name)
 from troperows
 where media_type || '/' || media_name not in ({})
 {}
 group by 1 having array_length(array_agg(trope_type || '/' || trope_name),1) >= {};
""".format(media_list, media_group_str, min_tot_tropes)

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")

cursor = db.cursor()
    
cursor.execute(wanted_query)

wantedset = {w[0] for w in cursor}

#wantedset = {'Main/WakeUpCallBoss', 'Main/AntiFrustrationFeatures', 'Main/ExactTimeToFailure', 'Main/CentralTheme', 'Main/ZigZagged', 'Main/NiceJobBreakingItHero', 'Main/AdultFear', 'Main/InfantImmortality', 'Main/Determinator', 'Main/UpToEleven', 'Main/StealthPun', 'Main/GoldenEnding', 'Main/WellIntentionedExtremist', 'Main/TheHeroDies', 'Main/SarcasmMode', 'Main/ColorCodedCharacters', 'Main/LostInTranslation', 'Main/SubvertedTrope', 'Main/Mooks', 'Main/MortonsFork', 'VideoGame/Persona3', 'Main/VillainousBreakdown', 'Main/GenreSavvy', 'Main/YouBastard', 'Main/GenreBusting', 'Main/BreakingTheFourthWall', 'Main/DoomedByCanon', 'Main/JerkWithAHeartOfGold', 'Main/JumpScare', 'Main/GreyAndGrayMorality', 'Main/AnyoneCanDie', 'Main/MetalSlime', 'Main/PassiveAggressiveKombat', 'Main/HelloInsertNameHere', 'Main/HeroicBSOD', 'Main/NonstandardGameOver', 'Main/LampshadeHanging', 'Main/HopeSpot', 'Main/PointOfNoReturn', 'Main/RedHerring', 'Main/HiddenDepths', 'Main/MythologyGag', 'Main/WordOfGod', 'Main/InfinityPlusOneSword', 'Main/BreakTheCutie', 'Main/BookEnds', 'Main/DrivenToSuicide', 'Main/BonusBoss', 'Main/DoesThisRemindYouOfAnything', 'Main/CharacterDevelopment', 'Main/MoodWhiplash', 'Main/JustifiedTrope', 'Main/Irony', 'Main/AlasPoorVillain', 'Main/ActionGirl', 'Main/WhamLine', 'Main/WhatTheHellHero', 'Main/GameplayAndStorySegregation', 'Main/WhamShot', 'Main/StupidityIsTheOnlyOption', 'Main/FourIsDeath', 'Main/WhamEpisode', 'Main/BossBattle', 'Main/BigDamnHeroes', 'Main/CallBack', 'Main/NewGamePlus', 'Main/MeaningfulName', 'Main/TheDragon', 'Main/DidYouJustPunchOutCthulhu', 'Main/ShoutOut', 'Main/InterfaceSpoiler', 'Main/GuideDangIt', 'Main/DespairEventHorizon', 'Main/BittersweetEnding', 'Main/ChekhovsGun', 'Main/HopelessBossFight', 'Main/AllThereInTheManual', 'Main/BigBad', 'Main/Foreshadowing', 'Main/HeroicSacrifice', 'Main/ArcWords'}


cursor.execute(pct_query)
trope_data = {row[0]: 1.0 - float(row[1])**pct_exp for row in cursor}

def getAdj(sim, tro):
    return round((sim**sim_exp) * 1.0 / (tro**tro_exp), 3) # tropeCnt**1.4

print '\t'.join(['TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2'])

cursor.execute(trope_query)

for row in cursor:
    me = row[0]
    st = set(row[1])
    
    tropeCnt = len(st)
    simt = st & wantedset
    similarCnt = len(simt)
    
    if tropeCnt >= min_tot_tropes and similarCnt >= min_common_tropes:
	    typ,nam = me.split('/')
	    
	    if not desired_types or typ in desired_types:
	        pct = round(similarCnt * 1.0 / tropeCnt, 3)
	        adj = getAdj(similarCnt, tropeCnt)
	        
	        simCntAdj = sum([trope_data[s] for s in simt]) #error check if not exists
	        adjPct = getAdj(simCntAdj, tropeCnt)    
	        
	        print_list = [typ, nam, str(tropeCnt), str(similarCnt), str(pct), str(adj), str(adjPct)]
	        print '\t'.join(print_list)

db.close()
