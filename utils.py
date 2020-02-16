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
    # timedelta natively provides days and seconds
    # could be negative though
    d, s = timedelta.days, timedelta.seconds
    h = s // 3600
    m = s // 60 - h * 60
    s = s % 60

    outstr = ''
    if d > 0:
        outstr += str(d) + ' days, '

    outstr += two_digit(h) + ':' + two_digit(m) + ':' + two_digit(s)
    return outstr


def nowstring():
    # YYYY-MM-DD HH:MM:SS
    # removes microseconds and timezone
    return str(datetime.now(tz=timezone.utc))[:19]


def two_digit(n: int) -> str:
    return str(n) if n > 9 else '0' + str(n)
