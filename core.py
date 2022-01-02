
from os import system
import requests
import hashlib
import json
import websocket
import rel
import ssl
import _thread
import time
import configparser
import sys

API_KEY = ''

HOST = 'https://pwl.icu'

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'

RED_PACKET_SWITCH = True
NO_HEARTBEAT = False
USERNAME = ''
PASSWORD = ''


def init():
    global USERNAME,PASSWORD,NO_HEARTBEAT,RED_PACKET_SWITCH
    config = configparser.ConfigParser()
    try:
        config.read('./config.ini', encoding='utf-8')
        USERNAME = config.get('auth', 'username')
        PASSWORD = config.get('auth', 'password')
        RED_PACKET_SWITCH = config.getboolean('redPacket','openRedPacket')
        #NO_HEARTBEAT = config.getboolean('redPacket','openRedPacket')
    except:
        print("请检查配置文件是否合法")
        sys.exit(1)

def login(user,password):
    global API_KEY
    params = {'nameOrEmail': user,'userPassword':hashlib.md5(str(password).encode('utf-8')).hexdigest()}
    resp = requests.post(HOST + "/api/getKey",json=params,headers={'User-Agent': UA})
    body = json.loads(resp.text)

    if body['code'] == 0:
        print("登陆成功 Key:" + body['Key'])
        API_KEY = body['Key']
    else:
        printl("登陆失败: " + body['msg'])
        sys.exit(1)


def sysIn():
    while True:
      msg = input("")
      sendMsg(msg)       
    
    
def sendMsg(message):
    params = {'apiKey': API_KEY,'content':message}
    requests.post(HOST + "/chat-room/send",json=params,headers={'User-Agent': UA})

def openRedPacket(red_packet_id):
    params = {'apiKey': API_KEY,'oId':red_packet_id}
    requests.post(HOST + "/chat-room/red-packet/open",json=params,headers={'User-Agent': UA})

rel.safe_read()

def on_message(ws, message):
    json_body = json.loads(message)
    #json_formatted_str = json.dumps(json_body, indent=2)
    #print(json_formatted_str)
    if json_body['type'] == 'msg':
        if json_body['content'].find("redPacket") != -1:
            if(RED_PACKET_SWITCH):
                openRedPacket(json_body['oId'])
                print("红包助手: 恭喜，你抢到了一个红包!")
                #TODO 抢到的积分
            else:
                print("红包助手: 你错过了一个红包，请开启抢红包模式！")    
        else:
            print(json_body['userName']+ '说:' )
            print(json_body['md'])
    
def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def heartbeat(ws):

    while True:
        time.sleep(180)
        print("### heartbeat")
        ws.send("-hb-")

def on_open(ws):
    print("Opened connection")
    _thread.start_new_thread(heartbeat, (ws,))

if __name__ == "__main__":
    init()
    login(USERNAME,PASSWORD)
    _thread.start_new_thread(sysIn,())
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://pwl.icu/chat-room-channel?apiKey="+API_KEY,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(dispatcher=rel,sslopt={"cert_reqs":ssl.CERT_NONE})
    rel.signal(2, rel.abort)
    rel.dispatch()