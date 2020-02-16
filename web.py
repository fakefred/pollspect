from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from fedi import *
from polls import *
from os import path
from json import dumps
from random import choice


@view_config(route_name='index')
def index(req):
    # HACK opens static html and serves client
    return Response(open('./static/index.html', 'r').read())


@view_config(route_name='analyze')
def analyze(req):
    key = None
    if 'key' in req.params:
        key = req.params['key']
        if not key in subscriptions and find_poll_in_archive(key) is None:
            return Response('Poll data not found')

    elif 'url' in req.params:
        url = req.params['url']
        key = find_poll_key_by_url(url)
        if key is None:
            instance, id = get_instance_and_id_from_status_url(url)

            if instance == '404 not found':
                return Response('Poll does not exist or is deleted')
            elif instance == 'not ok':
                return Response('Error occurred while server made request')
            elif instance == 'error':
                return Response('Error fetching URL')
            elif instance == 'invalid':
                return Response('Invalid URL')
            elif instance == 'no poll':
                return Response('No poll in this toot')

            key = genkey(instance, id)

    else:
        return Response('No URL or key entered')

    intv = int(req.params['interval']) if 'interval' in req.params else 30

    analysis = analyze_poll(key)
    if analysis == 'not found':
        sub_status = subscribe_to_poll(instance, id, url, intv=intv)
        if sub_status == 'expired':
            return Response('Poll expired')
        elif sub_status == 404:
            return Response('Poll not found')
        analysis = analyze_poll(key)

    return Response(dumps(analysis))


@view_config(route_name='random')
def random(req):
    # randomly pick one key and redirect to it
    raise HTTPFound(
        location='/?key=' + choice(list(subscriptions.keys())))


@view_config(route_name='list')
def list_polls(req):
    # responds with a list of all subscribed polls
    return Response(dumps(list_subscribed_polls()))


def start_server():
    with Configurator() as config:
        config.add_route('index', '/')
        config.add_route('analyze', '/analyze')
        config.add_route('random', '/random')
        config.add_route('list', '/list')
        config.add_static_view(
            'static',
            path.join(path.dirname(__file__), 'static'))
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6522, app)
    print('Server started')
    server.serve_forever()
