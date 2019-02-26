#!/usr/bin/env python3

import psycopg2
from tabulate import tabulate

#---------------------------

min_tot_tropes = 100
min_common_tropes = 2

results_amt = 100

pct_exp = 0.5  # lower is more punishing
sim_exp = 2.2  # lower is more punishing
tro_exp = 1.2  # higher is more punishing

desired_types = ('VideoGame',)
ignored_types = ('Music',)

## -------- CHANGE ---------

#min_trope = 2
#media_list = ('WesternAnimation/HowToTrainYourDragon', 'WesternAnimation/Brave', 'Disney/Moana', 'WesternAnimation/FindingNemo', 'WesternAnimation/FindingNemo', 'WesternAnimation/InsideOut', 'WesternAnimation/WallE')

#min_trope = 1
#media_list = ('Series/ArrestedDevelopment', 'WesternAnimation/Archer', 'Series/AmericanVandal', 'Film/TeamAmericaWorldPolice', 'Series/WetHotAmericanSummerFirstDayOfCamp', 'Film/WetHotAmericanSummer', 'Music/FlightOfTheConchords')

min_trope = 2
media_list = ('VideoGame/TheWalkingDead', 'VideoGame/TalesOfXillia', 'VideoGame/Portal1', 'VideoGame/Portal2', 'Series/Lost', 'VideoGame/Catherine', 'VideoGame/TheLastOfUs', 'VisualNovel/NineHoursNinePersonsNineDoors', 'Anime/CodeGeass', 'VideoGame/FinalFantasyX', 'VideoGame/ValkyriaChronicles', 'VideoGame/ShinMegamiTenseiIV', 'VideoGame/Persona3', 'VideoGame/Persona4', 'VideoGame/Persona5', 'Anime/TengenToppaGurrenLagann', 'VideoGame/BravelyDefault', 'Series/GameOfThrones', 'Manga/DeathNote', 'VideoGame/PersonaQShadowOfTheLabyrinth', 'VideoGame/TheWolfAmongUs', 'VisualNovel/VirtuesLastReward', 'VisualNovel/Ever17', 'Manga/MyHeroAcademia', 'VisualNovel/HigurashiWhenTheyCry', 'VideoGame/Xenoblade', 'VideoGame/XenobladeChronicles2', 'LightNovel/SwordArtOnline', 'Manga/HunterXHunter', 'Film/Passengers2016', 'Series/SpartacusBloodAndSand', 'VideoGame/LifeIsStrange', 'VisualNovel/DanganRonpa', 'VisualNovel/SuperDanganRonpa2', 'VideoGame/PrinceOfPersiaTheSandsOfTime', 'VideoGame/SOMA', 'VisualNovel/ZeroTimeDilemma', 'VisualNovel/DokiDokiLiteratureClub', 'Series/Torchwood', 'Series/Homeland', 'Series/Sherlock', 'WesternAnimation/HowToTrainYourDragon', 'Manga/AttackOnTitan', 'Film/TheCabinInTheWoods', 'Series/JessicaJones2015', 'Series/FridayNightLights', 'Manga/Berserk', 'Literature/AngelsAndDemons', 'VideoGame/HorizonZeroDawn', 'Manga/FutureDiary', 'Disney/Zootopia', 'Series/AscensionMiniseries', 'Series/TheOA', 'Series/StrangerThings')


#wantedset = None
wantedset = {'Main/WakeUpCallBoss', 'Main/AntiFrustrationFeatures', 'Main/ExactTimeToFailure', 'Main/CentralTheme', 'Main/ZigZagged', 'Main/NiceJobBreakingItHero', 'Main/AdultFear', 'Main/InfantImmortality', 'Main/Determinator', 'Main/UpToEleven', 'Main/StealthPun', 'Main/GoldenEnding', 'Main/WellIntentionedExtremist', 'Main/TheHeroDies', 'Main/SarcasmMode', 'Main/ColorCodedCharacters', 'Main/LostInTranslation', 'Main/SubvertedTrope', 'Main/Mooks', 'Main/MortonsFork', 'VideoGame/Persona3', 'Main/VillainousBreakdown', 'Main/GenreSavvy', 'Main/YouBastard', 'Main/GenreBusting', 'Main/BreakingTheFourthWall', 'Main/DoomedByCanon', 'Main/JerkWithAHeartOfGold', 'Main/JumpScare', 'Main/GreyAndGrayMorality', 'Main/AnyoneCanDie', 'Main/MetalSlime', 'Main/PassiveAggressiveKombat', 'Main/HelloInsertNameHere', 'Main/HeroicBSOD', 'Main/NonstandardGameOver', 'Main/LampshadeHanging', 'Main/HopeSpot', 'Main/PointOfNoReturn', 'Main/RedHerring', 'Main/HiddenDepths', 'Main/MythologyGag', 'Main/WordOfGod', 'Main/InfinityPlusOneSword', 'Main/BreakTheCutie', 'Main/BookEnds', 'Main/DrivenToSuicide', 'Main/BonusBoss', 'Main/DoesThisRemindYouOfAnything', 'Main/CharacterDevelopment', 'Main/MoodWhiplash', 'Main/JustifiedTrope', 'Main/Irony', 'Main/AlasPoorVillain', 'Main/ActionGirl', 'Main/WhamLine', 'Main/WhatTheHellHero', 'Main/GameplayAndStorySegregation', 'Main/WhamShot', 'Main/StupidityIsTheOnlyOption', 'Main/FourIsDeath', 'Main/WhamEpisode', 'Main/BossBattle', 'Main/BigDamnHeroes', 'Main/CallBack', 'Main/NewGamePlus', 'Main/MeaningfulName', 'Main/TheDragon', 'Main/DidYouJustPunchOutCthulhu', 'Main/ShoutOut', 'Main/InterfaceSpoiler', 'Main/GuideDangIt', 'Main/DespairEventHorizon', 'Main/BittersweetEnding', 'Main/ChekhovsGun', 'Main/HopelessBossFight', 'Main/AllThereInTheManual', 'Main/BigBad', 'Main/Foreshadowing', 'Main/HeroicSacrifice', 'Main/ArcWords'}

