import json
import ssl
import rel
import time
import schedule
import websocket
import _thread

from api import FishPi
from core.chatroom import listener
from core.config import GLOBAL_CONFIG

__api = FishPi()
def on_message(ws, message):
    json_body = json.loads(message)
    listener(__api, json_body)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def heartbeat(ws):
    while True:
        time.sleep(60)
        ws.send("-hb-")
        if GLOBAL_CONFIG.repeat_config.soliloquize_switch:
            schedule.run_pending()


def on_open(ws):
    _thread.start_new_thread(heartbeat, (ws,))


def start(api: FishPi):
    global __api
    __api = api

    rel.safe_read()
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://fishpi.cn/chat-room-channel?apiKey=" + api.api_key,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel, sslopt={"cert_reqs": ssl.CERT_NONE})
    print("进入聊天室")
    rel.signal(2, rel.abort)
    rel.dispatch()
