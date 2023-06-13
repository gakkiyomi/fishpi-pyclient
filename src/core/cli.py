import re
from .blacklist import *
from .config import GLOBAL_CONFIG
from .user import *
from .websocket import chatroom_out,init_chatroom
from src.api.redpacket import *
from src.utils.utils import *



def __send_redpacket_handler(api :FishPi, msg :str):
        if  msg == "#rp":
               api.chatroom.send_redpacket()
        elif msg == "#rp-ave":
               api.chatroom.send_redpacket(RedPacket('不要抢,人人有份!', 32, 5, RedPacketType.AVERAGE))
        elif msg == "#rp-hb":
               api.chatroom.send_redpacket(RedPacket('玩的就是心跳!', 32, 5, RedPacketType.HEARTBEAT))
        elif msg == "#rp-rps":
               api.chatroom.send_redpacket(RPSRedPacket('剪刀石头布!', 32, 0))
        elif msg.startswith('#rp-to'):
            res = re.fullmatch(RP_SEND_TO_CODE_RE, msg)
            if res is not None:
                api.chatroom.send_redpacket(SpecifyRedPacket('听我说谢谢你,因为有你,温暖了四季!', res.group(1), res.group(2).replace('，',',').split(",")))
            else:
                print('非法红包指令')               
        elif msg.startswith('#rp-ave'):
            res = re.fullmatch(RP_AVER_CODE_RE,msg)
            if res is not None:
                api.chatroom.send_redpacket(RedPacket('不要抢,人人有份!', res.group(2), res.group(1), RedPacketType.AVERAGE))
            else:
                print('非法红包指令')       
        elif msg.startswith('#rp-hb'):
            res = re.fullmatch(RP_HB_CODE_RE,msg)
            if res is not None:
                api.chatroom.send_redpacket(RedPacket('玩的就是心跳!', res.group(2), res.group(1), RedPacketType.HEARTBEAT))
            else:
                print('非法红包指令')
        elif msg.startswith('#rp-rps'):
            if msg.startswith('#rp-rps-limit'):
                try:
                    limit = msg.split(' ')[1]
                    GLOBAL_CONFIG.redpacket_config.rps_limit = int(limit)
                    print(f'猜拳红包限制设置{limit}成功')
                except Exception:
                    print('非法红包指令')
            else:
                res = re.fullmatch(RP_RPS_CODE_RE,msg)
                if res is not None:
                    api.chatroom.send_redpacket(RPSRedPacket('剪刀石头布!', res.group(2), res.group(1)))
                else:
                    print('非法红包指令')
        elif msg.startswith('#rp-time'):
            res = re.fullmatch(RP_TIME_CODE_RE,msg)
            if res is not None:
                time = res.group(1)
                GLOBAL_CONFIG.redpacket_config.rate = int(time)
                print(f'红包等待时间已设置成功 {time}s')
            else:
                print('非法红包指令')
        elif msg.startswith('#rp'):
            res = re.fullmatch(RP_CODE_RE,msg)
            if res is not None:
                api.chatroom.send_redpacket(RedPacket('那就看运气吧!', res.group(2), res.group(1), RedPacketType.RANDOM))
            else:
                print('非法红包指令')
                    


def cli_handler(api: FishPi):
    while True:
        msg = input("")
        if msg == '#help':
            print(COMMAND_GUIDE)
        elif len(api.api_key) == 0:
            api.login(GLOBAL_CONFIG.auth_config.username,
                      GLOBAL_CONFIG.auth_config.password, msg)                
        elif msg == '#cli':
            if api.ws == None:
                print("已经进入交互模式了")
            else:    
                chatroom_out(api)
                print("进入交互模式")
        elif msg == '#chatroom':
            if api.ws == None:
               init_chatroom(api)
            else:
               chatroom_out(api)
               init_chatroom(api)
        elif msg.startswith('#bm'):
            api.user.send_breezemoon(msg[msg.find(' ')+1:len(msg)])
        elif msg == '#api-key':
            print(api.api_key)
        elif msg.startswith('#transfer'):
            res = re.fullmatch(TRANSFER_RE, msg)
            if res is not None:
                api.user.transfer(res.group(2), res.group(1), res.group(3))
            else:
               print('非法转账命令')    
        elif msg.startswith('#rp'):
            __send_redpacket_handler(api, msg)                                   
        elif msg == '#answer':
            if GLOBAL_CONFIG.chat_config.answerMode:
                GLOBAL_CONFIG.chat_config.answerMode = False
                print('退出答题模式')
            else:
                GLOBAL_CONFIG.chat_config.answerMode = True
                print('进入答题模式')
        elif msg == '#checked':
            if api.user.checked_status()['checkedIn']:
                print('今日你已签到！')
            else:
                print('今日还未签到，摸鱼也要努力呀！')
        elif msg == '#reward':
            api.user.get_yesterday_reward()
        elif msg == '#liveness':
            print('当前活跃度: ' +
                  str(api.user.get_liveness_info()['liveness']))
        elif msg == '#point':
            print('当前积分: ' + str(api.user.get_user_info(GLOBAL_CONFIG.auth_config.username)['userPoint']))
        elif msg == '#online-users':
            render_online_users(api)
        elif msg.startswith('#user '):
            user = msg.split()[1]
            userInfo = api.user.get_user_info(user)
            if userInfo is not None:
                render_user_info(userInfo)
        elif msg == '#blacklist':
            print(GLOBAL_CONFIG.chat_config.blacklist)
        elif msg.startswith('#ban '):
            user = msg.split()[1]
            ban_someone(api, user)
        elif msg.startswith('#unban '):
            user = msg.split()[1]
            unban_someone(api, user)
        elif msg.startswith('#'):
            print('命令错误,请查看命令引导手册')
            print(COMMAND_GUIDE)
        else:
            if api.ws is not None:
                if GLOBAL_CONFIG.chat_config.answerMode:
                    api.chatroom.send(f'鸽 {msg}')
                else:
                    api.chatroom.send(msg)
            else:
                print("请输入正确指令")        
