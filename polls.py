from fedi import *
from json import dump, dumps, load, decoder
from utils import *
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep
from dateutil import parser

try:
    subscriptions = load(open('./subscriptions.json', 'r'))
except FileNotFoundError:
    # does not exist: create file
    dump({}, open('./subscriptions.json', 'x'))
    subscriptions = {}
except decoder.JSONDecodeError:
    # file is empty: dump {} into it
    dump({}, open('./subscriptions.json', 'w'))
    subscriptions = {}


def update_json():
    with open('./subscriptions.json', 'w') as f:
        f.write(dumps(subscriptions))
        f.close()


def move_to_archive(key: str):
    try:
        archive = load(open('./archive.json', 'r'))
    except FileNotFoundError:
        dump({}, open('./archive.json', 'x'))
        archive = {}
    except decoder.JSONDecodeError:
        dump({}, open('./archive.json', 'w'))
        archive = {}

    archive[key] = subscriptions[key]
    with open('./archive.json', 'w') as f:
        f.write(dumps(archive))
        f.close()

    del(subscriptions[key])
    update_json()


def subscribe_to_poll(instance: str, id: int, url: str) -> str:
    key = genkey(instance, id)
    if not key in subscriptions:
        # fetch poll
        poll = get_poll_by_id(instance, id)
        if not poll:
            return 'no poll'
        elif poll['expired']:
            return 'expired'

        # create a subscription
        subscriptions[key] = {
            'subscribed_at': nowstring(),
            'expires_at': poll['expires_at'],
            'url': url,
            'instance': sanitize_instance(instance),
            'id': id,
            'multiple': poll['multiple'],
            'choices': [opt['title'] for opt in poll['options']],
            'snapshots': {}
        }
        update_json()
        poll_poll(key)
        return 'success'
    return 'already subscribed'


def find_poll_key_by_url(url: str) -> str:
    for k, v in subscriptions.items():
        if v['url'] == url:
            return k
    return None


def poll_poll(key: str) -> str:
    if not key in subscriptions:
        return 'not subscribed'

    sub_info = subscriptions[key]

    poll = get_poll_by_id(sub_info['instance'], sub_info['id'])
    if not poll:
        return 'no poll'
    elif poll['expired']:
        move_to_archive(key)
        return 'expired'

    # save as {'snapshot': {<datetime>: [0, 1, 2, 3]}}
    subscriptions[key]['snapshots'][nowstring()] = [opt['votes_count']
                                                    for opt in poll['options']]
    update_json()
    return 'success'


def poll_all_polls():
    # helper method
    for key in subscriptions.keys():
        poll_poll(key)


def analyze_poll(key: str):
    # analyze a certain poll for frontend visualization
    if not key in subscriptions:
        return 'not subscribed'

    poll = subscriptions[key]
    d, h, m, s = humanify_timedelta(
        expires_in(poll['expires_at']))

    stats = {
        'generated_at': nowstring(),
        'expires_in': f'{d} days, {h}:{m}:{s}',
        'url': poll['url'],
        'instance': poll['instance'],
        'id': poll['id'],
        'multiple': poll['multiple'],
        'snapshots': [],
        'choices': [{  # stuff in titles
            'title': opt,
            'votes': []
        } for opt in poll['choices']]
    }

    # stuff in snapshot time and votes
    for timestr, votes in poll['snapshots'].items():
        stats['snapshots'].append(
            (parser.parse(timestr) -
             parser.parse(poll['subscribed_at'])).seconds)
        for idx, count in enumerate(votes):
            stats['choices'][idx]['votes'].append(count)

    return stats


def schedule_poll(seconds=300):
    # create interval scheduler
    sch = BackgroundScheduler()
    sch.add_job(poll_all_polls, 'interval', seconds=seconds)
    sch.start()
