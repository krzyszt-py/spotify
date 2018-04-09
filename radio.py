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


def search(q: str) -> List[str]:
    r = requests.get('https://www.googleapis.com/youtube/v3/search',
                     params=f"q={urllib.parse.quote(q)}&maxResults=25&part=snippet&key={config.YOUR_API_KEY}")
    assert r.status_code == 200
    print(r.json())

    return [v['id']['videoId']
            for v in r.json()['items']
            if 'videoId' in v['id']
            and not long_song(v['id']['videoId'])]


def long_song(id: str) -> bool:
    r = requests.get('https://www.googleapis.com/youtube/v3/videos',
                     params=f'id={urllib.parse.quote(id)}&part=contentDetails&key={config.YOUR_API_KEY}')
    assert r.status_code == 200

    return isodate.parse_duration(r.json()['items'][0]['contentDetails']['duration']).total_seconds() > 15 * 60
