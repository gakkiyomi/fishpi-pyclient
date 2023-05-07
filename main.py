# -*- coding: utf-8 -*-
import time
import json
from core import __init__
from core.blacklist import ban_someone, unban_someone
from core.chat import repeat, soliloquize
from core.config import GLOBAL_CONFIG
from core.redpacket import rush_redpacket
from core.user import render_online_users, render_user_info
import websocket
import rel
import ssl
import _thread
import schedule
from core.version import __version__
from api import FishPi


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


API: FishPi = FishPi()


def init():
    __init__()


def sysIn():
    while True:
        msg = input("")
        if msg == '#help':
            print(COMMAND_GUIDE)
        elif len(API.api_key) == 0:
            API.login(GLOBAL_CONFIG.auth_config.username,
                      GLOBAL_CONFIG.auth_config.password, msg)
        elif msg == '#checked':
            if API.user.checked_status()['checkedIn']:
                print('今日你已签到！')
            else:
                print('今日还未签到，摸鱼也要努力呀！')
        elif msg == '#reward':
            if API.get_yesterday_reward()['sum'] == -1:
                print('你已经领取过昨日活跃度奖励了')
            else:
                print('领取昨日活跃度奖励 积分: ' +
                      str(API.user.get_liveness_info()['sum']))
        elif msg == '#liveness':
            print('当前活跃度: ' +
                  str(API.user.get_liveness_info()['liveness']))
        elif msg == '#point':
            print(
                '当前积分: ' + str(API.user.get_user_info(GLOBAL_CONFIG.auth_config.username)['userPoint']))
        elif msg == '#online-users':
            render_online_users()
        elif msg.startswith('#user '):
            user = msg.split()[1]
            userInfo = API.user.get_user_info(user)
            if userInfo is not None:
                render_user_info(userInfo)
        elif msg == '#blacklist':
            print(GLOBAL_CONFIG.repead_config.blacklist)
        elif msg.startswith('#ban '):
            user = msg.split()[1]
            ban_someone(API, user)
        elif msg.startswith('#unban '):
            user = msg.split()[1]
            unban_someone(API, user)
        else:
            API.chatroom.send(msg)


rel.safe_read()


def renderMsg(message):
    if message['type'] == 'msg':
        if message['content'].find("redPacket") != -1:
            rush_redpacket(API, message)
        else:
            time = message['time']
            user = message['userName']
            if len(GLOBAL_CONFIG.repead_config.blacklist) > 0 and GLOBAL_CONFIG.repead_config.blacklist.__contains__(user):
                return
            if user == GLOBAL_CONFIG.auth_config.username:
                print('\t\t\t\t\t\t[' + time + ']')
                print('\t\t\t\t\t\t你说: ' + message['md'])
            else:
                print('[' + time + ']')
                print(user + '说:')
                print(message['md'])
                print('\r\n')
            if GLOBAL_CONFIG.repead_config.repeat_mode_switch:
                msg = message['md']
                repeat(API, msg)


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
    _thread.start_new_thread(sysIn, ())
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
