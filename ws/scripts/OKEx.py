import asyncio, base64, datetime, hmac, json, time, zlib
from asgiref.sync import sync_to_async

from libs_exchange_handler.og_exception import *
from rest_framework.exceptions import ValidationError
from .userInfo import UserInfo

import requests
import websockets
import uuid

async def getClient(ogUserId):
    # keys = userInfo.getUserKey(request.user.id)
    print(ogUserId)
    userInfo = UserInfo()
    keys = await userInfo.getUserKey(ogUserId)
    if keys is None:
        raise OgException('Invalid User', status_code=400)

    return OKExClient(**keys)

class OKExClient():
    def __init__(self, **keys):
        self.api_key = keys.get('wallet_key')
        self.secret_key = keys.get('wallet_secret')
        self.passphrase = keys.get('tag')
        self.flag = '0'
            
    def get_timestamp(self):
        now = datetime.datetime.now()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    def login_params(self):
        try:
            timestamp = str(self.get_local_timestamp())
            message = timestamp + 'GET' + '/users/self/verify'

            mac = hmac.new(bytes(self.secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
            d = mac.digest()
            sign = base64.b64encode(d)

            login_param = {"op": "login", "args": [{"apiKey": self.api_key,
                                                    "passphrase": self.passphrase,
                                                    "timestamp": timestamp,
                                                    "sign": sign.decode("utf-8")}]}
            login_str = json.dumps(login_param)
            return login_str
        except Exception as e:
            print(e)
            return 'Socket Login Error'

    def get_local_timestamp(self):
        return int(time.time())
    
    def get_ws(self):
        return self.ws

    """
    {
    "id": "1512",
    "op": "order",
    "args": [
        {
        "side": "buy",
        "instId": "BTC-USDT",
        "tdMode": "isolated",
        "ordType": "market",
        "sz": "100"
        }
    ]
    }
    """
    async def order(self, data, ogSocket):
        param = {
            "id": str(uuid.uuid4().hex),
            "op": "order",
            "args": [
                data
            ]
        }

        res = await self.ws.send(json.dumps(param))

        await ogSocket.send(text_data=json.dumps({"response": res}))

    async def subscribe(self, url, channels, ogSocket):
        while True:
            try:
                async with websockets.connect(url) as ws:
                    # login
                    timestamp = str(self.get_local_timestamp())
                    login_str = self.login_params()
                    await ws.send(login_str)
                    # print(f"send: {login_str}")
                    res = await ws.recv()
                    # print(res)

                    # subscribe
                    sub_param = {"op": "subscribe", "args": channels}
                    sub_str = json.dumps(sub_param)
                    await ws.send(sub_str)
                    # print(f"send: {sub_str}")
                    self.ws = ws

                    while True:
                        try:
                            res = await asyncio.wait_for(ws.recv(), timeout=25)
                        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                            try:
                                await ws.send('ping')
                                res = await ws.recv()
                                # print(res)
                                continue
                            except Exception as e:
                                print("error sub")
                                break

                        resObj = json.loads(res)
                        
                        if json.loads(res).get('data') != None:
                            data = []
                            for position in json.loads(res).get('data'):
                                if position.get('adl') != "":
                                    resObj.get('arg')['close'] = False
                                else:
                                    resObj.get('arg')['close'] = True
                                
                        # print(self.get_timestamp() + res)
                        await ogSocket.send(text_data=json.dumps({"response": resObj}))

            except Exception as e:
                print("error main", e)
                continue