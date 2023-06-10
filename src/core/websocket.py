import json
import ssl
import _thread
import schedule
import websocket

from src.api import FishPi
from .chatroom import listener
from .config import GLOBAL_CONFIG

__api = FishPi()
def on_message(ws, message):
    json_body = json.loads(message)
    listener(__api, json_body)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("已经离开聊天室,可以执行命令 #chatroom 重新进入聊天室")



def on_open(ws):
    print(f'欢迎{__api.current_user}进入聊天室!')
    if len(GLOBAL_CONFIG.chat_config.blacklist) > 0:
        print('小黑屋成员: ' + str(GLOBAL_CONFIG.chat_config.blacklist))
    if GLOBAL_CONFIG.chat_config.soliloquize_switch:
            schedule.run_pending()

def chatroom_out(api: FishPi):
    api.ws.close()
    api.ws = None

def chatroom_in(api: FishPi):
    global __api
    __api = api
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://fishpi.cn/chat-room-channel?apiKey=" + api.api_key,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    api.ws = ws
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
def init_chatroom(api: FishPi):
    _thread.start_new_thread(chatroom_in, (api,))    