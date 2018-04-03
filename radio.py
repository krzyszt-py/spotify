import json
import requests


def play(id="s2o4zxtqNZ4"):
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

def search(q=''):
    r = requests.get()
    # https: // www.google.pl / search?q = La + Di + Da + Di