#---------------------------

db = psycopg2.connect(host="localhost", user="brett", password="", database="tropes")
cursor = db.cursor()

if not wantedset:
    wanted_query = """
     select trope_type || '/' || trope_name, count(1)
     from troperows t join media m on t.media_id = m.id
     where m.type || '/' || m.name in %s
     group by 1 having count(1) >= %s;
    """

    cursor.execute(wanted_query, (media_list, min_trope))

    wantedset = {w[0] for w in cursor}
    #print(wantedset)

    # todo: prefer ones with higher counts

if desired_types:
    media_type_limiter = 'm.type in %s'
    media_type_list = desired_types
elif ignored_types:
    media_type_limiter = 'm.type not in %s'
    media_type_list = ignored_types
else:
    media_type_limiter = '1 = %s'
    media_type_list = 1

pct_query = """
with a as (
  select count(1)*1.0 c from media m {}
)
select c.tr, c.sumcnt / a.c as pct from (
  select b.trope_type || '/' || b.trope_name as tr, sum(cnt) as sumcnt
  from trope_count b
  {}
  group by 1
) c, a
;""".format('where ' + media_type_limiter, 'where ' + media_type_limiter.replace('m.type', 'b.media_type'))

cursor.execute(pct_query, (media_type_list, media_type_list))
trope_data = {row[0]: 1.0 - float(row[1])**pct_exp for row in cursor}

trope_query = """
select m.type, m.name, array_agg(trope_type || '/' || trope_name)
 from troperows t join media m on t.media_id = m.id
 where m.type  || '/' || m.title not in %s
 {}
 group by 1,2 having array_length(array_agg(trope_type || '/' || trope_name), 1) >= %s;
""".format('and ' + media_type_limiter)

cursor.execute(trope_query, (media_list, media_type_list, min_tot_tropes))


def get_adj(sim, tro):
    return round((sim**sim_exp) * 1.0 / (tro**tro_exp), 3)  # tropeCnt**1.4


print_list = []
for row in cursor:
    typ = row[0]
    nam = row[1]
    st = set(row[2])

    tropeCnt = len(st)
    simt = st & wantedset
    similarCnt = len(simt)

    if similarCnt >= min_common_tropes:
        pct = round(similarCnt * 1.0 / tropeCnt, 3)
        adj = get_adj(similarCnt, tropeCnt)

        simCntAdj = sum([trope_data[s] for s in simt])  # error check if not exists
        adjPct = get_adj(simCntAdj, tropeCnt)

        p_list = [typ, nam, tropeCnt, similarCnt, pct, adj, adjPct]
        print_list.append(p_list)

# adj
tabulate_list = sorted(print_list, key=lambda x: x[6], reverse=True)[:results_amt]
tabulate_list = [[tabulate_list.index(x) + 1] + x for x in tabulate_list]
print(tabulate(tabulate_list, headers=['#', 'TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2']))

# pct
tabulate_list = sorted(print_list, key=lambda x: x[5], reverse=True)[:results_amt]
tabulate_list = [[tabulate_list.index(x) + 1] + x for x in tabulate_list]
print(tabulate(tabulate_list, headers=['#', 'TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2']))

# sim
tabulate_list = sorted(print_list, key=lambda x: x[4], reverse=True)[:results_amt]
tabulate_list = [[tabulate_list.index(x) + 1] + x for x in tabulate_list]
print(tabulate(tabulate_list, headers=['#', 'TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2']))

db.close()
