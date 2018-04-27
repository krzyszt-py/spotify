import config
import isodate
import json
import requests
import urllib

from typing import List


def play(id: str) -> None:
    session = requests.sessions.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    r = session.get('https://togethertube.com/rooms/radio-wolny-direct')
    session.headers.update({
        'Referer': 'https://togethertube.com/rooms/radio-wolny-direct',
        'Origin': 'https://togethertube.com',
        'Content-Type': 'application/json;charset=UTF-8',
    })

    p = session.post('https://togethertube.com/api/v1/rooms/radio-wolny-direct/playlist/votes',
                     data=json.dumps({"mediaServiceId": "youtube", "mediaId": id}))
    assert p.status_code == 201


def search(q: str, lenght: float) -> List[str]:
    r = requests.get('https://www.googleapis.com/youtube/v3/search',
                     params=f"q={urllib.parse.quote(q)}&maxResults=25&part=snippet&key={config.YOUR_API_KEY}")
    assert r.status_code == 200
    print(r.json())

    ids = [v['id']['videoId']
           for v in r.json()['items']
           if 'videoId' in v['id']]
    ids = ','.join(ids)
    r = requests.get('https://www.googleapis.com/youtube/v3/videos',
                     params=f'id={urllib.parse.quote(ids)}&part=contentDetails&key={config.YOUR_API_KEY}')
    assert r.status_code == 200
    info = r.json()
    lenghts = {item['id']: isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
               for item in info['items']}

    return sorted(lenghts, key=lambda id: abs(lenghts[id] - lenght))


def long_song(id: str) -> bool:
    r = requests.get('https://www.googleapis.com/youtube/v3/videos',
                     params=f'id={urllib.parse.quote(id)}&part=contentDetails&key={config.YOUR_API_KEY}')
    assert r.status_code == 200

    return isodate.parse_duration(r.json()['items'][0]['contentDetails']['duration']).total_seconds() > config.LONG_SONG


def ws():
    wss = 'wss://togethertube.com/websocket/rooms/radio-wolny-direct'
    from websocket import create_connection
    ws = create_connection(wss)
    ws.send(json.dumps({"op": "addr_sub", "addr": "dogecoin_address"}))
    result = ws.recv()
    print(result)
    ws.close()
