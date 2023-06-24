from src.api import FishPi
import json
import time
import enum
from src.utils.utils import RPS_LOSED, RPS_ZERO, RPS_SUCCESS
from .config import GLOBAL_CONFIG

CODE = enum.Enum('REDPACKET_CODE', ['SUCCESS', 'LOSED', 'NOT_ME', "ZERO"])


def __open_redpacket_render(username, redpacket: dict) -> CODE:
    who = redpacket['who']
    sender = redpacket['info']['userName']
    for i in who:
        if i['userName'] == username:
            if i['userMoney'] < 0:
                print(f"红包助手: 悲剧，你竟然被{sender}反向抢了红包({str(i['userMoney'])})积分!")
                return CODE.LOSED
            elif i['userMoney'] == 0:
                print(f"红包助手: 零溢事件，{sender}的红包抢到了({str(i['userMoney'])})积分!")
                return CODE.ZERO
            else:
                print(f"红包助手: 恭喜，你抢到了{sender}的红包({str(i['userMoney'])})积分!")
                return CODE.SUCCESS
    print(f"红包助手: 遗憾 {sender}的红包没有抢到，比别人慢了一点点，建议换宽带!")
    return CODE.NOT_ME


def open_red_packet(api: FishPi, red_packet_id) -> None:
    resp_json = api.chatroom.open_redpacket(red_packet_id)
    if ('code' in resp_json and resp_json['code'] == -1):
        print(resp_json['msg'])
        return
    __open_redpacket_render(api.current_user, resp_json)


def open_rock_paper_scissors_packet(api: FishPi, red_packet_id) -> None:
    resp_json = api.chatroom.open_rock_paper_scissors_redpacket(red_packet_id)
    if ('code' in resp_json and resp_json['code'] == -1):
        print(resp_json['msg'])
        return
    code = __open_redpacket_render(api.current_user, resp_json)
    if code == CODE.SUCCESS:
        api.chatroom.send(RPS_SUCCESS)
    elif code == CODE.LOSED:
        api.chatroom.send(RPS_LOSED)
    elif code == CODE.ZERO:
        api.chatroom.send(RPS_ZERO)

def render_redpacket(api: FishPi, message :dict) -> None:
    if message['type'] != 'redPacketStatus':
        return
    sender = message['whoGive']
    goter = message['whoGot']
    if sender == api.current_user:
        if goter != sender:
            print(f"红包助手: {goter} 领取了你的红包!")
    else:
        return

def rush_redpacket(api: FishPi, redpacket):
    sender = redpacket['userName']
    content = json.loads(redpacket['content'])
    if sender == api.current_user:
        print('\t\t\t\t\t\t[' + redpacket['time'] + ']')
        print('\t\t\t\t\t\t发送了一个红包')
        if content['type'] not in ['rockPaperScissors','heartbeat']:
            open_red_packet(api, redpacket['oId'])
        return
    if (GLOBAL_CONFIG.redpacket_config.red_packet_switch == False):
        print(f'红包助手: {sender}发送了一个红包 你错过了这个红包，请开启抢红包模式！')
        return
    if content['type'] == 'heartbeat':
        if GLOBAL_CONFIG.redpacket_config.heartbeat:
            if GLOBAL_CONFIG.redpacket_config.smart_mode:
                print(f'红包助手: {sender}发了一个心跳红包')
                __analyzeHeartbeatRedPacket(api, redpacket['oId'])
                return
            open_red_packet(api, redpacket['oId'])
        else:
            print(f'红包助手: {sender}发送了一个心跳红包, 你选择跳过了这个心跳红包！不尝试赌一下人品吗？')
            return
    if content['type'] == 'rockPaperScissors':
        print(
            f'红包助手: {sender} 发送了一个猜拳红包, 但社区规定，助手抢红包要等{GLOBAL_CONFIG.redpacket_config.rate}秒哦～')
        time.sleep(GLOBAL_CONFIG.redpacket_config.rate)
        print('红包助手正在帮你猜拳，石头剪刀布！')
        money = content['money']
        if money > GLOBAL_CONFIG.redpacket_config.rps_limit:
            print(f'红包助手: {sender} 发送了一个积分为({money})的猜拳红包, 怂了 不敢赌～')
        else:
            open_rock_paper_scissors_packet(api, redpacket['oId'])
    else:
        print(f'红包助手: {sender} 发送了一个红包, 但社区规定，助手抢红包要等' +
              str(GLOBAL_CONFIG.redpacket_config.rate)+'秒哦～')
        time.sleep(GLOBAL_CONFIG.redpacket_config.rate)
        open_red_packet(api, redpacket['oId'])


def __analyzeHeartbeatRedPacket(api: FishPi, red_packet_id):
    for data in api.chatroom.more()['data']:
        if data['oId'] == red_packet_id:
            if data['content']:
                __analyze(api, json.loads(data['content']), red_packet_id, data['time'], data['userName'])
            else:
                return
        return    
    print("红包助手: 你与此红包无缘")


def __analyze(api: FishPi, packet, red_packet_id, ctime, sender):
    count = packet['count']
    got = packet['got']
    if packet['count'] == packet['got']:
        print(f'红包助手: {sender} 发送的心跳红包, 遗憾没有抢到，比别人慢了一点点，建议换宽带!')
        return

    probability = 1 / (count - got)
    for get in packet['who']:
        if get['userMoney'] > 0:
            print('红包助手: '+sender+' 发送的心跳红包已无效，智能跳坑！')
            return
    print(f'红包助手: 此心跳红包的中奖概率为:{str(probability)}')
    if probability >= GLOBAL_CONFIG.redpacket_config.threshold:
        open_red_packet(api, red_packet_id)
    else:
        timeArray = time.strptime(ctime, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        if int(time.time()) - timeStamp > GLOBAL_CONFIG.redpacket_config.timeout:
            if GLOBAL_CONFIG.redpacket_config.adventure_mode:
                print("红包助手: 超时了，干了兄弟们！")
                open_red_packet(api, red_packet_id)
            else:
                print("红包助手: 忍住了，他们血亏，我看戏！")
            return
        # 递归分析
        __analyzeHeartbeatRedPacket(api, red_packet_id)
