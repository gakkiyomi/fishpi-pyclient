import json

from api import FishPi
from core.chatroom import init_soliloquize
from core.cli import init_sys_in
from core.config import GLOBAL_CONFIG, RedPacketConfig, AuthConfig, RepeatConfig
import configparser
import os
import sys


def __init__(api: FishPi):
    config = configparser.ConfigParser()
    try:
        print("配置读取中")
        config.read(f'{os.getcwd()}/config.ini', encoding='utf-8')
        GLOBAL_CONFIG.auth_config = __init_login_auth_config(config)
        GLOBAL_CONFIG.redpacket_config = __int_redpacket_var(config)
        GLOBAL_CONFIG.repeat_config = __init_repeat_config(config)
    except:
        print("请检查config.ini配置文件是否合法")
        sys.exit(1)
    init_soliloquize(api)
    init_sys_in(api)


def __int_redpacket_var(config) -> RedPacketConfig:
    ret = RedPacketConfig()
    if config.getint('redPacket', 'rate') > 0:
        ret.rate = config.getint('redPacket', 'rate')
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


def __init_repeat_config(config) -> RepeatConfig:
    ret = RepeatConfig()
    ret.repeat_mode_switch = config.getboolean('chat', 'repeatMode')
    ret.frequency = config.getint('chat', 'repeatFrequency')
    ret.soliloquize_switch = config.getboolean('chat', 'soliloquizeMode')
    ret.soliloquize_frequency = config.getint('chat', 'soliloquizeFrequency')
    ret.sentences = json.loads(config.get('chat', 'sentences'))
    ret.blacklist = json.loads(config.get('chat', 'blacklist'))
    if ret.blacklist.__contains__(''):
        ret.blacklist.remove('')
    return ret
