
import random
from api import FishPi
from core.config import GLOBAL_CONFIG


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
