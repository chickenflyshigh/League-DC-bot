import boto3
import os 
session = boto3.Session(region_name = 'ap-southeast-2',
aws_access_key_id = os.getenv('aws_access_key_id'),
aws_secret_access_key = os.getenv('aws_secret_access_key')) # setting up your credentials for aws

api_key=os.getenv('apikey')

#discord_key = os.getenv('discordtest')
discord_key = os.getenv('discordkey') #key for the discord bot

channel_id = int(os.getenv('channel_id')) #discord channel id

players_file = os.getenv('players_file')

smurfs_file = os.getenv('smurfs_file')
