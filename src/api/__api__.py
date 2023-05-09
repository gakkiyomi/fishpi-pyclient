

class Response:
    def __init__(self, code: int = 0, msg: str = '', data: any = {}):
        self.code = code
        self.msg = msg
        self.data = data


class Base(object):
    def __init__(self, key=''):
        self.set_token(key)

    def set_token(self, api_key=''):
        self.api_key = api_key
