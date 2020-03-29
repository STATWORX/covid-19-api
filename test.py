import requests
import json
import pandas as pd

# POST to API
payload = {'country': 'Germany'}
URL = 'https://api.statworx.com/covid'
response = requests.post(url=URL, data=json.dumps(payload))

# Convert to data frame
df = pd.DataFrame.from_dict(json.loads(response.text))
df.head()
