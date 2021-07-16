from discord.ext import commands
from mainfiles import get
from mainfiles.summoner import Summoner
from mainfiles.summoner import class_of_leaguers
from mainfiles.summoner import names_of_leaguers
from Data2.keys import session, players_file

class PlayerList(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases =['asr','add'])
    async def add_summoner(self, ctx, *, name):
        if len(class_of_leaguers) == 30:
            await ctx.send("Add failed: Maximum number of players tracked is capped at 30.")
        else:
            info = get.summoner_info(name)
            if 'name' not in info.keys():
                await ctx.send("Add failed: Please choose a valid summoner name.")
            elif info['name'] not in names_of_leaguers:
                leaguer = Summoner(info['name'])
                leaguer.summonerid = info['id']
                leaguer.accountid = info['accountId']
                leaguer.puuid = info['puuid']
                leaguer.level = info['summonerLevel']
                leaguer.name = info['name']
                leaguer.initiate_v4()
                with open(players_file,'a') as f:
                    f.write(f'{leaguer.name}\n')

                s3 = session.client('s3')
                with open(players_file,'rb') as f:
                    s3.upload_fileobj(f, "leagueaddict",players_file)

                class_of_leaguers.append(leaguer)
                names_of_leaguers.append(leaguer.name)
                await ctx.send(f"Add successful. {leaguer.name} is now being tracked.")
                await ctx.message.add_reaction('🐸')
            else:
                await ctx.send("Add failed: This player is already in the list.")

    @commands.command(aliases=['rm','remove','rmsmr'])
    async def remove_summoner(self, ctx, *, name):
        info = get.summoner_info(name)
        if len(class_of_leaguers) == 0:
            await ctx.send("Remove failed: There are no players in the list to remove.")
        elif 'name' not in info.keys():
            await ctx.send("Remove failed: This player does not exist.")
        elif info['name'] not in names_of_leaguers:
            await ctx.send("Remove failed: This player is not currently in the list.")
        else:
            for player in class_of_leaguers:
                if player.name == info['name']:
                    class_of_leaguers.remove(player)
                    break
            names_of_leaguers.remove(info['name'])
            new_players_file = ''
            for playername in names_of_leaguers:
                new_players_file = new_players_file + f'{playername}\n'
            with open(players_file, 'w') as f:
                f.write(new_players_file)

            s3 = session.client('s3')
            with open(players_file,'rb') as f:
                s3.upload_fileobj(f, "leagueaddict", players_file)
            await ctx.send("Player removed succesfully.")
            await ctx.message.add_reaction('🐸')

    @commands.command(aliases = ['list', 'los'])
    async def list_of_summoners(self, ctx):
        if len(class_of_leaguers) >=2:
            ls = ''
            for person in class_of_leaguers:
                ls = f"{ls}\n{person.name}".lstrip()
            await ctx.send(f"{ls}")
            await ctx.message.add_reaction('🐸')
        elif len(class_of_leaguers) == 1:
            await ctx.send(class_of_leaguers[0].name)
            await ctx.message.add_reaction('🐸')
        else:
            await ctx.send("There are currently no players being tracked.")


def setup(client):
    client.add_cog(PlayerList(client))
