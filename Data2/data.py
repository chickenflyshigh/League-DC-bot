import os
import json
import pandas as pd

queue_dict = {}
champ_dict = {}

queuefile = os.path.join('Data2','queuesFull.json')
with open(queuefile) as f:
    queues = json.load(f)
    for queue in queues:
        queue_dict[queue['id']] = queue['name']

champfile = os.path.join('Data2','champion.json')
with open(champfile,encoding = 'utf8') as f:
    champs = json.load(f)
    dt = champs['data']
    for champ in dt:
        champ_dict[str(dt[champ]['key'])] = dt[champ]['id']

champ_id_df = pd.DataFrame.from_dict(champ_dict,orient='index')
champ_id_df.rename(columns = {0: "champion name"},inplace=True)
champ_id_df.index.name = 'championId'
champ_id_df.index = champ_id_df.index.astype('int64')

if __name__ == '__main__':
    print(champ_dict['161'])