# -*- coding: utf-8 -*-

import json

import requests

from src.api import Base
from src.utils import UA

from .config import GLOBAL_CONFIG


class UserAPI(Base):

    def __init__(self):
        self.reward = False

    def get_user_info(self, username: str) -> None | dict:
        if self.api_key == '':
            return None
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/user/{username}?apiKey={self.api_key}', headers={'User-Agent': UA})
        if resp.status_code == 200:
            data = json.loads(resp.text)
            if data.get('code') is not None and data['code'] == -1:
                print('此用户不存在: ' + username)
            else:
                return data
        else:
            print('此用户不存在: ' + username)

    def get_online_users(self) -> dict:
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/chat-room/online-users', headers={'User-Agent': UA})
        return json.loads(resp.text)

    def get_yesterday_reward(self) -> None:
        if self.reward == True:
            print('你已经领取过昨日活跃度奖励了')
            return
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/activity/yesterday-liveness-reward-api?apiKey={self.api_key}', headers={'User-Agent': UA})
        response = json.loads(resp.text)
        reward = response['sum']
        if reward == -1:
            print('你已经领取过昨日活跃度奖励了')
        else:
            print(f'领取昨日活跃度奖励 积分: {reward}')
        self.reward = True

    def send_breezemoon(self, content: str) -> None:
        res = requests.post(f'{GLOBAL_CONFIG.host}/breezemoon', headers={'User-Agent': UA}, json={
            'apiKey': self.api_key,
            'breezemoonContent': content
        })
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            print('清风明月发布成功')
        else:
            print(response['msg'])

    def get_breezemoons(self, username: str, page: int = 1, size: int = 10) -> dict | None:
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/api/user/{username}/breezemoons?p={page}&size={size}&apiKey={self.api_key}', headers={'User-Agent': UA})
        response = json.loads(resp.text)
        if 'code' in response and response['code'] == 0:
            return response['data']['breezemoons']
        else:
            print(response['msg'])
            return None

    def checked_status(self) -> dict:
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/user/checkedIn?apiKey={self.api_key}', headers={'User-Agent': UA})
        return json.loads(resp.text)

    def get_liveness_info(self) -> dict:
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/user/liveness?apiKey={self.api_key}', headers={'User-Agent': UA})
        return json.loads(resp.text)

    def transfer(self, to: str, amount: int = 32, memo: str = '给') -> None:
        resp = requests.post(f'{GLOBAL_CONFIG.host}/point/transfer', headers={'User-Agent': UA},
                             json={
            'apiKey': self.api_key,
            'userName': to,
            'amount': amount,
            'memo': memo
        })
        response = json.loads(resp.text)
        if 'code' in response:
            print('转账成功')
        else:
            print(response['msg'])

    def get_username_by_key(self, key: str) -> str | None:
        resp = requests.get(
            f'{GLOBAL_CONFIG.host}/api/user?apiKey={key}', headers={'User-Agent': UA})
        response = json.loads(resp.text)
        if 'data' in response:
            return response['data']['userName']
        else:
            return None
