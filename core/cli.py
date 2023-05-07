import _thread
from core.blacklist import *
from core.config import GLOBAL_CONFIG
from core.user import *
from utils.utils import *




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
        elif msg == '#checked':
            if api.user.checked_status()['checkedIn']:
                print('今日你已签到！')
            else:
                print('今日还未签到，摸鱼也要努力呀！')
        elif msg == '#reward':
            if api.get_yesterday_reward()['sum'] == -1:
                print('你已经领取过昨日活跃度奖励了')
            else:
                print('领取昨日活跃度奖励 积分: ' +
                      str(api.user.get_liveness_info()['sum']))
        elif msg == '#liveness':
            print('当前活跃度: ' +
                  str(api.user.get_liveness_info()['liveness']))
        elif msg == '#point':
            print(
                '当前积分: ' + str(api.user.get_user_info(GLOBAL_CONFIG.auth_config.username)['userPoint']))
        elif msg == '#online-users':
            render_online_users()
        elif msg.startswith('#user '):
            user = msg.split()[1]
            userInfo = api.user.get_user_info(user)
            if userInfo is not None:
                render_user_info(userInfo)
        elif msg == '#blacklist':
            print(GLOBAL_CONFIG.repeat_config.blacklist)
        elif msg.startswith('#ban '):
            user = msg.split()[1]
            ban_someone(api, user)
        elif msg.startswith('#unban '):
            user = msg.split()[1]
            unban_someone(api, user)
        else:
            api.chatroom.send(msg)
