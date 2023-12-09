# -*- coding: utf-8 -*-
import configparser

from src.utils import HOST


class RedPacketConfig(object):
    def __init__(self, red_packet_switch=True, heartbeat=True, smart_mode=True, threshold=0.5, adventure_mode=True,
                 timeout=7, rate=3, rps_limit=100):
        self.red_packet_switch = red_packet_switch
        self.heartbeat = heartbeat
        self.smart_mode = smart_mode
        self.threshold = threshold
        self.adventure_mode = adventure_mode
        self.timeout = timeout
        self.rate = rate
        self.rps_limit = rps_limit

    def to_config(self) -> dict:
        return {
            'openRedPacket': str(self.red_packet_switch),
            'rate': str(self.rate),
            'rpsLimit': str(self.rps_limit),
            'heartbeat': str(self.heartbeat),
            'heartbeatSmartMode': str(self.smart_mode),
            'heartbeatThreshold': str(self.threshold),
            'heartbeatTimeout': str(self.timeout),
            'heartbeatAdventure': str(self.adventure_mode),
        }


class AuthConfig(object):
    def __init__(self, username='', password='', mfa_code='', key=''):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self.key = key
        self.accounts: list[tuple[str, ...]] = []

    def add_account(self, username='', password=''):
        self.accounts.append((username, password))

    def to_config(self) -> dict:
        usernames = ''
        passwords = ''
        if len(self.accounts) != 0:
            usernames = ",".join(username for username, _ in self.accounts)
            usernames = ",".join(password for password, _ in self.accounts)
        return {
            'username': self.username,
            'password': self.password,
            'key': self.key,
            'sockpuppet_usernames': usernames,
            'sockpuppet_passwords': passwords
        }


class ChatConfig(object):
    def __init__(self, blacklist: list[str] = [], kw_blacklist: list[str] = ['你点的歌来了'], repeat_mode_switch=False, frequency=5, soliloquize_switch=False,
                 soliloquize_frequency=20, sentences: list[str] = [], answer_mode: bool = False, fish_ball: str = '凌 捞鱼丸',
                 chat_user_color: str | None = None, chat_content_color: str | None = None):
        self.repeat_mode_switch = repeat_mode_switch
        self.frequency = frequency
        self.soliloquize_switch = soliloquize_switch
        self.soliloquize_frequency = soliloquize_frequency
        self.sentences = ['你们好！', '牵着我的手，闭着眼睛走你也不会迷路。',
                          '吃饭了没有?', '💗 爱你哟！'] + sentences
        self.blacklist = blacklist
        self.kw_blacklist = kw_blacklist
        self.answer_mode = answer_mode
        self.fish_ball = fish_ball
        self.chat_user_color = chat_user_color
        self.chat_content_color = chat_content_color

    def to_config(self) -> dict:
        res = {
            'fishBall': str(self.fish_ball),
            'repeatMode': str(self.repeat_mode_switch),
            'answerMode': str(self.answer_mode),
            'repeatFrequency': str(self.frequency),
            'soliloquizeMode': str(self.soliloquize_switch),
            'soliloquizeFrequency': str(self.soliloquize_frequency),
            'sentences': '[' + ",".join('\"'+item+'\"' for item in self.sentences) + ']',
            'blacklist': '[' + ",".join('\"'+item+'\"' for item in self.blacklist) + ']',
            'kwBlacklist': '[' + ",".join('\"'+item+'\"' for item in self.kw_blacklist) + ']',
            'chatUserColor': self.chat_user_color,
            'chatContentColor': self.chat_content_color
        }

        if self.chat_user_color is None:
            res['chatUserColor'] = ''
        if self.chat_user_color is None:
            res['chatContentColor'] = ''
        return res


class Config(object):
    def __init__(self, auth: AuthConfig = None, redpacket: RedPacketConfig = None, chat: ChatConfig = None, cfg_path: str = None, host: str = 'https://fishpi.cn'):
        self.auth_config = auth
        self.redpacket_config = redpacket
        self.chat_config = chat
        self.cfg_path = cfg_path
        self.host = host

    def to_ini_template(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config['auth'] = self.auth_config.to_config()
        config['redPacket'] = self.redpacket_config.to_config()
        config['chat'] = self.chat_config.to_config()
        return config


class CliOptions(object):
    def __init__(self, username: str = '', password: str = '', code: str = '', file_path: str = None, host: str = None):
        self.username = username
        self.password = password
        self.code = code
        self.file_path = file_path
        self.host = host


def init_defualt_config() -> Config:
    return Config(AuthConfig(), RedPacketConfig(), ChatConfig(), None, HOST)


GLOBAL_CONFIG = Config()
