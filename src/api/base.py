# -*- coding: utf-8 -*-

import hashlib
import json
import re
import sys

import requests

from src.utils import HELP, UA

from .config import GLOBAL_CONFIG


class Base(object):
    def __init__(self, key=''):
        self.current_user: str = ''
        self.set_token(key)

    def set_token(self, api_key: str = ''):
        self.api_key: str = api_key

    def set_current_user(self, username):
        self.current_user = username

    def login(self, username: str, password: str, mfa_code=''):
        params = {
            'nameOrEmail': username,
            'userPassword': hashlib.md5(str(password).encode('utf-8')).hexdigest(),
            'mfaCode': mfa_code
        }
        res = requests.post(f"{GLOBAL_CONFIG.host}/api/getKey",
                            json=params, headers={'User-Agent': UA})
        rsp = json.loads(res.text)
        if rsp['code'] == 0:
            self.set_token(rsp['Key'])
            self.set_current_user(username)
            print(f'登陆成功! 更多功能与趣味游戏请访问网页端: {GLOBAL_CONFIG.host}')
            print(HELP)
        elif rsp['code'] == -1 and rsp['msg'] == '两步验证失败，请填写正确的一次性密码':
            self.set_token('')
            print("请输入两步验证码:")
            while len(self.api_key) == 0:
                code = input("")
                self.login(username, password, code)
        else:
            print(f"登陆失败: {rsp['msg']}")
            sys.exit(0)

    def user_key_write_to_config_file(self):
        # 持久化到文件
        if GLOBAL_CONFIG.cfg_path is None:
            return
        with open(GLOBAL_CONFIG.cfg_path, "r+", encoding='utf-8') as src:
            config_text = src.read()
        with open(GLOBAL_CONFIG.cfg_path, 'w', encoding='utf-8') as dst:
            after = f"key={self.api_key}"
            dst.write(re.sub(r'key\s*=.*', after, config_text))
