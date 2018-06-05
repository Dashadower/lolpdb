# -*- coding: utf-8 -*-
# test script to check if analyzer scores work good
def pScoreForChampion(totalgames, wins, kills, assists, deaths):
    winrate_coversion = abs(float(wins)/float(totalgames) - 50.0)
    score_conversion = abs(float(kills + assists)/float(deaths) - 2.25) if deaths else 10.0
    if score_conversion < 1.0:
        score_conversion = 1.0
    return round(winrate_coversion * score_conversion, 3)


test_players = ["fundumjin"]
import riot_api_tools
for summoner in test_players:
    summonerdata = riot_api_tools.getSummonerByName(summoner)

    matches = riot_api_tools.getMatchList(summonerdata["accountId"])  # get a list of last 100 ranked solo games
    tmp_champstats = {}  # gather info(kills, assists, wins, etc) for each champion
    for match in matches:  # analyze games
        champid = match["champion"]  # get played champion ID
        if str(champid) not in tmp_champstats:  # create entity in dict if it doesnt exist
            tmp_champstats[str(champid)] = {"kills": 0.0, "assists": 0.0, "deaths": 0.0, "score": 0.0,
                                            "wins": 0.0, "totalgames": 0.0,
                                            "champname": riot_api_tools.champdata[str(champid)]["name"]}

        gdata = riot_api_tools.getMatchData(match["gameId"])  # get match game info
        if not gdata:  # failed fetch: just pass
            continue

        data = tmp_champstats[str(champid)]
        champscore = riot_api_tools.ParseScoreForSummoner(gdata,
                                                          summonerdata["id"])  # gets (kills, assists, deaths)
        data["kills"] += float(int(champscore[0]))
        data["assists"] += float(int(champscore[1]))
        data["deaths"] += float(int(champscore[2]))
        data["totalgames"] += 1.0
        if riot_api_tools.ParseWinrateForSummoner(gdata, summonerdata["id"]):  # check if game won
            data["wins"] += 1.0

    minscore = 100000000000.0
    maxscore = -100000000000.0
    for key, value in tmp_champstats.iteritems():  # python2: use iteritems
        if value["totalgames"] >= 10:  # only calculate champions with more than 10 games played
            value["score"] = pScoreForChampion(value["totalgames"], value["wins"], value["kills"], value["assists"],
                                               value["deaths"])

            minscore = min(minscore, value["score"])  # get pMax
            maxscore = max(maxscore, value["score"])  # get pMin
    print("-----------------------")
    if minscore == 100000000000.0 or maxscore == -100000000000.0:  # couldn't get useful data: abort
        print("fail")
    print("max:", maxscore, "min:", minscore)
    user_pscore = maxscore - minscore
    print(user_pscore)

