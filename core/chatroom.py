
import random
from api import FishPi
from core.config import GLOBAL_CONFIG
from core.redpacket import rush_redpacket


REPEAT_POOL = {}  # 复读池


def repeat(api: FishPi, msg):
    if REPEAT_POOL.__contains__(msg) == False:
        REPEAT_POOL.clear()
        REPEAT_POOL[msg] = 1
    elif REPEAT_POOL[msg] == GLOBAL_CONFIG.repead_config.frequency:
        api.chatroom.send(msg)
        REPEAT_POOL[msg] = REPEAT_POOL[msg] + 1
    else:
        REPEAT_POOL[msg] = REPEAT_POOL[msg] + 1


def soliloquize(api: FishPi):
    length = len(GLOBAL_CONFIG.repead_config.sentences)
    index = random.randint(0, length - 1)
    api.chatroom.send(GLOBAL_CONFIG.repead_config.sentences[index])


def listener(api: FishPi, message):
    if message['type'] == 'msg':
        if message['content'].find("redPacket") != -1:
            rush_redpacket(api, message)
        else:
            time = message['time']
            user = message['userName']
            if len(GLOBAL_CONFIG.repead_config.blacklist) > 0 and GLOBAL_CONFIG.repead_config.blacklist.__contains__(user):
                return
            if user == GLOBAL_CONFIG.auth_config.username:
                print('\t\t\t\t\t\t[' + time + ']')
                print('\t\t\t\t\t\t你说: ' + message['md'])
            else:
                print('[' + time + ']')
                print(user + '说:')
                print(message['md'])
                print('\r\n')
            if GLOBAL_CONFIG.repead_config.repeat_mode_switch:
                msg = message['md']
                repeat(api, msg)
