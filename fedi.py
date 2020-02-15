import requests
import re
from utils import sanitize_instance


def infer_api_url(url: str) -> str:
    if not re.match('^https://\S+(\.\S+)+', url):
        return 'invalid'
    # remove protocol, split into pieces
    slices = re.sub('^https://', '', url.strip()).split('/')
    if slices[1:3] == ['web', 'statuses'] and slices[3].isdecimal():
        # mastodon
        return 'https://' + slices[0] + '/api/v1/statuses/' + slices[3]
    elif re.match('^@\S+$', slices[1]) and slices[2].isdecimal():
        # also mastodon
        return 'https://' + slices[0] + '/api/v1/statuses/' + slices[2]
    elif slices[1] == 'notice' and slices[2].isalnum():
        # pleroma
        pass
    return 'invalid'


def get_instance_and_id_from_status_url(url: str) -> tuple:
    api_url = infer_api_url(url)
    if not api_url == 'invalid':
        try:
            res = requests.get(api_url).json()
            if 'poll' in res and res['poll']:
                return (
                    url.split('/')[2],
                    int(res['poll']['id']))
            return ('no poll', None)
        except Exception:
            print('Error occurred while GET\'ing ' + api_url)
            return ('error', None)
    return ('invalid', None)  # invalid


def get_poll_by_id(instance: str, id: int) -> dict:
    # just barely smart enough to add protocol
    # and remove redundant slashes
    try:
        return requests.get(('https://'
                             if not re.match('^https://', instance.strip())
                             else '') + instance.strip('/') +
                            '/api/v1/polls/' + str(id)).json()
    except Exception:
        print('Error occurred while GET\'ing poll #' +
              str(id) + ' on instance ' + instance)


if __name__ == '__main__':
    print(get_instance_and_id_from_status_url(
        'https://mastodon.technology/web/statuses/103606663022677446'))
    print(get_poll_by_id('mastodon.technology', 20569))
