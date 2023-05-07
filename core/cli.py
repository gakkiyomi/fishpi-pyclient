from api import FishPi
from core.blacklist import *
from core.config import GLOBAL_CONFIG
from core.user import *


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




def consle_input(api:FishPi):
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
            print(GLOBAL_CONFIG.repead_config.blacklist)
        elif msg.startswith('#ban '):
            user = msg.split()[1]
            ban_someone(api, user)
        elif msg.startswith('#unban '):
            user = msg.split()[1]
            unban_someone(api, user)
        else:
            api.chatroom.send(msg)