# -*- coding: utf-8 -*-
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Self

import schedule

from src.api import API, FishPi
from src.api.ws import WS

from .config import GLOBAL_CONFIG
from .redpacket import render_redpacket, rush_redpacket

REPEAT_POOL = {}  # 复读池


def init_soliloquize(api: FishPi) -> None:
    if GLOBAL_CONFIG.chat_config.soliloquize_switch:
        schedule.every(GLOBAL_CONFIG.chat_config.soliloquize_frequency).minutes.do(
            soliloquize, api
        )


def repeat(api: FishPi, msg) -> None:
    if not REPEAT_POOL.__contains__(msg):
        REPEAT_POOL.clear()
        REPEAT_POOL[msg] = 1
    elif REPEAT_POOL[msg] == GLOBAL_CONFIG.chat_config.frequency:
        api.chatroom.send(msg)
        REPEAT_POOL[msg] = REPEAT_POOL[msg] + 1
    else:
        REPEAT_POOL[msg] = REPEAT_POOL[msg] + 1


def soliloquize(api: FishPi) -> None:
    length = len(GLOBAL_CONFIG.chat_config.sentences)
    index = random.randint(0, length - 1)
    api.chatroom.send(GLOBAL_CONFIG.chat_config.sentences[index])


executor = ThreadPoolExecutor(max_workers=5)


def render(api: FishPi, message: dict) -> None:
    if message["type"] == "msg":
        if message["content"].find("redPacket") != -1:
            executor.submit(rush_redpacket, api, message)
        else:
            renderChatroomMsg(api, message)


def renderChatroomMsg(api: FishPi, message: dict) -> None:
    time = message["time"]
    user = message["userName"]
    user_nick_name = message["userNickname"]
    if len(GLOBAL_CONFIG.chat_config.blacklist) > 0 and GLOBAL_CONFIG.chat_config.blacklist.__contains__(user):
        return
    if user == GLOBAL_CONFIG.auth_config.username:
        print(f"\t\t\t\t\t\t[{time}]")
        print(f'\t\t\t\t\t\t你说: {message["md"]}')
        api.chatroom.last_msg_id = message['oId']
    else:
        if "client" in message:
            print(f'[{time}] 来自({message["client"]})')
        else:
            print(f"[{time}]")
        if len(user_nick_name) > 0:
            print(f"{user_nick_name}({user})说:")
        else:
            print(f"{user}说:")
        print(message["md"])
        print("\r\n")
    if GLOBAL_CONFIG.chat_config.repeat_mode_switch:
        msg = message["md"]
        repeat(api, msg)


class ChatRoom(WS):
    WS_URL = 'fishpi.cn/chat-room-channel'

    def __init__(self) -> None:
        init_soliloquize(WS.api)
        super().__init__(ChatRoom.WS_URL, [render, render_redpacket])

    def on_open(self, obj):
        print(f'欢迎{API.current_user}进入聊天室!')
        if len(GLOBAL_CONFIG.chat_config.blacklist) > 0:
            print('小黑屋成员: ' + str(GLOBAL_CONFIG.chat_config.blacklist))
        if GLOBAL_CONFIG.chat_config.soliloquize_switch:
            schedule.run_pending()

    def on_error(self, obj, error):
        super().on_error(obj, error)

    def on_close(self, obj, close_status_code, close_msg):
        print("已经离开聊天室,可以执行命令 #chatroom 重新进入聊天室")
