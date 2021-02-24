import requests
import json
import pandas as pd

# POST to world API
payload = {'code': 'ALL'}
URL = 'https://api.statworx.com/covid'
URL = 'http://127.0.0.1:80/covid'
response_world = requests.post(url=URL, data=json.dumps(payload))
df_world = pd.DataFrame.from_dict(json.loads(response_world.text))
df_world.head()

# POST to Germany API
payload = {}
URL = 'https://api.statworx.com/covid/de'
response_germany = requests.post(url=URL, data=json.dumps(payload))
df_germany = pd.DataFrame.from_dict(json.loads(response_germany.text))
df_germany.head()
