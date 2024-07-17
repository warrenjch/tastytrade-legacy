import datetime
import time
import pandas_market_calendars as mcal

def get_channel():
    a=1
    while True:
        yield a
        a += 1

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

def calc_dte_reverse(expiry: datetime.datetime, tradingdays: int):
    nyse = mcal.get_calendar('NYSE')
    exp_date = expiry.date().strftime("%Y-%m-%d")
    start_day = expiry.date() - datetime.timedelta(days=(2*tradingdays+3))
    start_date = start_day.strftime("%Y-%m-%d")
    schedule = nyse.schedule(start_date=start_date, end_date=exp_date)
    #smth smth schedule[-(tradingdays+1)]
    pass

def calc_vwap(bb, ba, vbb, vba) -> float:
    return round((bb*vbb + ba*vba)/(vbb+vba),4)