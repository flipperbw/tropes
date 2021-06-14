#!/usr/bin/env python

from typing import Union

import psycopg2
from tabulate import tabulate

#---------------------------

min_tot_tropes = 50
min_common_tropes = 2

results_amt = 100

pct_exp = 0.5  # lower is more punishing
sim_exp = 2.2  # lower is more punishing
tro_exp = 1.2  # higher is more punishing

desired_types = ('Film',)
#desired_types = ('LightNovel', 'WesternAnimation', 'Manga', 'Anime', 'VisualNovel')
#desired_types: tuple = tuple()

ignored_types = ('Literature', 'Webcomic', 'ComicBook', 'Machinima', 'Theatre', 'LetsPlay')
#ignored_types: tuple = tuple()

## -------- CHANGE ---------

min_trope = 1
media_list = ('Film/PalmSprings', 'Film/HappyDeathDay', 'Film/HappyDeathDay2U', 'Series/RussianDoll')  # make edge of tomorrow higher

# - animated
# min_trope = 2
# media_list = ('WesternAnimation/HowToTrainYourDragon', 'WesternAnimation/Brave', 'WesternAnimation/Moana', 'WesternAnimation/FindingNemo', 'WesternAnimation/InsideOut', 'WesternAnimation/WallE')

# - comedy
# min_trope = 2
# media_list = ('Series/ArrestedDevelopment', 'WesternAnimation/Archer', 'Series/AmericanVandal', 'Film/TeamAmericaWorldPolice', 'Film/WetHotAmericanSummer', 'Series/ItsAlwaysSunnyInPhiladelphia', 'Film/PopstarNeverStopNeverStopping')

# - favorites
#min_trope = 2
#media_list = (
#    'VideoGame/TheWalkingDead', 'VideoGame/TalesOfXillia', 'VideoGame/Portal1', 'VideoGame/Portal2', 'Series/Lost',
#    'VideoGame/Catherine', 'VideoGame/TheLastOfUs', 'VisualNovel/NineHoursNinePersonsNineDoors', 'Anime/CodeGeass',
#    'VideoGame/FinalFantasyX', 'VideoGame/ValkyriaChronicles', 'VideoGame/ShinMegamiTenseiIV', 'VideoGame/Persona3',
#    'VideoGame/Persona4', 'VideoGame/Persona5', 'Anime/TengenToppaGurrenLagann', 'VideoGame/BravelyDefault',
#    'Series/GameOfThrones', 'Manga/DeathNote', 'VideoGame/PersonaQShadowOfTheLabyrinth', 'VideoGame/TheWolfAmongUs',
#    'VisualNovel/VirtuesLastReward', 'VisualNovel/Ever17', 'Manga/MyHeroAcademia', 'VisualNovel/HigurashiWhenTheyCry',
#    'VideoGame/XenobladeChronicles1', 'VideoGame/XenobladeChronicles2', 'LightNovel/SwordArtOnline', 'Manga/HunterXHunter',
#    'Film/Passengers2016', 'Series/SpartacusBloodAndSand', 'VideoGame/LifeIsStrange', 'VisualNovel/DanganronpaTriggerHappyHavoc',
#    'VideoGame/PrinceOfPersiaTheSandsOfTime', 'VideoGame/SOMA',
#    'VisualNovel/ZeroTimeDilemma', 'VisualNovel/DokiDokiLiteratureClub', 'Series/Torchwood', 'Series/Homeland',
#    'Series/Sherlock', 'WesternAnimation/HowToTrainYourDragon', 'Manga/AttackOnTitan', 'Film/TheCabinInTheWoods',
#    'Series/JessicaJones2015', 'Series/FridayNightLights', 'Manga/Berserk', 'Literature/AngelsAndDemons',
#    'VideoGame/HorizonZeroDawn', 'Manga/FutureDiary', 'WesternAnimation/Zootopia', 'Series/AscensionMiniseries', 'Series/TheOA',
#    'Series/StrangerThings', 'Manga/DrStone'
#)

# min_trope = 2
# media_list = (
#    'VideoGame/TheWalkingDead', 'VideoGame/TalesOfXillia', 'Series/Lost',
#    'VideoGame/Catherine', 'VideoGame/TheLastOfUs', 'VisualNovel/NineHoursNinePersonsNineDoors', 'Anime/CodeGeass',
#    'VideoGame/FinalFantasyX', 'VideoGame/ValkyriaChronicles', 'VideoGame/ShinMegamiTenseiIV', 'VideoGame/Persona3',
#    'VideoGame/Persona4', 'VideoGame/Persona5', 'Anime/TengenToppaGurrenLagann', 'VideoGame/BravelyDefault',
#    'Series/GameOfThrones', 'Manga/DeathNote',
#    'VisualNovel/VirtuesLastReward', 'VisualNovel/Ever17', 'VisualNovel/HigurashiWhenTheyCry',
#    'VideoGame/XenobladeChronicles1', 'VideoGame/XenobladeChronicles2', 'LightNovel/SwordArtOnline', 'Manga/HunterXHunter',
#    'Film/Passengers2016', 'Series/SpartacusBloodAndSand', 'VideoGame/LifeIsStrange', 'VisualNovel/DanganronpaTriggerHappyHavoc',
#    'VideoGame/PrinceOfPersiaTheSandsOfTime', 'VideoGame/SOMA',
#    'VisualNovel/DokiDokiLiteratureClub', 'Series/Homeland',
#    'Series/Sherlock', 'WesternAnimation/HowToTrainYourDragon', 'Manga/AttackOnTitan', 'Film/TheCabinInTheWoods',
#    'Series/FridayNightLights', 'Manga/Berserk', 'Literature/AngelsAndDemons',
#    'VideoGame/HorizonZeroDawn', 'Manga/FutureDiary', 'WesternAnimation/Zootopia', 'Series/AscensionMiniseries', 'Series/TheOA',
#    'Series/StrangerThings', 'Manga/DrStone'
# )


