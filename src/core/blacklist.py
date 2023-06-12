
import re
from src.api import FishPi
from .config import GLOBAL_CONFIG


def unban_someone(api: FishPi, username):
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
    src = open(GLOBAL_CONFIG.cfg_path, "r+")
    config_text = src.read()
    src.close()
    dst = open(GLOBAL_CONFIG.cfg_path, 'w')
    if len(GLOBAL_CONFIG.chat_config.blacklist) == 0:
        after = r'blacklist=[""]'
    else:
        after = "blacklist=" + \
            str(GLOBAL_CONFIG.chat_config.blacklist).replace("\'", "\"")
    dst.write(re.sub(r'blacklist.*', after, config_text))
    dst.close()


def ban_someone(api: FishPi, username):
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
    src = open(GLOBAL_CONFIG.cfg_path, "r+")
    config_text = src.read()
    src.close()
    dst = open(GLOBAL_CONFIG.cfg_path, 'w')
    after = "blacklist=" + \
        str(GLOBAL_CONFIG.chat_config.blacklist).replace("\'", "\"")
    dst.write(re.sub(r'blacklist.*', after, config_text))
    dst.close()
