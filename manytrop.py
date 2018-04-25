#!/usr/bin/env python

import psycopg2
import sys

#---------------------------

min_tot_tropes = 30
min_common_tropes = 1

desired_types = []

## CHANGE
min_trope = 1
media_list = """'Anime/SwordArtOnline', 'Anime/AngelBeats'"""

#---------------------------

#min_trope = 5
#media_list = """'VideoGame/TheWalkingDead','VideoGame/TalesOfXillia','VideoGame/Portal1','VideoGame/Portal2','Series/Lost','VideoGame/Catherine','VideoGame/TheLastOfUs','VisualNovel/NineHoursNinePersonsNineDoors','Anime/CodeGeass','VideoGame/FinalFantasyX','VideoGame/ValkyriaChronicles','VideoGame/ShinMegamiTenseiIV','VideoGame/Persona3','VideoGame/Persona4','VideoGame/Persona5','Anime/TengenToppaGurrenLagann','VideoGame/BravelyDefault','Series/GameOfThrones','Manga/DeathNote','VideoGame/LostOdyssey','VideoGame/PersonaQShadowOfTheLabyrinth','VideoGame/TheWolfAmongUs','VisualNovel/VirtuesLastReward','VisualNovel/Ever17','Manga/MyHeroAcademia','VisualNovel/HigurashiWhenTheyCry','VideoGame/Xenoblade','VideoGame/XenobladeChronicles2','Anime/SwordArtOnline','Manga/HunterXHunter','Film/Passengers','Series/SpartacusBloodAndSand','VideoGame/LifeIsStrange','VisualNovel/DanganRonpa','VisualNovel/SuperDanganronpa2','VideoGame/PrinceOfPersiaTheSandsOfTime','VideoGame/SOMA','VisualNovel/ZeroTimeDilemma','VisualNovel/DokiDokiLiteratureClub','Series/Torchwood','Series/Homeland','Series/Sherlock','WesternAnimation/HowToTrainYourDragon','Manga/AttackOnTitan','Film/TheCabinInTheWoods','Series/JessicaJones2015','Series/FridayNightLights','Manga/Berserk','Literature/AngelsAndDemons','VideoGame/HorizonZeroDawn','Manga/FutureDiary','WesternAnimation/Zootopia','Series/AscensionMiniseries','Series/TheOA','Series/StrangerThings'"""

#min_trope = 2
#media_list = """'Series/ArrestedDevelopment','Series/ItsAlwaysSunnyInPhiladelphia','WesternAnimation/Archer','Series/AmericanVandal','Film/TeamAmericaWorldPolice','Series/WetHotAmericanSummerFirstDayOfCamp','Film/WetHotAmericanSummer','Series/FlightOfTheConchords'"""

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")

with db.cursor('manytrop1') as c1:
    c1.execute("""select distinct a.t v, count(1) c from (select distinct link, unnest(tropes) as t from tropelist where link in ({})) a group by 1 having count(1) >= {} order by 2 desc;""".format(media_list, min_trope))
    
    wantedset = set()
    for w in c1:
        #todo: add some preference for more counts?
        wantedset.add(w[0])

#wantedset = {'Main/WakeUpCallBoss', 'Main/AntiFrustrationFeatures', 'Main/ExactTimeToFailure', 'Main/CentralTheme', 'Main/ZigZagged', 'Main/NiceJobBreakingItHero', 'Main/AdultFear', 'Main/InfantImmortality', 'Main/Determinator', 'Main/UpToEleven', 'Main/StealthPun', 'Main/GoldenEnding', 'Main/WellIntentionedExtremist', 'Main/TheHeroDies', 'Main/SarcasmMode', 'Main/ColorCodedCharacters', 'Main/LostInTranslation', 'Main/SubvertedTrope', 'Main/Mooks', 'Main/MortonsFork', 'VideoGame/Persona3', 'Main/VillainousBreakdown', 'Main/GenreSavvy', 'Main/YouBastard', 'Main/GenreBusting', 'Main/BreakingTheFourthWall', 'Main/DoomedByCanon', 'Main/JerkWithAHeartOfGold', 'Main/JumpScare', 'Main/GreyAndGrayMorality', 'Main/AnyoneCanDie', 'Main/MetalSlime', 'Main/PassiveAggressiveKombat', 'Main/HelloInsertNameHere', 'Main/HeroicBSOD', 'Main/NonstandardGameOver', 'Main/LampshadeHanging', 'Main/HopeSpot', 'Main/PointOfNoReturn', 'Main/RedHerring', 'Main/HiddenDepths', 'Main/MythologyGag', 'Main/WordOfGod', 'Main/InfinityPlusOneSword', 'Main/BreakTheCutie', 'Main/BookEnds', 'Main/DrivenToSuicide', 'Main/BonusBoss', 'Main/DoesThisRemindYouOfAnything', 'Main/CharacterDevelopment', 'Main/MoodWhiplash', 'Main/JustifiedTrope', 'Main/Irony', 'Main/AlasPoorVillain', 'Main/ActionGirl', 'Main/WhamLine', 'Main/WhatTheHellHero', 'Main/GameplayAndStorySegregation', 'Main/WhamShot', 'Main/StupidityIsTheOnlyOption', 'Main/FourIsDeath', 'Main/WhamEpisode', 'Main/BossBattle', 'Main/BigDamnHeroes', 'Main/CallBack', 'Main/NewGamePlus', 'Main/MeaningfulName', 'Main/TheDragon', 'Main/DidYouJustPunchOutCthulhu', 'Main/ShoutOut', 'Main/InterfaceSpoiler', 'Main/GuideDangIt', 'Main/DespairEventHorizon', 'Main/BittersweetEnding', 'Main/ChekhovsGun', 'Main/HopelessBossFight', 'Main/AllThereInTheManual', 'Main/BigBad', 'Main/Foreshadowing', 'Main/HeroicSacrifice', 'Main/ArcWords'}


print '\t'.join(['TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ'])

with db.cursor('manytrop2') as c2:
    c2.execute("""select distinct link, tropes from tropelist where link not in ({});""".format(media_list))

    for row in c2:
	    link = row[0]
	    tropes = row[1]
	    
	    st = set(tropes)
	    tropeCnt = len(st)
	    simt = st & wantedset
	    similarCnt = len(simt)

	    if tropeCnt >= min_tot_tropes and similarCnt >= min_common_tropes:
		    typ,nam = link.split('/')
		    
		    if not desired_types or typ in desired_types:
		        pct = round(similarCnt * 1.0 / tropeCnt, 3)
		        adj = round((similarCnt**2) * 1.0 / tropeCnt, 3)
		        
		        print '\t'.join([typ, nam, str(tropeCnt), str(similarCnt), str(pct), str(adj)])
		
