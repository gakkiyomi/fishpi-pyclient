from api.chatroom import ChatRoom
from core.const import UA, HOST
from dotenv import dotenv_values
from .__api__ import Base
from .user import User
import sys
import requests
import hashlib
import json


def __init__():
    env = dotenv_values(".env")
    init_host(env)


def init_host(config: dict):
    global HOST
    if 'fishpi_domain' in config:
        HOST = config.get('fishpi_domain')


class FishPi(Base):
    def __init__(self):
        self.current_user = ''
        self.user = User()
        self.chatroom = ChatRoom()
        Base.__init__(self)

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
        res = requests.post(HOST + "/api/getKey", json=params,
                            headers={'User-Agent': UA})
        rsp = json.loads(res.text)
        if rsp['code'] == 0:
            self.set_token(rsp['Key'])
            self.set_current_user(username)
            print("登陆成功 欢迎" + username + '进入聊天室!')
            print("更多功能与趣味游戏请访问网页端: " + HOST)
            return True
        elif rsp['code'] == -1 and rsp['msg'] == '两步验证失败，请填写正确的一次性密码':
            print("请输入两步验证码:")
            return False
        else:
            print("登陆失败: " + rsp['msg'])
            sys.exit(1)

    def get_yesterday_reward(self) -> dict:
        resp = requests.get(
            HOST + '/activity/yesterday-liveness-reward-api?apiKey='+self.api_key, headers={'User-Agent': UA})
        return json.loads(resp.text)