wantedset: set = set()
# wantedset = {
#     'WakeUpCallBoss', 'AntiFrustrationFeatures', 'ExactTimeToFailure', 'CentralTheme', 'ZigZagged',
#     'NiceJobBreakingItHero', 'AdultFear', 'InfantImmortality', 'Determinator', 'UpToEleven', 'StealthPun', 'GoldenEnding',
#     'WellIntentionedExtremist', 'TheHeroDies', 'SarcasmMode', 'ColorCodedCharacters', 'LostInTranslation', 'SubvertedTrope',
#     'Mooks', 'MortonsFork', 'VideoGame/Persona3', 'VillainousBreakdown', 'GenreSavvy', 'YouBastard', 'GenreBusting',
#     'BreakingTheFourthWall', 'DoomedByCanon', 'JerkWithAHeartOfGold', 'JumpScare', 'GreyAndGrayMorality', 'AnyoneCanDie',
#     'MetalSlime', 'PassiveAggressiveKombat', 'HelloInsertNameHere', 'HeroicBSOD', 'NonstandardGameOver', 'LampshadeHanging',
#     'HopeSpot', 'PointOfNoReturn', 'RedHerring', 'HiddenDepths', 'MythologyGag', 'WordOfGod', 'InfinityPlusOneSword',
#     'BreakTheCutie', 'BookEnds', 'DrivenToSuicide', 'BonusBoss', 'DoesThisRemindYouOfAnything', 'CharacterDevelopment',
#     'MoodWhiplash', 'JustifiedTrope', 'Irony', 'AlasPoorVillain', 'ActionGirl', 'WhamLine', 'WhatTheHellHero',
#     'GameplayAndStorySegregation', 'WhamShot', 'StupidityIsTheOnlyOption', 'FourIsDeath', 'WhamEpisode', 'BossBattle',
#     'BigDamnHeroes', 'CallBack', 'NewGamePlus', 'MeaningfulName', 'TheDragon', 'DidYouJustPunchOutCthulhu', 'ShoutOut',
#     'InterfaceSpoiler', 'GuideDangIt', 'DespairEventHorizon', 'BittersweetEnding', 'ChekhovsGun', 'HopelessBossFight',
#     'AllThereInTheManual', 'BigBad', 'Foreshadowing', 'HeroicSacrifice', 'ArcWords'
# }

#---------------------------


def get_adj(sim, tro):
    return round((sim ** sim_exp) * 1.0 / (tro ** tro_exp), 3)  # trope_cnt**1.4


def main():
    wantedset_adj = {'Main/' + ws for ws in wantedset if '/' not in ws}

    if not wantedset_adj:
        wanted_query = """
         select trope_type || '/' || trope_name, count(1)
         from troperows t join media m on t.media_id = m.id
         where m.type || '/' || m.title in %s
         group by 1 having count(1) >= %s;
        """

        cursor.execute(wanted_query, (media_list, min_trope))

        wantedset_adj = {w[0] for w in cursor}
        #print(wantedset_adj)

        # todo: prefer ones with higher counts

    media_type_list: Union[tuple, int]
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

    print_list = []
    for row in cursor:
        typ = row[0]
        nam = row[1]
        st = set(row[2])

        trope_cnt = len(st)
        simt = st & wantedset_adj
        similar_cnt = len(simt)

        if similar_cnt >= min_common_tropes:
            pct = round(similar_cnt * 1.0 / trope_cnt, 3)
            adj = get_adj(similar_cnt, trope_cnt)

            sim_cnt_adj = sum(trope_data[s] for s in simt)  # error check if not exists
            adj_pct = get_adj(sim_cnt_adj, trope_cnt)

            p_list = [typ, nam, trope_cnt, similar_cnt, pct, adj, adj_pct]
            print_list.append(p_list)

    # adj2
    tabulate_list = sorted(print_list, key=lambda x: x[6], reverse=True)[:results_amt]
    tabulate_list = [[tabulate_list.index(x) + 1] + x for x in tabulate_list]
    print(tabulate(tabulate_list, headers=['#', 'TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2']))

    # adj
    tabulate_list = sorted(print_list, key=lambda x: x[5], reverse=True)[:results_amt]
    tabulate_list = [[tabulate_list.index(x) + 1] + x for x in tabulate_list]
    print()
    print(tabulate(tabulate_list, headers=['#', 'TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2']))

    # pct
    tabulate_list = sorted(print_list, key=lambda x: x[4], reverse=True)[:results_amt]
    tabulate_list = [[tabulate_list.index(x) + 1] + x for x in tabulate_list]
    print()
    print(tabulate(tabulate_list, headers=['#', 'TYPE', 'NAME', 'TOT', 'SIM', 'PCT', 'ADJ', 'ADJ2']))


with psycopg2.connect(host="localhost", user="brett", password="", database="tropes") as db:
    with db.cursor() as cursor:
        main()
