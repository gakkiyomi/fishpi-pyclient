class RedPacketConfig(object):
    def __init__(self, red_packet_switch=True, heartbeat=False, smart_mode=False, threshold=0.5, adventure_mode=False,
                 timeout=5, rate=3):
        self.red_packet_switch = red_packet_switch
        self.heartbeat = heartbeat
        self.smart_mode = smart_mode
        self.threshold = threshold
        self.adventure_mode = adventure_mode
        self.timeout = timeout
        self.rate = rate


class AuthConfig(object):
    def __init__(self, username='', password='', mfa_code=''):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code

    @classmethod
    def build(cls, map: dict):
        return cls(map['username'], map['password'], map['2fa_code'])


class RepeatConfig(object):
    def __init__(self, blacklist=[], repeat_mode_switch=False, frequency=5, soliloquize_switch=False,
                 soliloquize_frequency=20, sentences=[]):
        self.repeat_mode_switch = repeat_mode_switch
        self.frequency = frequency
        self.soliloquize_switch = soliloquize_switch
        self.soliloquize_frequency = soliloquize_frequency
        self.sentences = ['你们好！', '牵着我的手，闭着眼睛走你也不会迷路。',
                          '吃饭了没有?', '💗 爱你哟！'] + sentences
        self.blacklist = blacklist


class Config(object):
    def __init__(self, auth: AuthConfig = None, redpacket: RedPacketConfig = None, repeat: RepeatConfig = None):
        self.auth_config = auth
        self.redpacket_config = redpacket
        self.repeat_config = repeat


GLOBAL_CONFIG = Config()
