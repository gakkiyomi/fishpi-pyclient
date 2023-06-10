import _thread
from .blacklist import *
from .config import GLOBAL_CONFIG
from .user import *
from .websocket import chatroom_out,init_chatroom
from src.utils.utils import *



def init_sys_in(api: FishPi):
    _thread.start_new_thread(console_input, (api,))


def console_input(api: FishPi):
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
            reward = api.get_yesterday_reward()['sum']
            if reward == -1:
                print('你已经领取过昨日活跃度奖励了')
            else:
                print(f'领取昨日活跃度奖励 积分: {reward}')
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
