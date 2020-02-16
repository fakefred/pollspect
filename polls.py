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

try:
    with open('./archive.json', 'x') as f:
        f.write('{}')
        f.close()
except FileExistsError:
    pass

scheduler = BackgroundScheduler()
scheduler.start()
# we will add jobs as new polls are to be subscribed


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


def subscribe_to_poll(instance: str, id: int, url: str, intv=30) -> str:
    key = genkey(instance, id)
    if not key in subscriptions:
        # fetch poll
        poll = get_poll_by_id(instance, id)
        if not poll:
            return 'no poll'
        elif poll == 404:
            return '404 not found'
        elif poll['expired']:
            return 'expired'

        # create a subscription
        subscriptions[key] = {
            'subscribed_at': nowstring(),
            'interval': intv,
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
        # add a scheduled job
        # id is used as an identifier
        scheduler.add_job(
            poll_poll, args=[key], trigger='interval', minutes=intv, id=key)

        return 'success'
    return 'already subscribed'


def find_poll_key_by_url(url: str) -> str:
    for k, v in subscriptions.items():
        if v['url'] == url:
            return k

    # not in current subscriptions
    # search in archive
    return find_poll_key_in_archive_by_url(url)


def find_poll_in_archive(key: str) -> dict:
    archive = load(open('./archive.json', 'r'))
    if key in archive:
        return archive[key]
    return None


def find_poll_key_in_archive_by_url(url: str) -> str:
    archive = load(open('./archive.json', 'r'))
    for k, v in archive.items():
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
    elif poll == 404:
        # API returns 404; poll DNE or is deleted.
        # In this case, since poll must have been in existence
        # in order for the subscriber to invoke this method.
        # Trigger job removal.
        move_to_archive(key)
        scheduler.remove_job(key)
        return 'deleted'
    elif poll['expired']:
        move_to_archive(key)
        scheduler.remove_job(key)  # stop polling this
        return 'expired'

    # save as {'snapshot': {<datetime>: [0, 1, 2, 3]}}
    # the array representing votes for each choice
    subscriptions[key]['snapshots'][nowstring()] = [opt['votes_count']
                                                    for opt in poll['options']]
    update_json()
    return 'success'


def list_subscribed_polls() -> list:
    return [
        {'key': k, 'url': v['url']}
        for k, v in subscriptions.items()]


def analyze_poll(key: str):
    # analyze a certain poll for frontend visualization
    if key in subscriptions:
        poll = subscriptions[key]
        expired = False
    else:
        poll = find_poll_in_archive(key)
        if poll is None:
            return 'not found'
        expired = True

    stats = {
        'generated_at': nowstring(),
        'interval': poll['interval'],
        'key': key,
        'expired': expired,
        'expires_in': humanify_timedelta(expires_in(poll['expires_at'])),
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
        stats['snapshots'].append(timestr)
        for idx, count in enumerate(votes):
            stats['choices'][idx]['votes'].append(count)

    return stats


for k, s in subscriptions.items():
    # when pollspect launches,
    # automatically resume all pre-scheduled jobs
    scheduler.add_job(
        poll_poll, args=[k], id=k,
        trigger='interval', minutes=s['interval'])
