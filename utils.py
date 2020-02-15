from dateutil import parser
from datetime import datetime, timezone


def sanitize_instance(instance: str) -> str:
    if instance.startswith('https://'):
        return instance.lstrip('https://').strip('/')
    return instance.strip('/')


def genkey(instance: str, id: int) -> str:
    # used for dict keys in subscriptions
    return sanitize_instance(instance) + '_' + str(id)


def expires_in(timestr: str):
    return parser.parse(timestr) - datetime.now(tz=timezone.utc)


def humanify_timedelta(timedelta):
    # timedelta natively provides
    d, s = timedelta.days, timedelta.seconds
    h = s // 3600
    m = s // 60 - h * 60
    s = s % 60
    return (d, h, m, s)


def nowstring():
    # YYYY-MM-DD HH:MM:SS
    # removes microseconds and timezone
    return str(datetime.now(tz=timezone.utc))[:19]
