import json

from src.api import FishPi
from .chatroom import init_soliloquize, listener
from .redpacket import render_redpacket
from .config import GLOBAL_CONFIG, RedPacketConfig, AuthConfig, ChatConfig
import configparser
import os


def __init__(api: FishPi, file_path: str = None):
    if file_path is None:   
        file_path = f'{os.getcwd()}/config.ini'
    config = configparser.ConfigParser()
    try:
        print("配置读取中...")
        if not os.path.exists(file_path):
            print(f'{file_path}配置文件不存在')
            __init_default_config()
        else:
            config.read(file_path, encoding='utf-8')
            GLOBAL_CONFIG.auth_config = __init_login_auth_config(config)
            GLOBAL_CONFIG.redpacket_config = __int_redpacket_config(config)
            GLOBAL_CONFIG.chat_config = __init_chat_config(config)
            GLOBAL_CONFIG.cfg_path = file_path
    except:
        print(f'{file_path}配置文件不合法')
        __init_default_config()
    __init_message_listener(api)
    init_soliloquize(api)


def __init_message_listener(api :FishPi):
    api.add_listener(listener)
    api.add_listener(render_redpacket)

def __init_default_config():
    print("加载默认配置文件")
    GLOBAL_CONFIG.auth_config = AuthConfig()
    GLOBAL_CONFIG.redpacket_config = RedPacketConfig()
    GLOBAL_CONFIG.chat_config = ChatConfig()
    GLOBAL_CONFIG.cfg_path = None

def __int_redpacket_config(config) -> RedPacketConfig:
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


def __init_login_auth_config(config) -> AuthConfig:
    return AuthConfig(config.get('auth', 'username'),
                      config.get('auth', 'password'))


def __init_chat_config(config) -> ChatConfig:
    ret = ChatConfig()
    ret.repeat_mode_switch = config.getboolean('chat', 'repeatMode')
    ret.frequency = config.getint('chat', 'repeatFrequency')
    ret.soliloquize_switch = config.getboolean('chat', 'soliloquizeMode')
    ret.soliloquize_frequency = config.getint('chat', 'soliloquizeFrequency')
    ret.sentences = json.loads(config.get('chat', 'sentences'))
    ret.blacklist = json.loads(config.get('chat', 'blacklist'))
    if ret.blacklist.__contains__(''):
        ret.blacklist.remove('')
    return ret
