#!/usr/local/bin/python2.7

import psycopg2
db = psycopg2.connect(host="localhost", user="postgres", password="", database="tropes")

cursor = db.cursor()
cursor.execute("""select * from tropelist;""")
results = cursor.fetchall()


#edit list and minimum tropes
#cursor.execute("""select b.v, b.c from (select distinct a.t v, count(1) c from (select distinct link,unnest(tropes) as t from tropelist where link in ('Series/ArrestedDevelopment','WesternAnimation/Archer','Series/ItsAlwaysSunnyInPhiladelphia')) a group by 1) b order by 2 desc;""")
cursor.execute("""select b.v, b.c from (select distinct a.t v, count(1) c from (select distinct link,unnest(tropes) as t from tropelist where lower(link) in ('videogame/shadowhearts', 'videogame/digitaldevilsaga', 'videogame/persona3')) a group by 1) b where b.c >= 1 order by 2 desc;""")
#cursor.execute("""select b.v, b.c from (select distinct a.t v, count(1) c from (select distinct link,unnest(tropes) as t from tropelist where link in ('VideoGame/TheWalkingDead','VideoGame/TalesOfXillia','VideoGame/Portal1','Series/Lost','VideoGame/Catherine','VideoGame/TheLastOfUs','VisualNovel/NineHoursNinePersonsNineDoors','VideoGame/NiNoKuni','Anime/CodeGeass','Series/SpartacusBloodAndSand','VideoGame/FinalFantasyX','VideoGame/ValkyriaChronicles','VideoGame/ShinMegamiTenseiIV','VideoGame/Persona4','Anime/TengenToppaGurrenLagann','VideoGame/BravelyDefault','Series/GameOfThrones','Manga/DeathNote','VideoGame/LostOdyssey','VideoGame/PersonaQShadowOfTheLabyrinth','VideoGame/Persona3','VideoGame/TheWolfAmongUs')) a group by 1) b where b.c > 3 order by 2 desc;""")
wan = cursor.fetchall()
a = [z[0] for z in wan]

#a = ['Main/ShoutOut','Main/BigBad','Main/Foreshadowing','Main/ChekhovsGun','Main/HeroicSacrifice','Main/CallBack','Main/AllThereInTheManual','Main/LampshadeHanging','Main/ActionGirl','Main/ArcWords','Main/GenreSavvy','Main/TheDragon','Main/WhamEpisode','Main/BigDamnHeroes','Main/CharacterDevelopment','Main/DoesThisRemindYouOfAnything','Main/JustifiedTrope','Main/MoodWhiplash','Main/WhamLine','Main/HeroicBSOD','Main/JerkWithAHeartOfGold','Main/RunningGag','Main/UpToEleven','Main/BreakTheCutie','Main/BrickJoke','Main/CatchPhrase','Main/ContinuityNod','Main/DeadpanSnarker','Main/GuideDangIt','Main/HiddenDepths','Main/MythologyGag','Main/OhCrap','Main/SubvertedTrope','Main/Badass','Main/BerserkButton','Main/BreakingTheFourthWall','Main/DidYouJustPunchOutCthulhu','Main/EvenEvilHasStandards','Main/Irony','Main/LargeHam','Main/PlayedForLaughs','Main/SarcasmMode','Main/TheHero','Main/AnyoneCanDie','Main/BattleOfWits','Main/BatmanGambit','Main/BilingualBonus','Main/BlatantLies','Main/DarkerAndEdgier','Main/Determinator','Main/Fanservice','Main/FridgeBrilliance','Main/HopeSpot','Main/NoodleIncident','Main/NotSoDifferent','Main/RedHerring','Main/StealthPun','Main/TheReasonYouSuckSpeech','Main/TheReveal','Main/TooDumbToLive','Main/TookALevelInBadass','Main/TrueCompanions','Main/VillainousBreakdown','Main/WellIntentionedExtremist','Main/YankTheDogsChain','Main/AwesomeButImpractical','Main/BonusBoss','Main/ButtMonkey','Main/ChekhovsSkill','Main/ClusterFBomb','Main/EarnYourHappyEnding','Main/HopelessBossFight','Main/HypocriticalHumor','Main/InfinityPlusOneSword','Main/InUniverse','Main/ItMakesSenseInContext','Main/KarmaHoudini','Main/Lampshaded','Main/MaleGaze','Main/MsFanservice','Main/PetTheDog']

wantedset = set(a)

allMatchList = []
for row in results:
	link = row[0]
	tropes = row[1]
	st = set(tropes)
	tropeCnt = len(st)
	simt = st & wantedset
	similarCnt = len(list(simt))
	allMatchList.append((link,tropeCnt,similarCnt))

print 'typ\tnam\ttot\tcnt\tpct\tadj'
for a in allMatchList:
	#if a[1] > 40 and a[2] > 4:
	if a[1] > 0 and a[2] > 0:
		typ,nam = a[0].split('/')
		if typ.startswith('Video'):
			pct = (a[2] * 1.0 / a[1])
			adj = ((a[2]**2) * 1.0 / a[1])
			print '\t'.join([typ, nam, str(a[1]), str(a[2]), str(pct), str(adj)])
