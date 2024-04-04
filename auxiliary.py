import datetime
import time

def time_to_unix(t: datetime.datetime) -> int:
    return int(time.mktime(t.timetuple())*1000)

def unix_to_time(t: int, granularity: str = 'd', scaled: bool = True):
    if scaled:
        dt = datetime.datetime.fromtimestamp(t/1000)
    else:
        dt = datetime.datetime.fromtimestamp(t)

    if granularity == 'd':
        t = datetime.date(dt.year, dt.month, dt.day)
        return t
    elif granularity == 's':
        return dt
    else:
        raise ValueError(f'invalid granularity: {granularity}')