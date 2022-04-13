# -*- coding: utf-8 -*-
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
import schedule
import random
import re

API_KEY = ''

HOST = 'https://fishpi.cn'

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'

RED_PACKET_SWITCH = True
HEARTBEAT = False
HEARTBEAT_SMART_MODE = False
HEARTBEAT_THRESHOLD = 0.5
HEARTBEAT_ADVENTURE = False
HEARTBEAT_TIMEOUT = 5
MAX_HEARTBEAT_TIMEOUT = 20
REPEAT_MODE = False
REPEAT_FREQUENCY = 3
RATE = 3
USERNAME = ''
PASSWORD = ''
SENTENCES = ['你们好！','牵着我的手，闭着眼睛走你也不会迷路。','吃饭了没有?','💗 爱你哟！']
BLACK_LIST = []
SOLILOQUIZE_MODE = True
SOLILOQUIZE_FREQUENCY = 20

HELP = '输入#help获得命令提示列表'


COMMAND_GUIDE = '''[#checked] 查看当前是否签到
[#reward] 领取昨日活跃奖励
[#point] 查看当前个人积分
[#online-users] 查看当前在线的用户列表
[#user username] 输入 #user 用户名 可查看此用户详细信息 (#user Gakkiyomi)
[#blacklist] 查看黑名单列表
[#ban username] 将某人送入黑名单
[#unban username] 将某人解除黑名单
[#liveness] 查看当前活跃度(⚠️慎用，如果频繁请求此命令(最少间隔30s)，登录状态会被直接注销,需要重启脚本！)
'''

REPEAT_POOL = {} #复读池

def init():
    global USERNAME,PASSWORD,HEARTBEAT,RED_PACKET_SWITCH,RATE,HEARTBEAT_SMART_MODE,HEARTBEAT_THRESHOLD,HEARTBEAT_TIMEOUT,HEARTBEAT_ADVENTURE,REPEAT_FREQUENCY,REPEAT_MODE,SENTENCES,SOLILOQUIZE_MODE,SOLILOQUIZE_FREQUENCY,BLACK_LIST
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
        REPEAT_MODE = config.getboolean('chat','repeatMode')
        REPEAT_FREQUENCY = config.getint('chat','repeatFrequency')
        SOLILOQUIZE_MODE = config.getboolean('chat','soliloquizeMode')
        SOLILOQUIZE_FREQUENCY = config.getint('chat','soliloquizeFrequency')
        appendList = json.loads(config.get('chat','sentences'))
        for i in appendList:
            SENTENCES.append(i)
        blacklist = json.loads(config.get('chat','blacklist'))
        for i in blacklist:
            BLACK_LIST.append(i)
        if BLACK_LIST.__contains__(''): 
            BLACK_LIST.remove('')
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

def getOnlineUsers():
    resp = requests.get(HOST + '/chat-room/online-users',headers={'User-Agent': UA})
    return json.loads(resp.text)

def getUserInfo(username):
    resp = requests.get(HOST + '/user/'+username+'?apiKey='+API_KEY,headers={'User-Agent': UA})
    if resp.status_code == 200:
        return json.loads(resp.text)
    else:
        print('此用户不存在: '+ username)  

def checkedStatus():
    resp = requests.get(HOST + '/user/checkedIn?apiKey='+API_KEY,headers={'User-Agent': UA})
    return json.loads(resp.text)

def getYesterdayReward():
    resp = requests.get(HOST + '/activity/yesterday-liveness-reward-api?apiKey='+API_KEY,headers={'User-Agent': UA})
    return json.loads(resp.text)

def getlivenessInfo():
    resp = requests.get(HOST + '/user/liveness?apiKey='+API_KEY,headers={'User-Agent': UA})
    return json.loads(resp.text) 

