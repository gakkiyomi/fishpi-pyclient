import json
import os
from configparser import ConfigParser

from src.api import FishPi

from .chatroom import init_soliloquize, listener
from .config import GLOBAL_CONFIG, AuthConfig, ChatConfig, CliConfig, RedPacketConfig
from .redpacket import render_redpacket


def init_config(api: FishPi, cli_config: CliConfig):
    file_path = cli_config.file_path
    if file_path is None:
        file_path = f'{os.getcwd()}/config.ini'
    config = ConfigParser()
    try:
        print("配置读取中...")
        if not os.path.exists(file_path):
            print(f'{file_path}配置文件不存在')
            __init_default_config(cli_config)
        else:
            config.read(file_path, encoding='utf-8')
            GLOBAL_CONFIG.auth_config = __init_login_auth_config(
                config, cli_config)
            GLOBAL_CONFIG.redpacket_config = __int_redpacket_config(config)
            GLOBAL_CONFIG.chat_config = __init_chat_config(config)
            GLOBAL_CONFIG.cfg_path = file_path
    except Exception as e:
        print(f'{file_path}配置文件不合法')
        __init_default_config()
    __init_message_listener(api)
    init_soliloquize(api)


def __init_message_listener(api: FishPi):
    api.add_listener(listener)
    api.add_listener(render_redpacket)



def __init_default_config(cli_config: CliConfig):
    print("加载系统变量")
    GLOBAL_CONFIG.auth_config = AuthConfig()
    GLOBAL_CONFIG.redpacket_config = RedPacketConfig()
    GLOBAL_CONFIG.chat_config = ChatConfig()
    GLOBAL_CONFIG.cfg_path = None
    __init_userinfo_with_sys_env(GLOBAL_CONFIG.auth_config)
    __init_userinfo_with_cli_config(GLOBAL_CONFIG.auth_config, cli_config)



def __int_redpacket_config(config: ConfigParser) -> RedPacketConfig:
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


def __init_login_auth_config(config: ConfigParser, cli_config: CliConfig) -> AuthConfig:
    auth_config = AuthConfig(config.get('auth', 'username'),
                             config.get('auth', 'password'))

    __init_userinfo_with_sys_env(auth_config)
    __init_userinfo_with_cli_config(auth_config, cli_config)
    return auth_config


def __init_userinfo_with_sys_env(auth_config: AuthConfig):
    auth_config.username = os.environ.get(
        "FISH_PI_USERNAME", auth_config.username)
    auth_config.password = os.environ.get(
        "FISH_PI_PASSWORD", auth_config.password)



def __init_userinfo_with_cli_config(auth_config: AuthConfig, cli_config: CliConfig):
    if cli_config.username is not None and cli_config.password is not None:
        auth_config.username = cli_config.username
        auth_config.password = cli_config.password
        auth_config.mfa_code = cli_config.code
    return auth_config



def __init_chat_config(config: ConfigParser) -> ChatConfig:
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
