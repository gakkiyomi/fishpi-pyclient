# -*- coding: utf-8 -*-
import time
import json
from core import __init__
from core.chatroom import listener, soliloquize
from core.cli import HELP, consle_input
from core.config import GLOBAL_CONFIG
import websocket
import rel
import ssl
import _thread
import schedule
from core.version import __version__
from api import FishPi


API: FishPi = FishPi()


def init():
    __init__()


rel.safe_read()


def on_message(ws, message):
    json_body = json.loads(message)
    listener(API, json_body)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def heartbeat(ws):
    while True:
        time.sleep(60)
        ws.send("-hb-")
        if GLOBAL_CONFIG.repead_config.soliloquize_switch:
            schedule.run_pending()


def on_open(ws):
    _thread.start_new_thread(heartbeat, (ws,))


if __name__ == "__main__":
    init()
    if GLOBAL_CONFIG.repead_config.soliloquize_switch:
        schedule.every(GLOBAL_CONFIG.repead_config.soliloquize_frequency).minutes.do(
            soliloquize, API)
    success = API.login(GLOBAL_CONFIG.auth_config.username,
                        GLOBAL_CONFIG.auth_config.password, '')
    _thread.start_new_thread(consle_input, (API,))
    if success:
        print(HELP)
        if len(GLOBAL_CONFIG.repead_config.blacklist) > 0:
            print('小黑屋成员: ' + str(GLOBAL_CONFIG.repead_config.blacklist))
    else:
        while len(API.api_key) == 0:
            time.sleep(3)
            if len(API.api_key) > 0:
                break
    print("进入聊天室")
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://fishpi.cn/chat-room-channel?apiKey="+API.api_key,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel, sslopt={"cert_reqs": ssl.CERT_NONE})
    rel.signal(2, rel.abort)
    rel.dispatch()
