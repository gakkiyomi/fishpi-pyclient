import json
import os
import re
from abc import ABC, abstractmethod
from configparser import ConfigParser, NoOptionError
from typing import Any

import schedule
from colorama import just_fix_windows_console

from src.api import FishPi, UserInfo
from src.api.config import (
    GLOBAL_CONFIG,
    ChatConfig,
    CliOptions,
    RedPacketConfig,
    init_defualt_config,
)
from src.utils import HOST

from .chatroom import ChatRoom, init_soliloquize
from .command import init_cli


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


class DefualtConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        print("生成默认配置")
        defualt = init_defualt_config()
        GLOBAL_CONFIG.auth_config = defualt.auth_config
        GLOBAL_CONFIG.redpacket_config = defualt.redpacket_config
        GLOBAL_CONFIG.chat_config = defualt.chat_config
        GLOBAL_CONFIG.cfg_path = defualt.cfg_path
        GLOBAL_CONFIG.host = defualt.host


class EnvConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        GLOBAL_CONFIG.auth_config.username = os.environ.get(
            "FISH_PI_USERNAME", '')
        GLOBAL_CONFIG.auth_config.password = os.environ.get(
            "FISH_PI_PASSWORD", '')
        GLOBAL_CONFIG.auth_config.key = os.environ.get('FISH_PI_KEY', '')


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


class CilConfigInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        init_userinfo_with_options(options)
        just_fix_windows_console()


class LoginInitor(Initor):
    def exec(self, api: FishPi, options: CliOptions) -> None:
        os.environ['NO_PROXY'] = GLOBAL_CONFIG.host
        if GLOBAL_CONFIG.auth_config.key == '':
            while len(GLOBAL_CONFIG.auth_config.username) == 0:
                print('请输入用户名:')
                GLOBAL_CONFIG.auth_config.username = input("")
            while len(GLOBAL_CONFIG.auth_config.password) == 0:
                print('请输入密码:')
                GLOBAL_CONFIG.auth_config.password = input("")
            api.login(GLOBAL_CONFIG.auth_config.username,
                      GLOBAL_CONFIG.auth_config.password,
                      GLOBAL_CONFIG.auth_config.mfa_code)
            GLOBAL_CONFIG.auth_config.key = api.api_key
        else:
            # 直接使用api-key
            username = api.user.get_username_by_key(
                GLOBAL_CONFIG.auth_config.key)
            if username is not None:
                GLOBAL_CONFIG.auth_config.username = username
                api.set_token(GLOBAL_CONFIG.auth_config.key)
                api.current_user = username
            else:
                print("非法API-KEY, 使用账户密码登陆")
                while len(GLOBAL_CONFIG.auth_config.username) == 0:
                    print('请输入用户名:')
                    GLOBAL_CONFIG.auth_config.username = input("")
                while len(GLOBAL_CONFIG.auth_config.password) == 0:
                    print('请输入密码:')
                    GLOBAL_CONFIG.auth_config.password = input("")
                api.login(GLOBAL_CONFIG.auth_config.username,
                          GLOBAL_CONFIG.auth_config.password,
                          GLOBAL_CONFIG.auth_config.mfa_code)
                GLOBAL_CONFIG.auth_config.key = api.api_key
        if len(GLOBAL_CONFIG.auth_config.accounts) != 0:
            api.sockpuppets = {account[0]: UserInfo(
                account[0], account[1], '') for account in GLOBAL_CONFIG.auth_config.accounts}
        api.sockpuppets[api.current_user] = UserInfo(
            api.current_user, GLOBAL_CONFIG.auth_config.password, api.api_key)
        api.sockpuppets[api.current_user].is_online = True
        api.user_key_write_to_config_file()


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
        ret.threshold = 0.4
    else:
        ret.threshold = config.getfloat('redPacket', 'heartbeatThreshold')
    if ret.threshold > 1:
        ret.threshold = 1
    ret.timeout = config.getint(
        'redPacket', 'heartbeatTimeout')
    return ret


def init_auth_config(config: ConfigParser) -> None:
    try:
        if len(config.get('auth', 'username')) != 0:
            GLOBAL_CONFIG.auth_config.username = ''
            GLOBAL_CONFIG.auth_config.password = ''
            GLOBAL_CONFIG.auth_config.key = ''
            GLOBAL_CONFIG.auth_config.username = config.get('auth', 'username')
    except NoOptionError:
        pass
    try:
        if len(config.get('auth', 'password')) != 0:
            GLOBAL_CONFIG.auth_config.password = config.get('auth', 'password')
    except NoOptionError:
        pass
    try:
        if len(config.get('auth', 'key')) != 0:
            GLOBAL_CONFIG.auth_config.key = config.get('auth', 'key')
    except NoOptionError:
        pass
    init_sockpuppets(config)


def init_sockpuppets(config: ConfigParser) -> None:
    try:
        sockpuppet_usernames = []
        sockpuppet_passwords = []
        usernames = config.get(
            'auth', 'sockpuppet_usernames')
        if len(usernames) != 0:
            sockpuppet_usernames = usernames.replace('，', ',').split(',')
        passwords = config.get(
            'auth', 'sockpuppet_passwords')
        if len(passwords) != 0:
            sockpuppet_passwords = passwords.replace('，', ',').split(',')
        if len(sockpuppet_usernames) == 0 or len(sockpuppet_usernames) != len(sockpuppet_passwords):
            return
        sockpuppets = zip(sockpuppet_usernames, sockpuppet_passwords)
        for sockpuppet in sockpuppets:
            GLOBAL_CONFIG.auth_config.add_account(
                sockpuppet[0].strip(), sockpuppet[1].strip())
    except NoOptionError:
        pass


def init_userinfo_with_options(options: CliOptions) -> None:
    if options.username is not None:
        GLOBAL_CONFIG.auth_config.username = options.username
        GLOBAL_CONFIG.auth_config.password = ''
        GLOBAL_CONFIG.auth_config.key = ''
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
    init_chat_color(ret, config)
    return ret


def init_chat_color(ret: ChatConfig, config: ConfigParser) -> None:
    try:
        user_color = config.get('chat', "chatUserColor")
        if user_color != '':
            ret.chat_user_color = user_color
    except NoOptionError:
        pass
    try:
        content_color = config.get('chat', "chatContentColor")
        if content_color != '':
            ret.chat_content_color = content_color
    except NoOptionError:
        pass


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
