import json
import os
import sys
from abc import ABC, abstractmethod
from configparser import ConfigParser
from typing import Any

from src.api import FishPi
from src.core.command import init_cli
from src.core.user import check_in, login
from src.core.websocket import init_chatroom

from .chatroom import init_soliloquize, listener
from .config import GLOBAL_CONFIG, AuthConfig, ChatConfig, CliConfig, RedPacketConfig
from .redpacket import render_redpacket


class Initor(ABC):
    def __init__(self, next=None):
        self.next = next

    def __iter__(self):
        node = self
        while node is not None:
            yield node
            node = node.next

    @abstractmethod
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        pass

    def init(self, api: FishPi, cli_config: CliConfig) -> None:
        self.exec(api, cli_config)
        self.next.init(api, cli_config)


class FileConfigInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        file_path = cli_config.file_path
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
        except Exception as e:
            breakpoint()
            print(f'{file_path}配置文件不合法')


class DefualtConfigInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        print("生成默认配置")
        GLOBAL_CONFIG.auth_config = AuthConfig()
        GLOBAL_CONFIG.redpacket_config = RedPacketConfig()
        GLOBAL_CONFIG.chat_config = ChatConfig()
        GLOBAL_CONFIG.cfg_path = None


class EnvConfigInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        GLOBAL_CONFIG.auth_config.username = os.environ.get(
            "FISH_PI_USERNAME", '')
        GLOBAL_CONFIG. auth_config.password = os.environ.get(
            "FISH_PI_PASSWORD", '')


class CilConfigInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        init_userinfo_with_cli_config(cli_config)


class LoginInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        if GLOBAL_CONFIG.auth_config.username is None:
            print('用户名不能为空')
            sys.exit(0)
        if GLOBAL_CONFIG.auth_config.password is None:
            print('密码不能为空')
            sys.exit(0)
        login(api)
        check_in(api)


class ChaRoomInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        api.add_listener(listener)
        api.add_listener(render_redpacket)
        init_soliloquize(api)
        init_chatroom(api)


class CliInitor(Initor):
    def exec(self, api: FishPi, cli_config: CliConfig) -> None:
        init_cli(api)


class InitChain(object):
    def __init__(self, api: FishPi = None, cli_config: CliConfig = None) -> None:
        self.head: Initor = None
        self.api = api
        self.cli_config = cli_config

    def __call__(self, *args: Any, **kwds: Any) -> None:
        self.api = kwds['api']
        self.cli_config = kwds['cli_config']
        self.init()

    def append(self, *args) -> None:
        curr_node = self.head
        sample_generator = (i for i in args)
        if curr_node is None:
            self.head = next(sample_generator)
            curr_node = self.head
        for initor in sample_generator:
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
        self.head.init(self.api, self.cli_config)


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


def init_userinfo_with_cli_config(cli_config: CliConfig) -> None:
    if cli_config.username is not None and cli_config.password is not None:
        GLOBAL_CONFIG.auth_config.username = cli_config.username
        GLOBAL_CONFIG.auth_config.password = cli_config.password
        GLOBAL_CONFIG.auth_config.mfa_code = cli_config.code


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
    return ret


FishPiInitor = InitChain()
