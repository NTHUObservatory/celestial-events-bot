import requests
import json
import re
from datetime import datetime
from tinydb import TinyDB, Query
import config

url = "https://www.tam.gov.taipei/OpenData.aspx?SN=D386D761E24960D0"
db = TinyDB('./db.json')

def post(event):
    title = event['title']
    desc = re.match(r'(.+（.+）)', event['內容']).group(1)
    desc_short = re.match(r'((?:[^，。]+[，。]?){3,9}[^，。]+[，。])', desc).group(1)[:-1]
    url = event['Source']

    r = requests.post('https://slack.com/api/chat.postMessage',
                      headers={'Authorization': f'Bearer {config.TOKEN}'},
                      data={'channel': config.CHANNEL,
                            'text': f'{desc_short}<{url}|...>'})
    res = json.loads(r.text)

    print(title, r.status_code, 'Success' if res['ok'] else 'Fail', res['ts'])


if __name__ == '__main__':
    j = requests.get(url).text
    raw_events = json.loads(j if j[0]!='\ufeff' else j[1:]) # Getting rid of UTF-8 BOM

    flag = True
    for i in range(len(raw_events)-1, -1, -1):
        event = raw_events[i]
        if db.get(Query().DataSN == event['DataSN']):
            continue
        event['date'] = str(datetime.now())
        db.insert(event)
        if i < 4:
            flag = False
            post(event)

    if (flag):
        print("It's great! There's nothing to post.")
