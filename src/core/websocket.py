import json
import ssl
import _thread
import schedule
import websocket

from src.api import API,FishPi
from .config import GLOBAL_CONFIG


def on_message(ws, message):
    data = json.loads(message)
    for call in API.ws_calls:
        call(API, data)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("已经离开聊天室,可以执行命令 #chatroom 重新进入聊天室")



def on_open(ws):
    print(f'欢迎{API.current_user}进入聊天室!')
    if len(GLOBAL_CONFIG.chat_config.blacklist) > 0:
        print('小黑屋成员: ' + str(GLOBAL_CONFIG.chat_config.blacklist))
    if GLOBAL_CONFIG.chat_config.soliloquize_switch:
            schedule.run_pending()

def chatroom_out(api: FishPi):
    api.ws.close()
    api.ws = None
      

def __chatroom_in(api :FishPi):
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://fishpi.cn/chat-room-channel?apiKey=" + api.api_key,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    api.ws = ws
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
def init_chatroom(api: FishPi):
    _thread.start_new_thread(__chatroom_in, (api,))