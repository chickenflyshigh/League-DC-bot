import requests
import json
import os
import datetime
from dateutil import tz
import time
from datetime import date
import pandas as pd
from Data2.data import champ_id_df
from Data2.keys import api_key

def summoner_info(name,apikey=api_key):
    URL = f"https://oc1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={apikey}"
    summoner_info = requests.get(URL)
    summoner_info.encoding = summoner_info.apparent_encoding
    return summoner_info.json()

## For the past matches
def match_ids(name,apikey=api_key, no_match=10):
    puuid = summoner_info(name)['puuid']
    URL = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={no_match}&api_key={apikey}"
    matches = requests.get(URL).json()
    #https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/16Fxl-5TmzJTXY_5uHO4PJtRyq6KYq3spMoa3sDQOv0mETFekeAZGrQboThzRxTmtbiW3BrhzQxzHw/ids?start=0&count=100&api_key=RGAPI-f59d115f-a307-4c10-b5a6-4cce954dd6dc
    return matches

def match(match_no,apikey=api_key):
    URL = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_no}?api_key={apikey}"
    match_info = requests.get(URL)
    match_info.encoding = match_info.apparent_encoding
    return match_info.json()

def match_ids_v4(name, apikey=api_key):
    account_id = summoner_info(name)['accountId']
    URL = f'https://oc1.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?api_key={apikey}'
    matches = requests.get(URL).json()
    return matches


def match_v4(game_id, apikey= api_key):
    URL = f'https://oc1.api.riotgames.com/lol/match/v4/matches/{game_id}?api_key={apikey}'
    match_info = requests.get(URL)
    match_info.encoding = match_info.apparent_encoding
    return match_info.json()

def past_matches(name, no_of_matches =10):
    list_of_matches = []
    all_match_ids = match_ids(name, no_match = no_of_matches)
    for mat in all_match_ids:
        list_of_matches.append(match(mat)['info']['participants'])
    return list_of_matches

def in_game(name,apikey=api_key):
    id = summoner_info(name)['id']
    URL = f"https://oc1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{id}?api_key={apikey}"
    in_game_info = requests.get(URL)
    in_game_info.encoding = in_game_info.apparent_encoding
    return in_game_info.json()

def now_time():
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')
    unix_to_utc = lambda date: datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    utc_to_aest =lambda utcdate: datetime.datetime.strptime(utcdate, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
    curr_time = unix_to_utc(time.time())
    curr_time = utc_to_aest(curr_time)
    return curr_time

def unix_to_utc(date):
    return datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

def utc_to_aest(utcdate):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')
    return datetime.datetime.strptime(utcdate, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)

def free_rotation(apikey = api_key):
    URL = f'https://oc1.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={apikey}'
    rotation_info = requests.get(URL)
    return rotation_info.json()

def ranked(name, apikey=api_key):
    summonerId = summoner_info(name)['id']
    URL = f'https://oc1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={apikey}'
    rank = requests.get(URL)
    return rank.json()

def champ_mastery(name, apikey=api_key):
    summoner_id = summoner_info(name)['id']
    URL = f"https://oc1.api.riotgames.com//lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}?api_key={apikey}"
    user_cm = requests.get(URL).json()
    cm = pd.read_json(json.dumps(user_cm))
    cm['lastPlayTime']= pd.to_numeric(cm['lastPlayTime'], downcast="float" )/1000

    unix_to_utc = lambda date: datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    cm['lastPlayTime']=cm['lastPlayTime'].apply(unix_to_utc)

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')
    utc_to_aest =lambda utcdate: datetime.datetime.strptime(utcdate, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
    cm['lastPlayTime']=cm['lastPlayTime'].apply(utc_to_aest)
    champ_name_id = champ_id_df.merge(cm,on='championId',how='left')
    champ_name_id = champ_name_id[champ_name_id['championLevel'] >= 1]

    return champ_name_id.set_index('champion name')

def champ_mastery_id(id, apikey=api_key):
    URL = f"https://oc1.api.riotgames.com//lol/champion-mastery/v4/champion-masteries/by-summoner/{id}?api_key={apikey}"
    user_cm = requests.get(URL).json()
    cm = pd.read_json(json.dumps(user_cm))
    cm['lastPlayTime']= pd.to_numeric(cm['lastPlayTime'], downcast="float" )/1000

    unix_to_utc = lambda date: datetime.datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    cm['lastPlayTime']=cm['lastPlayTime'].apply(unix_to_utc)

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')
    utc_to_aest =lambda utcdate: datetime.datetime.strptime(utcdate, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
    cm['lastPlayTime']=cm['lastPlayTime'].apply(utc_to_aest)
    champ_name_id = champ_id_df.merge(cm,on='championId',how='left')
    champ_name_id = champ_name_id[champ_name_id['championLevel'] >= 1]

    return champ_name_id.set_index('champion name')

if __name__ == '__main__':
    print(champ_mastery('smelly cows'))
