# -*- coding: utf-8 -*-
from api import FishPi
from core import __init__
from core.user import login
from core.websocket import start


def init(api: FishPi):
    __init__(api)


if __name__ == "__main__":
    api = FishPi()
    init(api)
    login(api)
    start(api)
