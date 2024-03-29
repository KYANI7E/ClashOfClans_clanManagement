from copy import copy
from tkinter.messagebox import askyesno
import dragon
import scriv
import os
import json
import sys
import copy
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(filename="clash.log", level=logging.INFO, format="%(asctime)s :: %(name)s :: %(message)s")

# logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


if len(sys.argv) > 1:
    sys.excepthook = handle_unhandled_exception

loadAllPlayerGold = 'none'
print("Start")
try:
    logging.info("Started :-------------------------------------")
    for arg in sys.argv:
        if arg == '-m':
            logging.info("Param Loaded : Mannuel")
        if arg == '-a':
            logging.info("Param Loaded : Automatic")
        if arg == '-ag':
            logging.info("Param Loaded : All gold")
            loadAllPlayerGold = "all"
        if arg == '-cg':
            logging.info("Param Loaded : All gold in clan")
            loadAllPlayerGold = "inClan"
        if arg == '-ng':
            logging.info("Param Loaded : No Gold")
            loadAllPlayerGold = "none"
    configPath = "\\".join(sys.argv[0].split("\\")[:-1])
    with open(configPath + '\config.json', 'r') as myfile:
        data=myfile.read()
    config = json.loads(data)
    clanTag = config['clanTag']
    tokens = config['keys']
    file = configPath + '\\' + config['file']
    tags = config['tags']
except:
    logging.info("Started :-------------------------------------")
    for arg in sys.argv:
        if arg == '-m':
            logging.info("Param Loaded : Mannuel")
        if arg == '-a':
            logging.info("Param Loaded : Automatic")
        if arg == '-ag':
            logging.info("Param Loaded : All gold")
            loadAllPlayerGold = "all"
        if arg == '-cg':
            logging.info("Param Loaded : All gold in clan")
            loadAllPlayerGold = "inClan"
        if arg == '-ng':
            logging.info("Param Loaded : No Gold")
            loadAllPlayerGold = "none"
    with open('config.json', 'r') as myfile:
        data=myfile.read()
    config = json.loads(data)
    clanTag = config['clanTag']
    tokens = config['keys']
    file = config['file']
    tags = config['tags']
    
clanTagS = clanTag
clanTag = clanTag.replace("#", "%23")

statusCode = None
statusCodeW = None
statusCodeR = None

for t in tokens:
    drago = dragon.Dragon(t, clanTag)
    (clanData, statusCode) = drago.getClanInfo(clanTag)
    (warData, statusCodeW) = drago.getClanWarInfo(clanTag)
    (raidData, statusCodeR) = drago.getClanRaids(clanTag)
    if statusCode == 200:
        break
    



flag = False
if not statusCode == 200:
    print("Could not fetch clan data")
    print(clanData)
    logging.critical("Could not fetch clan data. status Code {}".format(statusCode))
    logging.critical(clanData)
    flag = True
    
if not statusCodeW == 200:
    print("Could not fetch war data")
    print(warData)
    logging.critical("Could not fetch war data. Status Code {}".format(statusCodeW))
    logging.critical(warData)
    flag = True

if not statusCodeR == 200:
    print("Could not fetch raid data")
    print(raidData)
    logging.critical("Could not fetch raid data. Status Code {}".format(statusCodeR))
    logging.critical(raidData)
    flag = True

if flag:
    logging.critical("Exiting script")
    print("Exiting script")
    exit()

clanDataRaid = copy.deepcopy(clanData)
clanDataWar = copy.deepcopy(clanData)

if not warData["state"] == "notInWar":
    war = scriv.Scriv(file, tags)
    war.setUpMembers(clanDataWar)

    war.setUpWarColumnHeaders(2, 3, 4, 5, 6, 7, 5)
    war.setUpWar(warData)
    war.updateWarSheet(config['warAttacks'], config['stars'], config['warTotal'])
    war.saveFile(file)
else:
    logging.critical("Not in war - checking if in clan league")
    print("Not in war - checking if in clan league")

    statusCodeL = None
    for t in tokens:
        if not statusCodeL == 200:
            (leagueData, statusCodeL) = drago.getClanLeagueInfo(clanTag)
        else:
            break
    
    if 'reason' in leagueData:
        logging.critical("Not in clan league")
        print("Not in clan league")
    else:

        season = leagueData['season']

        leagueWarsData = []

        for rounds in tqdm(leagueData['rounds']):
            if rounds['warTags'][0] == '#0':
                continue
            for warTags in rounds['warTags']:
                (leagueWar, statusCodeL) = drago.getClanLeagueWarInfo(warTags.replace("#", "%23"))
                if leagueWar['clan']['tag'] == clanTagS or leagueWar['opponent']['tag'] == clanTagS:
                    leagueWarsData.append(leagueWar)
                    break

        war = scriv.Scriv(file, tags)
        war.setUpMembers(clanDataWar)

        war.setUpLeagueColumnHeaders(2, 3, 4, 5, 6, 4)
        war.setUpLeague(leagueWarsData, season)
        war.updateLeagueSheet(config['leagueTotal'], config['leagueAttacks'], config['leagueStars'])
        war.saveFile(file)




raid = scriv.Scriv(file, tags)
raid.setUpMembers(clanDataRaid)

raid.setUpRaidColumnHeaders(1,2,3,4,5,6,7,8,9,10,11,5,6,8)
raid.setUpRaids(raidData)
raid.addPlayerTotalGold(drago, loadAllPlayerGold)
raid.updateRiadsSheet(config['gold'], config['raidAttacks'], config['donations'], config['raidTotal'], config['totalContributionThreshold'])
raid.saveFile(file)

logging.info("Exited")