def sysIn():
    while True:
      msg = input("")
      if msg == '#help':
        print(COMMAND_GUIDE)
      elif msg == '#checked':
          if checkedStatus()['checkedIn']:
               print('今日你已签到！')  
          else:
               print('今日还未签到，摸鱼也要努力呀！')  
      elif msg == '#reward':
          if getYesterdayReward()['sum'] == -1:
               print('你已经领取过昨日活跃度奖励了')  
          else:
               print('领取昨日活跃度奖励 积分: ' + str(getYesterdayReward()['sum'])) 
      elif msg == '#liveness':
           print('当前活跃度: '+ str(getlivenessInfo()['liveness']))
      elif msg == '#point':
           print('当前积分: '+ str(getUserInfo(USERNAME)['userPoint']))
      elif msg == '#online-users':
           renderOnlineUsers()
      elif msg.startswith('#user '):
           user = msg.split( )[1]
           userInfo = getUserInfo(user)
           if userInfo is not None:
                renderUserInfo(userInfo)
      elif msg == '#blacklist':  
          print(BLACK_LIST)
      elif msg.startswith('#ban '):
          user = msg.split( )[1]
          banSomeone(user)
      elif msg.startswith('#unban '):
          user = msg.split( )[1]
          unbanSomeone(user)                
      else:
        sendMsg(msg)    
    
    
def sendMsg(message):
    params = {'apiKey': API_KEY,'content':message}
    requests.post(HOST + "/chat-room/send",json=params,headers={'User-Agent': UA})


def openRedPacket(red_packet_id,body):
    params = {'apiKey': API_KEY,'oId':red_packet_id} 
    if body:
       params.update(body)
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

def more():
    resp = requests.get(HOST + "/chat-room/more?page=1",headers={'User-Agent': UA})
    return json.loads(resp.text)


def analyzeRockPaperScissorsRedPacket(red_packet_id):
    for data in more()['data']:
        if data['oId'] == red_packet_id:
           res = analyze(json.loads(data['content']),red_packet_id,data['time'],data['userName'])
           openRedPacket(red_packet_id,{'gesture': str(res)})
           return
    print("红包助手: 你与此红包无缘")

def analyzeHeartbeatRedPacket(red_packet_id):
    for data in more()['data']:
        if data['oId'] == red_packet_id:
           analyze(json.loads(data['content']),red_packet_id,data['time'],data['userName'])
           return
    print("红包助手: 你与此红包无缘")         

def analyze(redPacket,red_packet_id,redPacketCreateTime,sender):
    count = redPacket['count']
    got = redPacket['got']
    redPacketType = redPacket['type']
    if redPacketType == 'rockPaperScissors':
       gesture = redPacket['gesture']
       if gesture == 0:
           return 2
       elif gesture == 1:
           return 0
       else:
           return 1
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
        openRedPacket(red_packet_id,{})
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


def renderUserInfo(userInfo):
    print("用户ID: "+ userInfo['oId'])
    print("用户名: "+ userInfo['userName'])
    print("用户签名: "+ userInfo['userIntro'])
    print("用户编号: "+ str(userInfo['userNo']))
    print("所在城市: "+ userInfo['userCity'])
    print("用户积分: "+ str(userInfo['userPoint']))
    print("在线时长: "+ str(userInfo['onlineMinute']))

def renderOnlineUsers():
    res = getOnlineUsers()
    data = res['data']
    print('----------------------')
    print('| 聊天室在线人数: ' + str(data['onlineChatCnt']) + ' |')
    print('----------------------')
    for user in data['users']:
        print('用户: ' + user['userName'])
        print('----------------------')

