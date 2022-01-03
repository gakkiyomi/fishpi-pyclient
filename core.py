
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
HEARTBEAT = False
HEARTBEAT_SMART_MODE = False
HEARTBEAT_THRESHOLD = 0.5
HEARTBEAT_ADVENTURE = False
HEARTBEAT_TIMEOUT = 5
MAX_HEARTBEAT_TIMEOUT = 20
RATE = 3
USERNAME = ''
PASSWORD = ''


def init():
    global USERNAME,PASSWORD,HEARTBEAT,RED_PACKET_SWITCH,RATE,HEARTBEAT_SMART_MODE,HEARTBEAT_THRESHOLD,HEARTBEAT_TIMEOUT,HEARTBEAT_ADVENTURE
    config = configparser.ConfigParser()
    try:
        config.read('./config.ini', encoding='utf-8')
        USERNAME = config.get('auth', 'username')
        PASSWORD = config.get('auth', 'password')
        RATE =  RATE if config.getint('redPacket', 'rate') < RATE else config.getint('redPacket', 'rate')
        RED_PACKET_SWITCH = config.getboolean('redPacket','openRedPacket')
        HEARTBEAT = config.getboolean('redPacket','heartbeat')
        HEARTBEAT_SMART_MODE = config.getboolean('redPacket','heartbeatSmartMode')
        HEARTBEAT_ADVENTURE = config.getboolean('redPacket','heartbeatAdventure')
        HEARTBEAT_THRESHOLD = config.getfloat('redPacket', 'heartbeatThreshold')
        if HEARTBEAT_THRESHOLD < 0:
            HEARTBEAT_THRESHOLD == 0.4
        elif HEARTBEAT_THRESHOLD >1:
            HEARTBEAT_THRESHOLD == 1
        HEARTBEAT_TIMEOUT =  config.getint('redPacket', 'heartbeatTimeout')    
        if HEARTBEAT_TIMEOUT > MAX_HEARTBEAT_TIMEOUT:
            HEARTBEAT_THRESHOLD == MAX_HEARTBEAT_TIMEOUT
        elif HEARTBEAT_THRESHOLD < 0:
            HEARTBEAT_THRESHOLD == 5
        
    except:
        print("请检查配置文件是否合法")
        sys.exit(1)

def login(user,password):
    global API_KEY
    params = {'nameOrEmail': user,'userPassword':hashlib.md5(str(password).encode('utf-8')).hexdigest()}
    resp = requests.post(HOST + "/api/getKey",json=params,headers={'User-Agent': UA})
    body = json.loads(resp.text)

    if body['code'] == 0:
        print("登陆成功 欢迎" + USERNAME + '进入聊天室!')
        print("更多功能与趣味游戏请访问网页端: " + HOST)
        API_KEY = body['Key']
    else:
        print("登陆失败: " + body['msg'])
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
    resp = requests.post(HOST + "/chat-room/red-packet/open",json=params,headers={'User-Agent': UA})
    who = json.loads(resp.text)['who']
    for i in who:
        if i['userName'] == USERNAME:
            if i['userMoney'] < 0:
                print("红包助手: 悲剧，你竟然被反向抢了红包("+ str(i['userMoney']) +")!")
            elif i['userMoney'] == 0:
                print("红包助手: 零溢事件，抢到了一个空的红包("+ str(i['userMoney']) +")!")
            else:
                print("红包助手: 恭喜，你抢到了一个红包("+ str(i['userMoney']) +")!")
            return i['userMoney']
    print("红包助手: 遗憾，比别人慢了一点点，建议换宽带!")        
    return 0

def analyzeHeartbeatRedPacket(red_packet_id):
    resp = requests.get(HOST + "/chat-room/more?page=1",headers={'User-Agent': UA})
    res = json.loads(resp.text)
    for data in res['data']:
        if data['oId'] == red_packet_id:
           analyze(json.loads(data['content']),red_packet_id,data['time'],data['userName'])
           return
    print("红包助手: 你与此红包无缘")         

def analyze(redPacket,red_packet_id,redPacketCreateTime,sender):
    count = redPacket['count']
    got = redPacket['got']
    if redPacket['count'] == redPacket['got']:
        print('红包助手: '+sender+' 发送的心跳红包, 遗憾没有抢到，比别人慢了一点点，建议换宽带!')
        return

    probability = 1 / (count - got)
    for get in redPacket['who']:
        if get['userMoney'] > 0:
           print('红包助手: '+sender+' 发送的心跳红包已无效，智能跳坑！')
           return   
    print('红包助手: 此心跳红包的中奖概率为:'+str(probability))    
    if probability >= HEARTBEAT_THRESHOLD:
        openRedPacket(red_packet_id)
    #还未结束，递归操作
    else:
        timeArray = time.strptime(redPacketCreateTime, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        if int(time.time()) - timeStamp > HEARTBEAT_TIMEOUT: # 递归将在1秒钟后结束
            if HEARTBEAT_ADVENTURE:
                print("红包助手: 超时了，干了兄弟们！")
                openRedPacket(red_packet_id)
            else:
                print("红包助手: 忍住了，他们血亏，我看戏！")    
            return
        analyzeHeartbeatRedPacket(red_packet_id)

rel.safe_read()

def renderRedPacket(redPacket):
    sender = redPacket['userName']
    content = json.loads(redPacket['content'])
    if content['type'] == 'heartbeat':
        if HEARTBEAT:
            if HEARTBEAT_SMART_MODE:
                print('红包助手: ' + sender +' 发了一个心跳红包') 
                analyzeHeartbeatRedPacket(redPacket['oId'])
                return
            openRedPacket(redPacket['oId'])
        else:
            print('红包助手: '+sender+' 发送了一个心跳红包, 你跳过了这个心跳红包！不尝试赌一下人品吗？')
    else:
        print('红包助手: '+sender+' 发送了一个红包, 但社区规定，助手抢红包要等'+str(RATE)+'秒哦～')
        time.sleep(RATE)
        openRedPacket(redPacket['oId'])

def renderMsg(message):
    if message['type'] == 'msg':
        if message['content'].find("redPacket") != -1:
            sender = message['userName']
            if(RED_PACKET_SWITCH):
                renderRedPacket(message)
            else:
                print('红包助手: '+sender+'发送了一个红包 你错过了这个红包，请开启抢红包模式！')    
        else:
            time = message['time']
            user = message['userName']
            if user == USERNAME:
                print('\t\t\t\t\t\t[' + time +']')
                print('\t\t\t\t\t\t你说: ' + message['md'])
            else:
                print('[' + time +']')
                print(user + '说:' )
                print(message['md'])
                print('\r\n')

def on_message(ws, message):
    json_body = json.loads(message)
    renderMsg(json_body)
    
def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def heartbeat(ws):
    while True:
        time.sleep(180)
        ws.send("-hb-")

def on_open(ws):
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