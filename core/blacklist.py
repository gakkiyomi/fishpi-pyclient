
import os
import re
from api import FishPi
from core.config import GLOBAL_CONFIG


def unban_someone(api: FishPi, username):
    if not GLOBAL_CONFIG.repeat_config.blacklist.__contains__(username):
        print(username + '不在黑名单中')
        return
    user_info = api.user.get_user_info(username)
    if user_info is None:
        return
    GLOBAL_CONFIG.repeat_config.blacklist.remove(username)
    # 持久化到文件
    f_path = f'{os.getcwd()}/config.ini'
    src = open(f_path, "r+")
    config_text = src.read()
    src.close()
    dst = open(f_path, 'w')
    if len(GLOBAL_CONFIG.repeat_config.blacklist) == 0:
        after = r'blacklist=[""]'
    else:
        after = "blacklist=" + \
            str(GLOBAL_CONFIG.repeat_config.blacklist).replace("\'", "\"")
    dst.write(re.sub(r'blacklist.*', after, config_text))
    dst.close()
    print(username + '已从小黑屋中释放')


def ban_someone(api: FishPi, username):
    if GLOBAL_CONFIG.repeat_config.blacklist.__contains__(username):
        print(username + ' 已在黑名单中')
        return
    user_info = api.user.get_user_info(username)
    if user_info is None:
        return
    GLOBAL_CONFIG.repeat_config.blacklist.append(username)
    # 持久化到文件
    f_path = f'{os.getcwd()}/config.ini'
    src = open(f_path, "r+")
    config_text = src.read()
    src.close()
    dst = open(f_path, 'w')
    after = "blacklist=" + \
        str(GLOBAL_CONFIG.repeat_config.blacklist).replace("\'", "\"")
    dst.write(re.sub(r'blacklist.*', after, config_text))
    dst.close()
    print(username + '已加入到黑名单中')
