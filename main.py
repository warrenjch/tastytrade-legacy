from api import *
from dxlink import *
from auxiliary import *
import time
from datetime import datetime, date, time, timedelta
import asyncio


async def streamer(stream, mode="single stream", symbol = '.SPY240712P560'):
    # generate channels and select mode
    mode = mode
    symbol = symbol
    gen = get_channel()

    if mode == "single stream":
        channel = next(gen)
        await stream.request_stream(symbol, channel)

    elif mode == "candle data":
        # request candle subscription
        granularity, channel, fromtime = '30m', next(gen), datetime(2024, 4, 8, 0, 0,0)
        await stream.request_candle(symbol, channel, fromtime, granularity, dump_feed=True)

    elif mode == "vol surface stream":
        # something
        pass

async def trader(stream):
    now = datetime.now()
    today = date.today()
    start1 = datetime.combine(today, time(22,0))
    end1 = datetime.combine(today, time(22,30))
    print('NOW!!!', now)

    while now < start1 and False:
        await asyncio.sleep(1)
    print('TIME TO COOK')

    filled = False
    await streamer(stream, mode="single stream", symbol='SPY')
    while now < end1 or filled == False:
        await stream.feed_data_event.wait()
        stream.feed_data_event.clear()
        d = stream.message_data[1]
        vwap = calc_vwap(d[2],d[3],d[4],d[5])
        #get atm
        atm = int(vwap)
        otmput, otmcall = atm - 6, atm + 6
        print(otmput, atm, otmcall)

        #request option chain of spy d+1 and find atm
        fly = [f"SPY   {today.strftime('%y%m%d')}C00{atm}000", f"SPY   {today.strftime('%y%m%d')}P00{atm}000", f"SPY {today.strftime('%y%m%d')}P00{otmput}000", f"SPY {today.strftime('%y%m%d')}C00{otmcall}000"]
        order = {
                    "time-in-force": "Day",
                    "order-type": "Limit",
                    "price": "2",
                    "price-effect": "Credit",
                    "legs": [
                    {
                        "action": "Sell to Open",
                        "symbol": f"SPY   240719C00{atm}000", #"AAPL  230818C00197500" AAPL Call Option with 197.5 strike price, option expires 2023-08-18
                        "quantity": 1,
                        "instrument-type": "Equity Option",
                    },
                    {
                        "action": "Sell to Open",
                        "symbol": f"SPY   240719P00{atm}000",
                        "quantity": 1,
                        "instrument-type": "Equity Option",
                    }
                  ]
                }
        stream.send_order(order)
        #do a fly at atm
        pass


async def main():
    #load configs and login
    config = Config(prod=False)
    session = API(config)
    session.login()
    print("Logged in", session.user_data)
    session.get_dxlink()
    stream = DXLink(session=session, account_number=config.account_number)

    await stream.auth_future

    #await streamer(stream, mode="single stream")

    #response = session.get('/option-chains/SPY/compact')
    #print(response)

    await trader(stream)

if __name__ == '__main__':
    asyncio.run(main())