import json
import os
import re
from abc import ABC, abstractmethod
from configparser import ConfigParser, NoOptionError
from typing import Any

import schedule

from src.api import FishPi, UserInfo
from src.api.config import (
    GLOBAL_CONFIG,
    AuthConfig,
    ChatConfig,
    CliOptions,
    RedPacketConfig,
)
from src.core.command import init_cli
from src.core.user import check_in
from src.utils import HOST

from .chatroom import ChatRoom, init_soliloquize


class Initor(ABC):
    def __init__(self, next=None):
        self.next = next

    def __iter__(self):
        node = self
        while node is not None:
            yield node
            node = node.next

    @abstractmethod
    def exec(self, api: FishPi, options: CliOptions) -> None:
        pass

    def init(self, api: FishPi, options: CliOptions) -> None:
        self.exec(api, options)
        self.next.init(api, options)


class FileConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        file_path = options.file_path
        if file_path is None:
            file_path = f'{os.getcwd()}/config.ini'
        config = ConfigParser()
        try:
            print("配置读取中...")
            if not os.path.exists(file_path):
                print(f'{file_path}配置文件不存在')
            else:
                config.read(file_path, encoding='utf-8')
                init_auth_config(config)
                GLOBAL_CONFIG.redpacket_config = int_redpacket_config(config)
                GLOBAL_CONFIG.chat_config = init_chat_config(config)
                GLOBAL_CONFIG.cfg_path = file_path
                GLOBAL_CONFIG.host = init_host_config(config)
        except Exception as e:
            print(f'{file_path}配置文件不合法')


class DefualtConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        print("生成默认配置")
        GLOBAL_CONFIG.auth_config = AuthConfig()
        GLOBAL_CONFIG.redpacket_config = RedPacketConfig()
        GLOBAL_CONFIG.chat_config = ChatConfig()
        GLOBAL_CONFIG.cfg_path = None
        GLOBAL_CONFIG.host = HOST


class EnvConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        GLOBAL_CONFIG.auth_config.username = os.environ.get(
            "FISH_PI_USERNAME", '')
        GLOBAL_CONFIG. auth_config.password = os.environ.get(
            "FISH_PI_PASSWORD", '')


class CilConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        init_userinfo_with_options(options)


class LoginInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        os.environ['NO_PROXY'] = GLOBAL_CONFIG.host
        while len(GLOBAL_CONFIG.auth_config.username) == 0:
            print('请输入用户名:')
            GLOBAL_CONFIG.auth_config.username = input("")
        while len(GLOBAL_CONFIG.auth_config.password) == 0:
            print('请输入密码:')
            GLOBAL_CONFIG.auth_config.password = input("")
        api.login(GLOBAL_CONFIG.auth_config.username,
                  GLOBAL_CONFIG.auth_config.password,
                  GLOBAL_CONFIG.auth_config.mfa_code)
        if len(GLOBAL_CONFIG.auth_config.accounts) != 0:
            for account in GLOBAL_CONFIG.auth_config.accounts:
                api.sockpuppets[account[0]] = UserInfo(
                    account[0], account[1], '')
        api.sockpuppets[api.current_user] = UserInfo(
            api.current_user, GLOBAL_CONFIG.auth_config.password, api.api_key)
        api.sockpuppets[api.current_user].is_online = True


class ChaRoomInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        init_soliloquize(api)
        if GLOBAL_CONFIG.chat_config.soliloquize_switch:
            schedule.run_pending()
        chatroom = ChatRoom()
        chatroom.start()


class CliInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        init_cli(api)


class InitChain(object):
    def __init__(self, api: FishPi = None, options: CliOptions = None) -> None:
        self.head: Initor = None
        self.api = api
        self.options = options

    def __call__(self, *args: Any, **kwds: Any) -> None:
        self.api = kwds['api']
        self.options = kwds['options']
        self.init()

    def append(self, *args) -> None:
        curr_node = self.head
        initors = (i for i in args)
        if curr_node is None:
            self.head = next(initors)
            curr_node = self.head
        for initor in initors:
            curr_node.next = initor
            curr_node = curr_node.next

    def init(self):
        self.append(DefualtConfigInitor(),
                    EnvConfigInitor(),
                    FileConfigInitor(),
                    CilConfigInitor(),
                    LoginInitor(),
                    ChaRoomInitor(),
                    CliInitor())
        self.head.init(self.api, self.options)


