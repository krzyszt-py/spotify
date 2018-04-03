from typing import Dict, List, Any

import adbus
from sanic import Sanic
from sanic.response import text as response_text
from sanic_jinja2 import SanicJinja2

app = Sanic(__name__)
jinja = SanicJinja2(app)
app.proxy_listen: adbus.client.Proxy
app.proxy: adbus.client.Proxy


@app.listener('before_server_start')
async def setup_dbus(app, _loop):
    service = adbus.Service(bus='session')
    app.proxy = adbus.client.Proxy(service,
                                   'org.mpris.MediaPlayer2.spotify',
                                   '/org/mpris/MediaPlayer2',
                                   interface='org.mpris.MediaPlayer2.Player')
    app.proxy_listen = adbus.client.Proxy(service,
                                          'org.mpris.MediaPlayer2.spotify',
                                          '/org/mpris/MediaPlayer2',
                                          interface='org.freedesktop.DBus.Properties')

    await app.proxy.update()
    await app.proxy_listen.update()

    async def local_method(_a: str, metadata: Dict[str, Any], _c: List[str]):
        print(metadata)
        # TODO:
        # - radio.search(title)
        # - radio.play(youtube_id)

    app.proxy_listen.PropertiesChanged(local_method)


@app.route('/play')
async def play(_r):
    await app.proxy.PlayPause()
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


app.run()
