import json
import websocket
import threading
import pandas as pd
import datetime
from auxiliary import *
from dbhandler import *
import asyncio

class DXLink():
    socket: websocket.WebSocketApp = None
    url: str = None
    auth_token: str = None
    auth_state: str = None
    user_id: str = None
    dump_feed: bool = False
    candle_symbol: str = None
    message_data: list = None

    def __init__(self, session, account_number: str = None):
        self.session = session
        self.url = session.dxlink_url
        self.auth_token = session.dxlink_token
        self.account_number = account_number
        self.loop = asyncio.get_event_loop()
        self.auth_future = self.loop.create_future()
        self.channel_open_event = asyncio.Event()
        self.feed_data_event = asyncio.Event()
        self.connect()

    def connect(self):
        print("dxlink connect")
        self.socket = websocket.WebSocketApp(
            url=self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.thread = threading.Thread(target=self.socket.run_forever)
        self.thread.start()

    def on_open(self, ws):
        print("dxlink open")
        self.send(
            {
                "type": "SETUP",
                "keepaliveTimeout": 60,
                "acceptKeepaliveTimeout": 60,
                "version": "0.1",
            }
        )

    def on_message(self, ws, message):
        message = json.loads(message)
        print(f"got {message}")
        match message["type"]:
            case "SETUP":
                self.send({"type": "AUTH", "token": self.auth_token})
            case "AUTH_STATE":
                if message["state"] == "AUTHORIZED":
                    self.auth_state = message["state"]
                    self.user_id = message["userId"]
                    self.loop.call_soon_threadsafe(self.auth_future.set_result, True)
            case "CHANNEL_OPENED":
                self.loop.call_soon_threadsafe(self.channel_open_event.set)
            case "KEEPALIVE":
                self.send({"type": "KEEPALIVE"})
            case "FEED_DATA":
                if self.dump_feed == True:
                    if self.candle_data is None:
                        print('ERROR: candle symbol is None')
                    else:
                        tn = self.candle_data
                        self.DB = DBHandler()
                        self.DB.modify_table(table_name=tn,jsonobject=message["data"],if_exists="replace")
                else:
                    self.loop.call_soon_threadsafe(self.feed_data_event.set)
                    self.message_data = message["data"]

    def on_close(self, ws, status_code, message):
        print(f"dxlink close {status_code} {message}")

    def on_error(self, ws, error):
        print(f"dxlink error {error}")

    def send(self, data: dict = {}, dump_feed: bool = False):
        self.dump_feed = dump_feed
        print(f"sending {data}")
        if (
                self.auth_state != "AUTHORIZED"
                and data["type"] != "SETUP"
                and data["type"] != "AUTH"
        ):
            print(
                f"dxlink tried to send message of type {data['type']} but auth_state is {self.auth_state}"
            )
            return
        if not "channel" in data:
            data["channel"] = 0
        if not "userId" in data and self.user_id is not None:
            data["userId"] = self.user_id
        self.socket.send(json.dumps(data))

    #formatting functions
    def channel_request(self, channel: int, service: str = "FEED", parameters: dict = None):
        if parameters is None:
            parameters = {"contract": "AUTO"}
        request = {
            "type": "CHANNEL_REQUEST",
            "channel": channel,
            "service": service,
            "parameters": parameters
        }
        return request

    def candle_format(self, symbol: str, fromtime: datetime.datetime, channel: int, granularity: str = None):
        data = {
            'type': 'FEED_SUBSCRIPTION',
            'channel': channel,
            'add': [
                {
                    'symbol': f'{symbol}{{={granularity}}}' if granularity is not None else f'{symbol}',
                    'type': 'Candle',
                    'fromTime': time_to_unix(fromtime)
                }
            ]
        }
        self.candle_data = f'{symbol}-{granularity}-{fromtime}' if granularity is not None else symbol
        return data


    #API functions
    async def request_stream(self, symbol: str, channel: int):
        # request channel
        self.send(self.channel_request(channel))
        await self.channel_open_event.wait()
        self.channel_open_event.clear()
        # config feed
        data_config = {
            "type": "FEED_SETUP",
            "channel": channel,
            "acceptAggregationPeriod": 10,  # TODO: why this thing not reflecting
            "acceptDataFormat": "COMPACT",
            "acceptEventFields": {
                "Quote": ["eventType", "eventSymbol", "bidPrice", "askPrice", "bidSize", "askSize"]
            }
        }
        self.send(data_config)
        # request feed subscription
        data = {
            "type": "FEED_SUBSCRIPTION",
            "channel": channel,
            "add": [
                {
                    "symbol": symbol,
                    "type": "Quote"
                }
            ]
        }
        self.send(data)

    async def request_candle(self, symbol: str, channel: int, fromtime: datetime.datetime, granularity: str = '1d', dump_feed=False):
        self.send(self.channel_request(channel, parameters={'contract': 'HISTORY'}))
        await self.channel_open_event.wait()
        self.channel_open_event.clear()
        candle_data = self.candle_format(
            symbol=symbol,fromtime=fromtime, granularity=granularity, channel=channel)
        self.send(candle_data, dump_feed=dump_feed)

    def send_order(self, order):
        response = self.session.post(endpoint=f"/accounts/{self.account_number}/orders", body=order)
        pass
