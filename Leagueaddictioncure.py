import time
import os
import datetime
from discord.ext import commands
from mainfiles import get
from mainfiles.summoner import Summoner, class_of_leaguers, names_of_leaguers
from Data2 import data
from Data2.keys import discord_key, session, players_file
## INITIATION. We obtain the ids for each and the level of the player. Note: haven't yet make it automatically update levels but no one needs it 

s3 = session.resource('s3')
s3.Bucket('leagueaddict').download_file(players_file, players_file)

with open(players_file) as f:
    for line in f:
        time.sleep(1)
        name = line.strip()
        if name:
            info = get.summoner_info(name)
            current = Summoner(info['name'])
            class_of_leaguers.append(current)
            current.summonerid = info['id']
            current.accountid = info['accountId']
            current.puuid = info['puuid']
            current.level = info['summonerLevel']
            names_of_leaguers.append(current.name)

for summoner in class_of_leaguers:
    time.sleep(3)
    summoner.initiate_v5()

client = commands.Bot(command_prefix = '$')

@client.event
async def on_remove_member(member):
      print(f"{member} has left a server.")

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return
    for leaguer in class_of_leaguers:
        if "kill" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.kills} kills today!")
        if "death" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.deaths} deaths today!")
        if "assist" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.assists} assists today!")
        if "penta" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.pentaKills} pentakills today!")
        if "quadra" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.quadraKills} quadrakills today!")
        if "triple" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.tripleKills} triplekills today!")
        if "double" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.doubleKills} doublekills today!")
        if "no" and "game" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has played {len(leaguer.gameid)} games today.")
        if "win" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.wins} wins today!")
        if "loss" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has {leaguer.losses} losses today!")
        if "time" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"Today's playtime for {leaguer.name} is {datetime.timedelta(seconds = int(leaguer.playtimetoday()*60))}.")
        if "cs/min" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"Your CS/minute for the past game was {round(leaguer.prev_cspm(),2)}!")
        elif "cs" in message.content:
            if message.content.lower().startswith(f"^{leaguer.name}".lower()):
                await message.channel.send(f"{leaguer.name} has a total CS of {sum(leaguer.minions)} today!")

@client.command()
async def delete(ctx, no: int =1):
  if 0 <= no <= 10:
    await ctx.channel.purge(limit = no+1)
  else:
    await ctx.send(f"Please input a number between 0 and 10.")
    await ctx.message.add_reaction('🐸')

@client.command()
async def ping(ctx):
    await ctx.send(f'Ping: {client.latency*1000} ms')

@client.command()
async def rotation(ctx):
    rot = get.free_rotation()
    list_of_champs = ''
    for champion in rot['freeChampionIds']:
        list_of_champs = f'{list_of_champs}{data.champ_dict[str(champion)]}\n'
    await ctx.send(f'This week\'s free rotation is \n>>> {list_of_champs}')
    await ctx.message.add_reaction('🐸')

@client.command()
async def noob(ctx):
    rot = get.free_rotation()
    list_of_champs = ''
    for champion in rot['freeChampionIdsForNewPlayers']:
        list_of_champs = f'{list_of_champs}{data.champ_dict[str(champion)]}\n'
    await ctx.send(f'The current free rotation for new players (up to level 10) is \n>>> {list_of_champs}')
    await ctx.message.add_reaction('🐸')

@commands.command()
@commands.is_owner()
async def shutdown(self, ctx):
    await ctx.message.add_reaction('🐸')
    await self.client.logout()

@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('🐸')

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('🐸')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(discord_key)
