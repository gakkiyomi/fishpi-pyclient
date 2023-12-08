# -*- coding: utf-8 -*-

import re

from src.api import FishPi
from src.api.config import GLOBAL_CONFIG


def release_someone(api: FishPi, username: str) -> None:
    if not GLOBAL_CONFIG.chat_config.blacklist.__contains__(username):
        print(f'{username}不在小黑屋中')
        return
    user_info = api.user.get_user_info(username)
    if user_info is None:
        return
    GLOBAL_CONFIG.chat_config.blacklist.remove(username)
    print(username + '已从小黑屋中释放')
    if GLOBAL_CONFIG.cfg_path is None:
        return
    # 持久化到文件
    with open(GLOBAL_CONFIG.cfg_path, "r+", encoding='utf-8') as src:
        config_text = src.read()

    with open(GLOBAL_CONFIG.cfg_path, 'w', encoding='utf-8') as dst:
        after = ''
        if len(GLOBAL_CONFIG.chat_config.blacklist) == 0:
            after = 'blacklist=[]'
        else:
            after = "blacklist=" + \
                str(GLOBAL_CONFIG.chat_config.blacklist).replace("\'", "\"")
        dst.write(re.sub(r'^blacklist\s*=.*', after, config_text))


def ban_someone(api: FishPi, username: str) -> None:
    if GLOBAL_CONFIG.chat_config.blacklist.__contains__(username):
        print(f'{username}已在小黑屋中')
        return
    user_info = api.user.get_user_info(username)
    if user_info is None:
        return
    GLOBAL_CONFIG.chat_config.blacklist.append(username)
    print(f'{username}已加入到小黑屋中')
    if GLOBAL_CONFIG.cfg_path is None:
        return
    # 持久化到文件
    with open(GLOBAL_CONFIG.cfg_path, "r+", encoding='utf-8') as src:
        config_text = src.read()
    with open(GLOBAL_CONFIG.cfg_path, 'w', encoding='utf-8') as dst:
        after = "blacklist=" + \
            str(GLOBAL_CONFIG.chat_config.blacklist).replace("\'", "\"")
        dst.write(re.sub(r'blacklist\s*=.*', after, config_text))


def put_keyword_to_bl(args: tuple[str, ...]) -> None:
    for keyword in args:
        if GLOBAL_CONFIG.chat_config.kw_blacklist.__contains__(keyword):
            print(f'{keyword} 已在加入关键词屏蔽')
            continue
        GLOBAL_CONFIG.chat_config.kw_blacklist.append(keyword)
        print(f'{keyword} 已在加入关键词屏蔽')
        if GLOBAL_CONFIG.cfg_path is None:
            return
        # 持久化到文件
        with open(GLOBAL_CONFIG.cfg_path, "r+", encoding='utf-8') as src:
            config_text = src.read()
        with open(GLOBAL_CONFIG.cfg_path, 'w', encoding='utf-8') as dst:
            after = "kwBlacklist=" + \
                str(GLOBAL_CONFIG.chat_config.kw_blacklist).replace("\'", "\"")
            dst.write(re.sub(r'^kwBlacklist\s*=.*', after, config_text))


def remove_keyword_to_bl(args: tuple[str, ...]) -> None:
    for keyword in args:
        if GLOBAL_CONFIG.chat_config.kw_blacklist.__contains__(keyword) == False:
            print(f'{keyword} 不在关键词屏蔽池中')
            continue
        GLOBAL_CONFIG.chat_config.kw_blacklist.remove(keyword)
        print(f'{keyword} 不再屏蔽')
        if GLOBAL_CONFIG.cfg_path is None:
            return
        # 持久化到文件
        with open(GLOBAL_CONFIG.cfg_path, "r+", encoding='utf-8') as src:
            config_text = src.read()
        with open(GLOBAL_CONFIG.cfg_path, 'w', encoding='utf-8') as dst:
            after = ''
            if len(GLOBAL_CONFIG.chat_config.blacklist) == 0:
                after = 'kwBlacklist=[]'
            else:
                after = "kwBlacklist=" + \
                    str(GLOBAL_CONFIG.chat_config.kw_blacklist).replace("\'", "\"")
            dst.write(re.sub(r'^kwBlacklist\s*=.*', after, config_text))
