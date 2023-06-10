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


class AuthConfig(object):
    def __init__(self, username='', password='', mfa_code=''):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code


class ChatConfig(object):
    def __init__(self, blacklist=[], repeat_mode_switch=False, frequency=5, soliloquize_switch=False,
                 soliloquize_frequency=20, sentences=[], answerMode :bool=False):
        self.repeat_mode_switch = repeat_mode_switch
        self.frequency = frequency
        self.soliloquize_switch = soliloquize_switch
        self.soliloquize_frequency = soliloquize_frequency
        self.sentences = ['你们好！', '牵着我的手，闭着眼睛走你也不会迷路。',
                          '吃饭了没有?', '💗 爱你哟！'] + sentences
        self.blacklist = blacklist
        self.answerMode = answerMode


class Config(object):
    def __init__(self, auth: AuthConfig = None, redpacket: RedPacketConfig = None, chat: ChatConfig = None, cfg_path :str = None):
        self.auth_config = auth
        self.redpacket_config = redpacket
        self.chat_config = chat
        self.cfg_path = cfg_path

GLOBAL_CONFIG = Config()
