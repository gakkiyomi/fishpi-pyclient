

import time
from src.api import FishPi
from src.utils.utils import *
from .config import GLOBAL_CONFIG


def render_user_info(userInfo):
    print("用户ID: " + userInfo['oId'])
    print("用户名: " + userInfo['userName'])
    print("用户签名: " + userInfo['userIntro'])
    print("用户编号: " + str(userInfo['userNo']))
    print("所在城市: " + userInfo['userCity'])
    print("用户积分: " + str(userInfo['userPoint']))
    print("在线时长: " + str(userInfo['onlineMinute']))


def render_online_users(api: FishPi):
    res = api.user.get_online_users()
    data = res['data']
    print('----------------------')
    print('| 聊天室在线人数: ' + str(data['onlineChatCnt']) + ' |')
    print('----------------------')
    for user in data['users']:
        print('用户: ' + user['userName'])
        print('----------------------')

def auto_check_in(api: FishPi):
    if len(api.api_key) == 0:
        print('未登录')
    else:
        api.user.get_yesterday_reward()

def login(api: FishPi):
    success = api.login(GLOBAL_CONFIG.auth_config.username,
                        GLOBAL_CONFIG.auth_config.password, GLOBAL_CONFIG.auth_config.mfa_code)
    if success:
        print(HELP)
    else:
        while len(api.api_key) == 0:
            time.sleep(3)
            if len(api.api_key) > 0:
                break
