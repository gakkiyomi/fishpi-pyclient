# -*- coding: utf-8 -*-
import json
from typing import Any

import requests

from src.api.base import Base
from src.utils import UA

from .article import ArticleAPI
from .chatroom import ChatRoomAPI
from .config import GLOBAL_CONFIG
from .user import UserAPI


class UserInfo(object):

    def __init__(self, username: str, password: str, api_key: str) -> None:
        self.username = username
        self.password = password
        self.api_key = api_key
        self.ws: dict[str, Any] = {}
        self.is_online = False

    def online(self, func) -> None:
        if (len(self.api_key) != 0):
            API.set_token(self.api_key)
            API.set_current_user(self.username)
        else:
            API.login(self.username, self.password)
            self.api_key = API.api_key
        func()
        self.is_online = True
        GLOBAL_CONFIG.auth_config.username = self.username
        GLOBAL_CONFIG.auth_config.password = self.password
        GLOBAL_CONFIG.auth_config.key = self.api_key
        API.user_key_write_to_config_file()

    def offline(self) -> None:
        keys = list(self.ws.keys())
        for key in keys:
            self.ws[key].stop()
        self.is_online = False


class FishPi(Base):
    def __init__(self):
        self.sockpuppets: dict[str, UserInfo] = {}
        self.user = UserAPI()
        self.chatroom = ChatRoomAPI()
        self.article = ArticleAPI()
        super().__init__(self)

    def set_token(self, key):
        super().set_token(key)
        self.user.set_token(key)
        self.chatroom.set_token(key)
        self.article.set_token(key)

    def get_breezemoons(self, page: int = 1, size: int = 10) -> dict | None:
        res = requests.get(
            f'{GLOBAL_CONFIG.host}/api/breezemoons?p={page}&size={size}', headers={'User-Agent': UA})
        print(res.text)
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            return response['breezemoons']
        else:
            print(response['msg'])
            return None


API = FishPi()
