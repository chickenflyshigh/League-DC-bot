import time
import os
import datetime
import discord
from discord.ext import commands, tasks
import asyncio
from mainfiles import get
from mainfiles.summoner import Summoner
from mainfiles.summoner import class_of_leaguers
from Data2.keys import channel_id
from Data2 import data

class PlayerInfo(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.last_update = time.time()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Frog is on a hunt for those leaguers.")
        await asyncio.sleep(120)
        self.addicts.start()
        await asyncio.sleep(120)
        self.update_info.start()

    @tasks.loop(minutes=2)
    async def update_info(self):
        try:
            for leaguer in class_of_leaguers:
                leaguer.update_v4()
            self.last_update = time.time()
        except Exception:
            print("Update unsuccessful :(")

    @tasks.loop(minutes=15)
    async def addicts(self):
        channel = self.client.get_channel(id = channel_id)
        games = {}
        start_time = {}
        for summoner in class_of_leaguers:
            game = summoner.in_game_db()
            if 'gameId' in game.keys():
                duration = game['gameLength']
                gameid = game['gameId']
                games[gameid] = games.get(gameid,[])+[summoner]
                start_time[summoner] = float(game['gameStartTime'])
        if len(games) != 0:
            for gameid, players in games.items():
                if len(players) > 1:
                    lplayers = players[0].name
                    for player in players[1:-1]:
                        lplayers = f'{lplayers}, {player.name}'
                    lplayers = f'{lplayers} and {players[-1].name}'
                    await channel.send(f"{lplayers} have been addicted together for {datetime.timedelta(seconds=round(time.time()-start_time[players[-1]]/1000))}.")
                else:
                    await channel.send(f"{players[0].name} has been addicted for {datetime.timedelta(seconds=round(time.time()-start_time[players[-1]]/1000))}.")
        else:
            print("No one is playing right now.")

    @commands.command(aliases=['pci'])
    async def players_currently_ingame(self, ctx):
        games = {}
        start_time = {}
        for summoner in class_of_leaguers:
            game = summoner.in_game_db()
            if 'gameId' in game.keys():
                duration = game['gameLength']
                gameid = game['gameId']
                games[gameid] = games.get(gameid,[])+[summoner]
                start_time[summoner] = float(game['gameStartTime'])
        if len(games) != 0:
            for gameid, players in games.items():
                if len(players) > 1:
                    lplayers = players[0].name
                    for player in players[1:-1]:
                        lplayers = f'{lplayers}, {player.name}'
                    lplayers = f'{lplayers} and {players[-1].name}'
                    await ctx.send(f"{lplayers} have been playing together for {datetime.timedelta(seconds=round(time.time()-start_time[players[-1]]/1000))}.")
                else:
                    await ctx.send(f"{players[0].name} has been ingame for {datetime.timedelta(seconds=round(time.time()-start_time[players[-1]]/1000))}.")
                await ctx.message.add_reaction('🐸')
        else:
            await ctx.send("OMggggg no one is ingame right now lezgoooooo")

    @commands.command()
    async def ingame(self, ctx, *, name):
        player_info = get.summoner_info(name)
        if 'name' in player_info.keys():
            player_name = player_info['name']
            game = get.in_game(name)
            id = player_info['id']
            if 'gameId' in game.keys():
                start = game['gameStartTime']
                mode = data.queue_dict[game['gameQueueConfigId']]
                players = game['participants']
                for player in players:
                    if player['summonerId'] == id:
                        champion = data.champ_dict[str(player['championId'])]
                        break
                await ctx.send(f"{player_name}\nIngame: Yes \nDuration: {datetime.timedelta(seconds=round(time.time()-start/1000))} \nGamemode: {mode} \nChampion: {champion}.")
                await ctx.message.add_reaction('🐸')
            else:
                await ctx.send(f"{player_name} is currently not playing a game.")
        else:
            await ctx.send('Please enter a valid summoner name.')

    @commands.command(aliases = ['updateall'])
    async def update(self, ctx):
        try:
            for leaguer in class_of_leaguers:
                print(leaguer.update_v4())
            self.last_update = time.time()
            await ctx.send(f"Update Successful")
            await ctx.message.add_reaction('🐸')
        except Exception:
            print("Update unsuccessful :(")
            await ctx.send(f"Update Unsuccessful :(")

    @commands.command(aliases = ['ltu'])
    async def last_time_updated(self, ctx):
        await ctx.send(f"Last Updated: {get.utc_to_aest(get.unix_to_utc(self.last_update))}")
        await ctx.message.add_reaction('🐸')

    @commands.command()
    async def rank(self, ctx, *, name):
        info = get.summoner_info(name)
        if 'name' in info.keys():
            player = Summoner(info['name'])
            player.summonerid = info['id']
            player_rank = player.ranked_id()
            if len(player_rank) == 0:
                await ctx.send(f'{player.name} is currently unranked in all queues')
            else:
                for i in range(len(player_rank)):
                    deets = player_rank[i]
                    queue = deets['queueType']
                    lp = deets['leaguePoints']
                    wins = deets['wins']
                    losses = deets['losses']
                    tier = deets['tier']
                    rank = deets['rank']
                    message = f'Player: {player.name} \nQueuetype: {queue} \nTier: {tier} \nDivision: {rank} \nLP: {lp} \nWins: {wins} \nLosses: {losses}'
                    await ctx.send(f'>>> {message}')
                    await ctx.message.add_reaction('🐸')
        else:
            await ctx.send(f'Please enter a valid summoner name')

    @commands.command(aliases = ['ci', 'stalk'])
    async def champion_info(self, ctx, *, name):
        info = get.summoner_info(name)
        if 'name' not in info.keys():
            await ctx.send('Please enter a valid summoner name')
        else:
            name = info['name']
            df = get.champ_mastery_id(info['id'])
            df.to_csv(f'{name}.csv',index = True)
            await ctx.send(file=discord.File(f'{name}.csv'))
            await ctx.message.add_reaction('🐸')
            os.remove(f'{name}.csv')

def setup(client):
    client.add_cog(PlayerInfo(client))

if __name__ == '__main__':
    print('hi')
