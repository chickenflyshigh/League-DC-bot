from discord.ext import commands
from mainfiles import get
from mainfiles.summoner import Summoner
from mainfiles.summoner import class_of_leaguers, names_of_leaguers
import json
from Data2.keys import session, smurfs_file
import datetime
s3 = session.resource('s3')
s3.Bucket('leagueaddict').download_file(smurfs_file,smurfs_file)
with open(smurfs_file) as f:
    smurfs_dict = json.load(f)

smurfs = {} #for associating each account with each person. Note the uniqueness of each account.

for person, accounts in smurfs_dict.items():
    for account in accounts:
        smurfs[account] = person

class Smurfs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['asf','addsmurf'])
    async def AddSmurf(self, ctx, person, *, accname):
        person = person.lower().capitalize()
        if person in smurfs_dict:
            info = get.summoner_info(accname)
            if 'name' in info.keys():
                accname = info['name']
                if accname not in smurfs:
                    if accname in names_of_leaguers:
                        smurfs_dict[person].append(accname)
                        smurfs[accname] = person
                        with open(smurfs_file, 'w') as outfile:
                            json.dump(smurfs_dict,outfile)
                        s3 = session.client('s3')
                        with open(smurfs_file,'rb') as f:
                            s3.upload_fileobj(f, "leagueaddict", smurfs_file)
                        await ctx.send(f'Add successful!')
                    else:
                        await ctx.send(f'Add failed: {accname} has not yet been tracked. \nPlease add this account to the _tracking_ list using the _add_ command before associating the person with this account.')
                else:
                    await ctx.send(f'Add failed: {accname} is already associated with a name. \nPlease use the _Humans_ command to find the list of people with their associated accounts.')
            else:
                await ctx.send(f'Add failed: Please enter a valid summoner name.')
        else:
            await ctx.send(f'Add failed: {person} is currently not in the _Humans_ list. \nTo add a new name to the list, please use the _AddHuman_ command. \nTo find out who is in the list and their associated accounts, please use the _Humans_ command.')

    @commands.command(aliases = ['removesmurf','rsf'])
    async def RemoveSmurf(self, ctx, *, accname):
        info = get.summoner_info(accname)
        if 'name' in info.keys():
            accname = info['name']
            if accname in smurfs:
                smurfs_dict[smurfs[accname]].remove(accname)
                smurfs.pop(accname)
                with open(smurfs_file, 'w') as outfile:
                    json.dump(smurfs_dict,outfile)
                s3 = session.client('s3')
                with open(smurfs_file,'rb') as f:
                    s3.upload_fileobj(f, "leagueaddict", smurfs_file)
                await ctx.send(f'Remove succesful: {accname} succesfully removed.')
            else:
                await ctx.send(f'Remove failed: {accname} is not currently associated with any human.')
        else:
            await ctx.send('Remove failed: Please enter a valid summoner name.')

    @commands.command(aliases = ['addhuman','ah'])
    async def AddHuman(self, ctx, person):
        if len(smurfs_dict) == 30:
            await ctx.send('Add failed: Number of humans is capped at 30.')
            return
        person = person.lower().capitalize()
        if person not in smurfs_dict:
            smurfs_dict[person] = []
            with open(smurfs_file, 'w') as outfile:
                json.dump(smurfs_dict,outfile)
            s3 = session.client('s3')
            with open(smurfs_file,'rb') as f:
                s3.upload_fileobj(f, "leagueaddict", smurfs_file)
            await ctx.send(f'Add successful: {person} has been added to the _Humans_ list.')
        else:
            await ctx.send('Add failed: This human is already in the list.')
    
    
    @commands.command(aliases = ['rh','removehuman'])
    async def RemoveHuman(self, ctx, person):
        person = person.lower().capitalize()
        if person in smurfs_dict:
            for accounts in smurfs_dict[person]:
                smurfs.pop(accounts)
            smurfs_dict.pop(person)
            with open(smurfs_file, 'w') as outfile:
                json.dump(smurfs_dict,outfile)
            s3 = session.client('s3')
            with open(smurfs_file,'rb') as f:
                s3.upload_fileobj(f, "leagueaddict", smurfs_file)
            await ctx.send('Remove succesful: This human has been removed from the list.')
        else:
            await ctx.send('Remove failed: This human is not in the list.')

    @commands.command(aliases = ['humans','smurfs','people','ppl'])
    async def Humans(self, ctx):
        to_send = ""
        for person, accounts in smurfs_dict.items():
            to_send = to_send + f'{person}: {", ".join(accounts)}\n'
        await ctx.send(f'>>> {to_send}')

    @commands.command(aliases = ['addiction'])
    async def time(self, ctx, *, player):
        player = player.lower().capitalize()
        if player not in smurfs_dict:
            await ctx.send(f'{player} is not in the _Humans_ list. \nTo add a new person to the list, use the _AddHuman_ [human] command and to link it with an account use the _AddSmurf_ [human] [account] command.')
            return
        total_time = 0
        for account in smurfs_dict[player]:
            for person in class_of_leaguers:
                if person.name == account:
                    total_time += person.playtimetoday()
                    break
        await ctx.send(f"Today's playtime for {player} is {datetime.timedelta(seconds = int(total_time*60))}.")
def setup(client):
    client.add_cog(Smurfs(client))