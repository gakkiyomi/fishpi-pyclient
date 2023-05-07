
import requests
import json

from utils.utils import UA, HOST
from .__api__ import Base


class User(Base):

    def get_user_info(self, username: str) -> None | dict:
        if self.api_key == '':
            return None
        resp = requests.get(HOST + '/user/'+username+'?apiKey=' +
                            self.api_key, headers={'User-Agent': UA})
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            print('此用户不存在: ' + username)

    def get_online_users(self) -> dict:
        resp = requests.get(HOST + '/chat-room/online-users',
                            headers={'User-Agent': UA})
        return json.loads(resp.text)

    def checked_status(self) -> dict:
        resp = requests.get(HOST + '/user/checkedIn?apiKey=' +
                            self.api_key, headers={'User-Agent': UA})
        return json.loads(resp.text)

    def get_liveness_info(self) -> dict:
        resp = requests.get(HOST + '/user/liveness?apiKey=' +
                            self.api_key, headers={'User-Agent': UA})
        return json.loads(resp.text)
