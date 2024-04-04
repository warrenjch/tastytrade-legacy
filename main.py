from api import *
from dxlink import *
from auxiliary import *
import time
import datetime
import asyncio




if __name__ == '__main__':
    #load configs and login
    config = Config(prod=False)
    session = API(config)
    session.login()
    print("Logged in", session.user_data)
    session.get_dxlink()
    stream = DXLink(url = session.dxlink_url, auth_token= session.dxlink_token)

    #config feed
    data_config = {
        "type": "FEED_SETUP",
        "channel": 1,
        "acceptAggregationPeriod": 10,  # TODO: why this thing not reflecting
        "acceptDataFormat": "COMPACT",
        "acceptEventFields": {
            "Quote": ["eventType", "eventSymbol", "bidPrice", "askPrice", "bidSize", "askSize"]
        }
    }
    time.sleep(3)
    #stream.send(data_config)

    #request feed subscription
    data = {
        "type": "FEED_SUBSCRIPTION",
        "channel": 1,
        "add": [
            {
                "symbol": "SOUN",
                "type": "Quote"
            }
        ]
    }
    #stream.send(data)

    #request candle subscription
    candle_channel = 3
    candle_config = stream.channel_request(candle_channel, parameters={'contract': 'HISTORY'}) #any random channel works
    stream.send(candle_config)
    time.sleep(1)

    #request candle
    candle_data = stream.candle_format(
        symbol='SPY',#'.SPY240405P523',
        fromtime=datetime.datetime(2024,3,15,0,0,0),granularity='m')
    stream.send(candle_data, dump_feed=True)