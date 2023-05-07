
import os
import re
from api import FishPi
from core.config import GLOBAL_CONFIG


def unban_someone(api: FishPi, userName):
    if GLOBAL_CONFIG.repead_config.blacklist.__contains__(userName) == False:
        print(userName + '不在黑名单中')
        return
    userInfo = api.user.get_user_info(userName)
    if userInfo is None:
        return
    GLOBAL_CONFIG.repead_config.blacklist.remove(userName)
    # 持久化到文件
    f_path = f'{os.getcwd()}/config.ini'
    src = open(f_path, "r+")
    configText = src.read()
    src.close()
    dst = open(f_path, 'w')
    after = ''
    if len(GLOBAL_CONFIG.repead_config.blacklist) == 0:
        after = r'blacklist=[""]'
    else:
        after = "blacklist=" + \
            str(GLOBAL_CONFIG.repead_config.blacklist).replace("\'", "\"")
    dst.write(re.sub(r'blacklist.*', after, configText))
    dst.close()
    print(userName + '已从小黑屋中释放')


def ban_someone(api: FishPi, userName):
    if GLOBAL_CONFIG.repead_config.blacklist.__contains__(userName):
        print(userName + ' 已在黑名单中')
        return
    userInfo = api.user.get_user_info(userName)
    if userInfo is None:
        return
    GLOBAL_CONFIG.repead_config.blacklist.append(userName)
    # 持久化到文件
    f_path = f'{os.getcwd()}/config.ini'
    src = open(f_path, "r+")
    configText = src.read()
    src.close()
    dst = open(f_path, 'w')
    after = "blacklist=" + \
        str(GLOBAL_CONFIG.repead_config.blacklist).replace("\'", "\"")
    dst.write(re.sub(r'blacklist.*', after, configText))
    dst.close()
    print(userName + '已加入到黑名单中')
