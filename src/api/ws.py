# -*- coding: utf-8 -*-
import json
import ssl
import threading
from abc import ABC, abstractmethod

import websocket

from src.api import API


class WS(ABC):
    def __init__(self, ws_url: str, ws_calls: list[str]) -> None:
        self.ws_url = ws_url
        self.ws_calls = ws_calls

    @abstractmethod
    def on_open(self, obj):
        pass

    def on_error(self, obj, error):
        print(error)

    @abstractmethod
    def on_close(self, obj, close_status_code, close_msg):
        pass

    def on_message(self, obj, message):
        data = json.loads(message)
        for call in self.ws_calls:
            call(API, data)

    def start(self):
        threading.Thread(target=aysnc_start_ws, args=(self,)).start()

    def stop(self):
        self.instance.close()
        self.instance = None
        API.sockpuppets[API.current_user].ws.pop(self.ws_url)
        self.ws_calls = None
        self.ws_url = None


def aysnc_start_ws(ws: WS):
    websocket.enableTrace(False)
    ws_instance = websocket.WebSocketApp(f"wss://{ws.ws_url}?apiKey={API.api_key}",
                                         on_open=ws.on_open,
                                         on_message=ws.on_message,
                                         on_error=ws.on_error,
                                         on_close=ws.on_close)
    ws.instance = ws_instance
    API.sockpuppets[API.current_user].ws[ws.ws_url] = ws
    ws_instance.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
