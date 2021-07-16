from mainfiles import get
from Data2.keys import api_key
import time
from datetime import date
import requests
import os
import datetime

class_of_leaguers = [] #the corresponding objects of the summoners
names_of_leaguers = [] #names of summoners tracked
reset_time = 3 #no. of hours after midnight to reset the player stats (includes negative values); AEST time

class Summoner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.summonerid = None
        self.accountid = None
        self.puuid = None
        self.level = None
        self.wins = 0
        self.losses = 0
        self.champions = []
        self.doubleKills = 0
        self.tripleKills = 0
        self.quadraKills = 0
        self.pentaKills = 0
        self.kills = 0
        self.assists = 0
        self.deaths = 0
        self.damage = []
        self.minions = []
        self.duration = []
        self.gameid = [] #matches that are not corrupt; elements of form: (gameid, date)
        self.prev_game = None #includes corrupt matches
        self.prev_cs = None
        self.prev_duration = None

    def in_game_db(self, apikey=api_key):
        id = self.summonerid
        URL = f"https://oc1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{id}?api_key={apikey}"
        in_game_info = requests.get(URL)
        in_game_info.encoding = in_game_info.apparent_encoding
        return in_game_info.json()

    def match_ids_puuid(self, apikey=api_key, no_match=10):
        puuid = self.puuid
        URL = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={no_match}&api_key={apikey}"
        matches = requests.get(URL).json()
        return matches

    def match_ids_accid(self, apikey=api_key):
        account_id = self.accountid
        URL = f'https://oc1.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?api_key={apikey}'
        matches = requests.get(URL)
        matches.encoding = matches.apparent_encoding
        return matches.json()

    def ranked_id(self, apikey=api_key):
        summonerId = self.summonerid
        URL = f'https://oc1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={apikey}'
        rank = requests.get(URL)
        return rank.json()
        
    def initiate_v5(self): #does not give the id because we do not want to call for the summoner_info twice using the API
        first_game = True
        matches = self.match_ids_puuid(no_match = 100)
        if len(matches) != 0:
            self.prev_game = matches[0]
        for game in matches:
            match_1 = get.match(game)
            ## Finding whether or not the game was played today. We want to convert the unix time to AEST time
            if 'metadata' in match_1.keys(): #we check for this to ensure there is no error
                time_0 = float(match_1['info']['gameCreation'])/1000
                time_0 = get.unix_to_utc(time_0)
                time_0 = get.utc_to_aest(time_0)
                game_playdate = (time_0 - datetime.timedelta(hours=reset_time)).date()
                if game_playdate == (get.now_time()-datetime.timedelta(hours=reset_time)).date():
                    self.gameid = [(match_1['metadata']['matchId'], game_playdate)] + self.gameid
                    players_in_game = match_1['info']['participants']
                    for player in players_in_game:
                        if player['summonerId'] == self.summonerid:
                            tot_cs = float(player['totalMinionsKilled'])+float(player['neutralMinionsKilled'])
                            self.pentaKills += player['pentaKills']
                            self.doubleKills += player['doubleKills']
                            self.tripleKills += player['tripleKills']
                            self.quadraKills += player['quadraKills']
                            self.deaths += player['deaths']
                            self.kills += player['kills']
                            self.assists += player['assists']
                            self.minions.append(tot_cs)
                            self.duration.append(float(match_1['info']['gameDuration'])/60000)
                            self.prev_duration = float(match_1['info']['gameDuration'])/60000
                            self.prev_cs = tot_cs
                            #leaguer.cs_prev_games.append(player['totalMinionsKilled']+player['totalMinionsKilled'])
                            if player['win']:
                                self.wins += 1
                            else:
                                self.losses += 1
                            break
                else:
                    break
            else:
                print(match_1['status']['message'])
                print(match_1['status']['status_code'])
                print(self.name)
                print(game)

    def update_v5(self):
        matches = self.match_ids_puuid(no_match = 10)
        current_date = (get.now_time() - datetime.timedelta(hours=reset_time)).date()
        if len(matches) == 0:
            return f'{self.name} currently has no matches available.'
        def update(games):
            for game in games:
                if game == self.prev_game:
                    return
                match_1 = get.match(game)
                if 'metadata' in match_1.keys():
                    time_0 = float(match_1['info']['gameCreation'])/1000
                    time_0 = get.unix_to_utc(time_0)
                    time_0 = get.utc_to_aest(time_0)
                    game_day = (time_0 - datetime.timedelta(hours=reset_time)).date()
                    if game_day == current_date:
                        m_id = match_1['metadata']['matchId']
                        self.gameid = [(m_id, game_day) ] + self.gameid
                        players_in_game = match_1['info']['participants']
                        for player in players_in_game:
                            if player['summonerId'] == self.summonerid:
                                tot_cs = float(player['totalMinionsKilled'])+float(player['neutralMinionsKilled'])
                                self.pentaKills += player['pentaKills']
                                self.doubleKills += player['doubleKills']
                                self.tripleKills += player['tripleKills']
                                self.quadraKills += player['quadraKills']
                                self.deaths += player['deaths']
                                self.kills += player['kills']
                                self.assists += player['assists']
                                self.minions.append(tot_cs)
                                self.duration.append(float(match_1['info']['gameDuration']/60000))
                                self.prev_duration = float(match_1['info']['gameDuration'])/60000
                                self.prev_cs = tot_cs
                                if player['win']:
                                    self.wins += 1
                                else:
                                    self.losses += 1
                                break
                        break
                else:
                    print(match_1['status']['message'])
                    print(match_1['status']['status_code'])
                    print(self.name)
                    print(game)

        if len(self.gameid) != 0:
            if current_date == self.gameid[0][1]:
                if matches[0] == self.prev_game:
                    return "nice"
                else:
                    update(matches)
                    self.prev_game = matches[0]
                    return "update with games played same day"
            else:
                self.pentaKills = 0
                self.doubleKills = 0
                self.tripleKills = 0
                self.quadraKills = 0
                self.deaths = 0
                self.kills = 0
                self.assists = 0
                self.minions = []
                self.duration = []
                self.gameid = []
                if matches[0] == self.prev_game:
                    return "nice2"
                else:
                    update(matches)
                    self.prev_game = matches[0]
                    return 'update with games played different date'
        else:
            if self.prev_game == matches[0]:
                return "nothing to do"
            else:
                update(matches)
                self.prev_game = matches[0]
                return "update without games played"

    def playtimetoday(self):
        return sum(self.duration) #in minutes

    def prev_cspm(self):
        return self.prev_cs/self.prev_duration
