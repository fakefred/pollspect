from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response
from fedi import *
from polls import *
from os import path
from json import dumps


@view_config(route_name='index')
def index(req):
    # HACK opens static html and serves client
    return Response(open('./static/index.html', 'r').read())


@view_config(route_name='analyze')
def analyze(req):
    if 'url' in req.params:
        url = req.params['url']
        key = find_poll_key_by_url(url)
        if key is None:
            instance, id = get_instance_and_id_from_status_url(url)

            if instance == 'error':
                return Response('Error fetching URL')
            elif instance == 'invalid':
                return Response('Invalid URL')
            elif instance == 'no poll':
                return Response('No poll in this toot')

            key = genkey(instance, id)
    else:
        return Response('No URL entered')

    analysis = analyze_poll(key)
    if analysis == 'not subscribed':
        sub_status = subscribe_to_poll(instance, id, url)
        if sub_status == 'expired':
            return Response('Poll expired')
        analysis = analyze_poll(key)

    return Response(dumps(analysis))


def start_server():
    with Configurator() as config:
        config.add_route('index', '/')
        config.add_route('analyze', '/analyze')
        config.add_static_view(
            'static',
            path.join(path.dirname(__file__), 'static'))
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6522, app)
    print('Server started')
    server.serve_forever()
