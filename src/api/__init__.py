# -*- coding: utf-8 -*-

from .chatroom import ChatRoom
from src.utils.utils import UA, HOST
from .__api__ import Base
from .user import User
import sys
import requests
import hashlib
import json


class FishPi(Base):
    def __init__(self):
        self.ws_calls = []
        self.ws = None
        self.current_user = ''
        self.user = User()
        self.chatroom = ChatRoom()
        Base.__init__(self)

    def add_listener(self, listener):
        self.ws_calls.append(listener)

    def set_current_user(self, username):
        self.current_user = username

    def set_token(self, key):
        Base.set_token(self, key)
        self.user.set_token(key)
        self.chatroom.set_token(key)

    def login(self, username: str, password: str, mfa_code='') -> bool:
        params = {
            'nameOrEmail': username,
            'userPassword': hashlib.md5(str(password).encode('utf-8')).hexdigest(),
            'mfaCode': mfa_code
        }
        res = requests.post(f"{HOST}/api/getKey", json=params, headers={'User-Agent': UA})
        rsp = json.loads(res.text)
        if rsp['code'] == 0:
            self.set_token(rsp['Key'])
            self.set_current_user(username)
            print(f'登陆成功! 更多功能与趣味游戏请访问网页端: {HOST}')
            return True
        elif rsp['code'] == -1 and rsp['msg'] == '两步验证失败，请填写正确的一次性密码':
            print("请输入两步验证码:")
            return False
        else:
            print(f"登陆失败: {rsp['msg']}")
            sys.exit(1)

    def get_breezemoons(self, page:int = 1,size :int = 10) -> dict | None:
        res = requests.get(f'{HOST}/api/breezemoons?p={page}&size={size}', headers={'User-Agent': UA})
        print(res.text)
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            return response['breezemoons']
        else:
            print(response['msg'])
            return None

API = FishPi()