<<<<<<< HEAD
### NOTE: This branch is used for when MATCH-V4 deprecates. It is currently unusable until MATCH-V5 is available. The match-v4 branch is branch currently deployed.

This bot is used for tracking players that are playing league :D

The main file being run is the Leagueaddictioncure.py file. As the server is set up on Heroku, the Procfile is used to show which python file is going to be run by the Dynos.

The requirements indicate what libraries are needed and their respective versions.

The other 'mainfiles' contains all the classes and functions used by the bot commands and tasks (found in both Leagueaddictioncure.py and the cogs)

All the data that we need are under the Data2 folder. Inside it has the data.py file which contains the dictionary and dataframes for matching the IDs of the champions with the champion names. Moreover, the API-key and all other credentials, IDs are found in the keys.py file. These are left to the user to setup. Note that we use S3 here to store the files.
=======
Currently deployed bot. Only differences in the endpoint we extract from.
>>>>>>> 90f2f781c82306d4d498640b17dedb039f073c62
