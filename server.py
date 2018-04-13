from pprint import pprint
from typing import Dict, List, Any

import adbus
from sanic import Sanic
from sanic.response import text as response_text
from sanic_jinja2 import SanicJinja2

import config
import radio

app = Sanic(__name__)
jinja = SanicJinja2(app)
app.proxy_listen: adbus.client.Proxy
app.proxy: adbus.client.Proxy


async def track_changed_handler(_a: str, metadata: Dict[str, Any], _c: List[str]):
    pprint(metadata)
    metadata = metadata['Metadata']
    if app.playing == metadata['mpris:trackid']:
        return
    app.playing = metadata['mpris:trackid']
    search = radio.search(f"{metadata['xesam:album']} {metadata['xesam:title']}")
    radio.play(search[0])


@app.listener('before_server_start')
async def setup_dbus(app, _loop):
    service = adbus.Service(bus='session')
    app.proxy = adbus.client.Proxy(
        service,
        'org.mpris.MediaPlayer2.spotify',
        '/org/mpris/MediaPlayer2',
        interface='org.mpris.MediaPlayer2.Player')
    app.proxy_listen = adbus.client.Proxy(
        service,
        'org.mpris.MediaPlayer2.spotify',
        '/org/mpris/MediaPlayer2',
        interface='org.freedesktop.DBus.Properties')
    app.playing = ''

    await app.proxy.update()
    await app.proxy_listen.update()

    app.proxy_listen.PropertiesChanged(track_changed_handler)


@app.route('/play')
async def play(_r):
    await app.proxy.PlayPause()
    return response_text('', 204)


@app.route('/robots.txt')
@app.route('/favicon.ico')
async def pass_(_r):
    return response_text('', 204)


@app.route('/')
@jinja.template('track.html')
async def index(_r):
    metadata = await app.proxy.Metadata()
    metadata['length_m'], metadata['length_s'] = divmod(metadata['mpris:length'] // 1_000_000, 60)
    return dict(metadata=metadata)


@app.route('/info')
async def index(_r):
    print(app.proxy.methods.keys())
    print(app.proxy.properties.keys())
    print(app.proxy.signals)
    return response_text('', 204)


app.run(port=config.PORT)
