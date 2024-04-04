import json
import websocket
import threading
import pandas as pd
import datetime
from auxiliary import *
from dbhandler import *

class DXLink():
    socket: websocket.WebSocketApp = None
    url: str = None
    auth_token: str = None
    auth_state: str = None
    user_id: str = None
    dump_feed: bool = False
    candle_symbol: str = None

    def __init__(self, url: str = None, auth_token: str = None):
        self.url = url
        self.auth_token = auth_token
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
                    self.send(self.channel_request(1))
            case "KEEPALIVE":
                self.send({"type": "KEEPALIVE"})
            case "FEED_DATA":
                if self.dump_feed == True:
                    if self.candle_symbol is None:
                        print('ERROR: candle symbol is None')
                        pass
                    else:
                        cs = self.candle_symbol
                        self.DB = DBHandler()
                        self.DB.modify_table(table_name=cs,jsonobject=message["data"],if_exists="append")



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

    def candle_format(self, symbol: str, fromtime: datetime.datetime, granularity: str = None, channel: int = 3):
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
        self.candle_symbol = symbol
        return data