def int_redpacket_config(config: ConfigParser) -> RedPacketConfig:
    ret = RedPacketConfig()
    if config.getint('redPacket', 'rate') > 0:
        ret.rate = config.getint('redPacket', 'rate')
    if config.getint('redPacket', 'rpsLimit') > 0:
        ret.rps_limit = config.getint('redPacket', 'rpsLimit')
    ret.red_packet_switch = config.getboolean(
        'redPacket', 'openRedPacket')
    ret.heartbeat = config.getboolean(
        'redPacket', 'heartbeat')
    ret.smart_mode = config.getboolean(
        'redPacket', 'heartbeatSmartMode')
    ret.adventure_mode = config.getboolean(
        'redPacket', 'heartbeatAdventure')
    if config.getfloat('redPacket', 'heartbeatThreshold') < 0:
        ret.threshold == 0.4
    if ret.threshold > 1:
        ret.threshold == 1
    ret.timeout = config.getint(
        'redPacket', 'heartbeatTimeout')
    return ret


def init_auth_config(config: ConfigParser) -> None:
    GLOBAL_CONFIG.auth_config = AuthConfig(config.get('auth', 'username'),
                                           config.get('auth', 'password'))
    try:
        sockpuppet_usernames = config.get(
            'auth', 'sockpuppet_usernames').replace('，', ',').split(',')
        sockpuppet_passwords = config.get(
            'auth', 'sockpuppet_passwords').replace('，', ',').split(',')
        sockpuppets = zip(sockpuppet_usernames, sockpuppet_passwords)
        for sockpuppet in sockpuppets:
            GLOBAL_CONFIG.auth_config.add_account(
                sockpuppet[0].strip(), sockpuppet[1].strip())
    except NoOptionError:
        pass


def init_userinfo_with_options(options: CliOptions) -> None:
    if options.username is not None:
        GLOBAL_CONFIG.auth_config.username = options.username
    if options.password is not None:
        GLOBAL_CONFIG.auth_config.password = options.password
    GLOBAL_CONFIG.auth_config.mfa_code = options.code
    if options.host is not None:
        pattern = re.compile(r'^https?://')
        if pattern.match(options.host):
            GLOBAL_CONFIG.host = options.host
        else:
            GLOBAL_CONFIG.host = 'https://' + options.host


def init_chat_config(config: ConfigParser) -> ChatConfig:
    ret = ChatConfig()
    ret.repeat_mode_switch = config.getboolean('chat', 'repeatMode')
    ret.answer_mode = config.getboolean('chat', "answerMode")
    ret.frequency = config.getint('chat', 'repeatFrequency')
    ret.soliloquize_switch = config.getboolean('chat', 'soliloquizeMode')
    ret.soliloquize_frequency = config.getint('chat', 'soliloquizeFrequency')
    ret.sentences = json.loads(config.get('chat', 'sentences'))
    ret.blacklist = json.loads(config.get('chat', 'blacklist'))
    if ret.blacklist.__contains__(''):
        ret.blacklist.remove('')
    ret.kw_blacklist = json.loads(config.get('chat', 'kwBlacklist'))
    if ret.kw_blacklist.__contains__(''):
        ret.kw_blacklist.remove('')
    ret.fish_ball = config.get('chat', "fishBall")
    return ret


def init_host_config(config: ConfigParser) -> str:
    try:
        host = config.get('auth', 'host')
        if host is None:
            return HOST
        pattern = re.compile(r'^https?://')
        if pattern.match(host):
            return host
        else:
            return 'https://' + host
    except NoOptionError:
        return HOST


FishPiInitor = InitChain()
