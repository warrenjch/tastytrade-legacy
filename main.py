from api import *
from dxlink import *
import time

config = Config(prod=False)
session = API(config)
session.login()
print("Logged in", session.user_data)
session.get_dxlink()
stream = DXLink(url = session.dxlink_url, auth_token= session.dxlink_token)
data = {"type": "FEED_SUBSCRIPTION",
        "channel": 1,
        "add": [
            {
                "symbol": "NVDA",
                "type": "Quote"
            }
        ]
        }
time.sleep(5)
stream.send(data)