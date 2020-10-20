import re
import requests
from random import random
import warnings
from http import cookiejar
from chaojiying import Chaojiying_Client
from shenzhen_cracker.PwdDecoder import decode_pwd

from config.xue_config import SZ_BL_USER, SZ_HOST, SZ_BL_PASSWD, SERVER_USER, SERVER_ACCOUNT

warnings.filterwarnings('ignore')


class ShenZhenSid(object):
    def __init__(self, server_ip, connect_type):

        self.host = SZ_HOST
        self.loginName = SZ_BL_USER
        self.password = SZ_BL_PASSWD

        self.server_ip = server_ip
        self.connect_type = connect_type

        self.session = requests.Session()
        self.session.cookies = cookiejar.LWPCookieJar(filename="cookies.txt")

    def getImage(self):
        url = self.host + '/fort/pages/commons/image.jsp?seed={}'.format(random())
        resp = self.session.get(url, verify=False)
        if resp.status_code == 200:
            with open('img_code.jpg', 'wb') as f:
                f.write(resp.content)

    def read_code(self):
        self.getImage()
        chaojiying = Chaojiying_Client('shenhua', 'shenhua@123', '96001')
        im = open('img_code.jpg', 'rb').read()
        ret = chaojiying.PostPic(im, 1004)
        return ret['pic_str']

    def login(self):
        post_data = {
            'loginName': self.loginName,
            'password': self.password,
            'imgCode': self.read_code()
        }
        url = self.host + '/fort/login/check.action'
        resp = self.session.post(url, data=post_data)

        if resp.status_code == 200:
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)

    def load_cookies(self):
        try:
            self.session.cookies.load(ignore_discard=True)  # 加载cookie文件，
        except:
            print('cookie未能加载')

    def get_sid(self, call_count=0):
        self.load_cookies()
        post_data = {
            'account': SERVER_ACCOUNT[self.server_ip]['account'],
            'protocol': self.connect_type,
            'resId': SERVER_ACCOUNT[self.server_ip]['resId'],
            'authType': 0,
            'newSso': 1,
        }
        url = self.host + '/fort/sso/execute.action'
        resp = self.session.post(url, data=post_data, verify=False)

        if resp.status_code == 200:
            result = re.search(r'<script LANGUAGE=\'javascript\'>document.location.href=\'(.*?)\'</script>', resp.text)
            if result:
                return SERVER_USER, decode_pwd(result.group(1))
            else:
                if call_count < 2:
                    call_count += 1
                    self.login()
                    self.get_sid(call_count)
                else:
                    print('login page failed!')
                    raise
        else:
            raise


if __name__ == '__main__':
    case = ShenZhenSid('10.12.140.13', 'ssh')

    user, pwd = case.get_sid()
    print(user, pwd)


