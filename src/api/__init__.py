# -*- coding: utf-8 -*-
import json
from typing import Any

import requests

from src.api.base import Base
from src.utils import HOST, UA

from .article import ArticleAPI
from .chatroom import ChatRoomAPI
from .user import UserAPI


class FishPi(Base):
    def __init__(self):
        self.ws: dict[str, Any] = {}
        self.user = UserAPI()
        self.chatroom = ChatRoomAPI()
        self.article = ArticleAPI()
        Base.__init__(self)

    def set_token(self, key):
        Base.set_token(self, key)
        self.user.set_token(key)
        self.chatroom.set_token(key)
        self.article.set_token(key)

    def get_breezemoons(self, page: int = 1, size: int = 10) -> dict | None:
        res = requests.get(
            f'{HOST}/api/breezemoons?p={page}&size={size}', headers={'User-Agent': UA})
        print(res.text)
        response = json.loads(res.text)
        if 'code' in response and response['code'] == 0:
            return response['breezemoons']
        else:
            print(response['msg'])
            return None


API = FishPi()
