# -*- coding: utf-8 -*-
import random
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, urlparse

import schedule
from prettytable import PrettyTable
from termcolor import colored

from src.api import API, FishPi
from src.api.config import GLOBAL_CONFIG
from src.api.ws import WS

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
    fish_ball_trigger(api, message)
    if len(GLOBAL_CONFIG.chat_config.blacklist) > 0 and GLOBAL_CONFIG.chat_config.blacklist.__contains__(user):
        return
    if user == api.current_user:
        print(f"\t\t\t\t\t\t[{time}]")
        print(colored(
            f'\t\t\t\t\t\t你说: {message["md"]}', GLOBAL_CONFIG.chat_config.chat_user_color))
        api.chatroom.last_msg_id = message['oId']
    else:
        if len(GLOBAL_CONFIG.chat_config.kw_blacklist) > 0:
            hasKeyword = any(
                i for i in GLOBAL_CONFIG.chat_config.kw_blacklist if message["md"].__contains__(i))
            if hasKeyword:
                return
        if "client" in message:
            print(f'[{time}] 来自({message["client"]})')
        else:
            print(f"[{time}]")
        if len(user_nick_name) > 0:
            print(colored(f"{user_nick_name}({user})说:",
                  GLOBAL_CONFIG.chat_config.chat_user_color))
        else:
            print(
                colored(f"{user}说:", GLOBAL_CONFIG.chat_config.chat_user_color))
        print(colored(remove_msg_tail(message),
              GLOBAL_CONFIG.chat_config.chat_content_color))
        print("\r\n")
    if GLOBAL_CONFIG.chat_config.repeat_mode_switch:
        repeat(api, message["md"])


class ChatRoom(WS):
    WS_URL = 'fishpi.cn/chat-room-channel'

    def __init__(self) -> None:
        super().__init__(ChatRoom.WS_URL, [render, render_redpacket])

    def on_open(self, obj):
        print(f'欢迎{API.current_user}进入聊天室!')
        if len(GLOBAL_CONFIG.chat_config.blacklist) > 0:
            print('小黑屋成员: ' + str(GLOBAL_CONFIG.chat_config.blacklist))

    def on_error(self, obj, error):
        super().on_error(obj, error)

    def on_close(self, obj, close_status_code, close_msg):
        print('已经离开聊天室')


def fish_ball_trigger(api: FishPi, message: dict) -> None:
    if 'sevenSummer' == message['userName'] and message['md'].__contains__('天降鱼丸, [0,10] 随机个数. 限时 1 min. 冲鸭~'):
        api.chatroom.send(GLOBAL_CONFIG.chat_config.fish_ball)


def remove_msg_tail(message: dict) -> str:
    excluded_prefixes = [">", "##### 引用"]
    excluded_substrings = [
        "https://zsh4869.github.io/fishpi.io/?hyd=",
        "extension-message",
        ":sweat_drops:",
        "下次更新时间",
        "https://unv-shield.librian.net/api/unv_shield",
        "EXP"
    ]
    if message["userName"] == 'b':
        return message['md']
    lines: list[str] = [
        line for line in message['md'].split('\n') if line != '']
    new_lines = [line for line in lines if not any(line.strip().startswith(
        prefix) for prefix in excluded_prefixes) and not any(substring in line for substring in excluded_substrings)]
    return renderWeather(message["userName"], new_lines)


def renderWeather(username: str, lines: list[str]) -> str:
    if username != 'xiaoIce':
        return '\n'.join(lines)
    for index in range(len(lines)):
        match = re.search(r'src="(.*?)"', lines[index])
        if match:
            src_url = match.group(1)
            parsed_url = urlparse(src_url)
            data = parse_qs(parsed_url.query)
            data['date'] = data['date'][0].split(',')
            data['weatherCode'] = data['weatherCode'][0].split(',')
            data['max'] = data['max'][0].split(',')
            data['min'] = data['min'][0].split(',')
            table = PrettyTable()
            table.title = data.pop('t')[0] + ' ' + data.pop('st')[0]
            table.field_names = list(data.keys())
            for i in range(len(data['date'])):
                row_data = [data[key][i] for key in data.keys()]
                table.add_row(row_data)
            lines[index] = table.get_string()
    return '\n'.join(lines)
