from enum import Enum

class RedPacketType(Enum):
    RANDOM = 'random'
    AVERAGE = 'average'
    SPECIFY = 'specify'
    HEARTBEAT = 'heartbeat'
    RPS = 'rockPaperScissors'


class RedPacket:
    def __init__(self, msg :str = '红包来咯!', money :int = 32, count :int = 2, type :RedPacketType = RedPacketType.RANDOM):
        self.msg = msg
        self.money = money
        self.count = count
        self.type = type
        
    def __json__(self):
        return {
            'msg': self.msg,
            'money': self.money,
            'count': self.count,
            'type': self.type.value
        }    
        
class SpecifyRedPacket(RedPacket):
    def __init__(self, msg :str = '给!', money :int = 32, send_to :list = []):
        super().__init__(msg, money, len(send_to), RedPacketType.SPECIFY)
        self.recivers = send_to

    def __json__(self):
        json_data = super().__json__()
        json_data['recivers'] = self.recivers
        return json_data    

class RPSRedPacket(RedPacket):
    def __init__(self, msg :str = '剪刀石头布!', money :int = 32, gesture :int = 0):
        super().__init__(msg, money, 1, RedPacketType.RPS)
        self.gesture = gesture
        
    def __json__(self):
        json_data = super().__json__()
        json_data['gesture'] = self.gesture
        return json_data