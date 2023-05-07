# -*- coding: utf-8 -*-
import time

import rel

from api import FishPi
from core import __init__
from core.cli import HELP
from core.config import GLOBAL_CONFIG
from core.websocket import start


def init(var: FishPi):
    __init__(var)


if __name__ == "__main__":
    rel.safe_read()
    api = FishPi()
    init(api)
    success = api.login(GLOBAL_CONFIG.auth_config.username,
                        GLOBAL_CONFIG.auth_config.password, '')
    if success:
        print(HELP)
        if len(GLOBAL_CONFIG.repeat_config.blacklist) > 0:
            print('小黑屋成员: ' + str(GLOBAL_CONFIG.repeat_config.blacklist))
    else:
        while len(api.api_key) == 0:
            time.sleep(3)
            if len(api.api_key) > 0:
                break
    print("进入聊天室")
    start(api)
    rel.signal(2, rel.abort)
    rel.dispatch()