def renderRedPacket(redPacket):
    sender = redPacket['userName']
    content = json.loads(redPacket['content'])
    if content['type'] == 'heartbeat':
        if HEARTBEAT:
            if HEARTBEAT_SMART_MODE:
                print('红包助手: ' + sender +' 发了一个心跳红包') 
                analyzeHeartbeatRedPacket(redPacket['oId'])
                return
            openRedPacket(redPacket['oId'],{})
        else:
            print('红包助手: '+sender+' 发送了一个心跳红包, 你跳过了这个心跳红包！不尝试赌一下人品吗？')
    if content['type'] == 'rockPaperScissors':
       print('红包助手: '+sender+' 发送了一个猜拳红包, 红包助手正在帮你猜拳，石头剪刀布！')
       analyzeRockPaperScissorsRedPacket(redPacket['oId'])
    else:
        print('红包助手: '+sender+' 发送了一个红包, 但社区规定，助手抢红包要等'+str(RATE)+'秒哦～')
        time.sleep(RATE)
        openRedPacket(redPacket['oId'],{})

def repeat(msg):
    if REPEAT_POOL.__contains__(msg) == False:
        REPEAT_POOL.clear()
        REPEAT_POOL[msg] = 1
    elif REPEAT_POOL[msg] == REPEAT_FREQUENCY:
        sendMsg(msg)
        REPEAT_POOL[msg] = REPEAT_POOL[msg] + 1 
    else:
        REPEAT_POOL[msg] = REPEAT_POOL[msg] + 1

def unbanSomeone(userName):
    if BLACK_LIST.__contains__(userName) == False:
        print(userName + '不在黑名单中')
        return
    userInfo = getUserInfo(userName)
    if userInfo is None:
        return
    BLACK_LIST.remove(userName)
    #持久化到文件
    f_path = './config.ini'
    src = open(f_path, "r+")
    configText = src.read()
    src.close()
    dst = open('./config.ini', 'w')
    after = ''
    if len(BLACK_LIST) ==0 :
        after = r'blacklist=[""]'
    else:
        after = "blacklist="+ str(BLACK_LIST).replace("\'","\"")
    dst.write(re.sub(r'blacklist.*', after,configText))
    dst.close()
    print(userName + '已从小黑屋中释放')        

def banSomeone(userName):
    if BLACK_LIST.__contains__(userName):
        print(userName + ' 已在黑名单中')
        return
    userInfo = getUserInfo(userName)
    if userInfo is None:
        return   
    BLACK_LIST.append(userName)
    #持久化到文件
    f_path = './config.ini'
    src = open(f_path, "r+")
    configText = src.read()
    src.close()
    dst = open('./config.ini', 'w')
    after = "blacklist="+ str(BLACK_LIST).replace("\'","\"")
    dst.write(re.sub(r'blacklist.*', after,configText))
    dst.close()
    print(userName + '已加入到黑名单中')

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
            if len(BLACK_LIST) > 0 and BLACK_LIST.__contains__(user):
                return
            if user == USERNAME:
                print('\t\t\t\t\t\t[' + time +']')
                print('\t\t\t\t\t\t你说: ' + message['md'])
            else:
                print('[' + time +']')
                print(user + '说:' )
                print(message['md'])
                print('\r\n')
            if REPEAT_MODE:
                msg = message['md']
                repeat(msg)

def on_message(ws, message):
    json_body = json.loads(message)
    renderMsg(json_body)
    
def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def heartbeat(ws):
    while True:
        time.sleep(60)
        ws.send("-hb-")
        if SOLILOQUIZE_MODE:
            schedule.run_pending()

def soliloquize():
    length = len(SENTENCES)
    index = random.randint(0,length - 1)
    sendMsg(SENTENCES[index])

if SOLILOQUIZE_MODE:
    schedule.every(SOLILOQUIZE_FREQUENCY).minutes.do(soliloquize)

def on_open(ws):
    _thread.start_new_thread(heartbeat, (ws,))

if __name__ == "__main__":
    init()
    login(USERNAME,PASSWORD)
    _thread.start_new_thread(sysIn,())
    print(HELP)
    print('小黑屋成员: ' + str(BLACK_LIST))
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://fishpi.cn/chat-room-channel?apiKey="+API_KEY,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(dispatcher=rel,sslopt={"cert_reqs":ssl.CERT_NONE})
    rel.signal(2, rel.abort)
    rel.dispatch()
