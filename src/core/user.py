# -*- coding: utf-8 -*-

from src.api import FishPi


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
