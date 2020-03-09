"""
根据登录指令信息，获取机房服务器远程登录的sessionId
method=login&user=shenhua&passwd=UHdkNE9QU0BaSFlM&adpasswd=&otppasswd=NTc0MDQw&domain=cn%3D%5BD%5Djhoam&certNo=null&macs=00-FF-57-8D-43-06
"""
import re, os

import requests
import hmac, base64, struct, hashlib, time
import win32api
import warnings

from config import BD_BL_PASSWD, BD_BL_USER, BD_FORT_IP, BD_HOST, \
    BD_SERVER_PASSWD, BD_SERVER_USER, OPT_KEY

warnings.filterwarnings("ignore")


def start_easy_connect():
    p = os.popen('tasklist /FI "IMAGENAME eq %s"' % 'SangforCSClient.exe')

    if p.read().count('SangforCSClient.exe') == 0:
        q = os.popen('tasklist /FI "IMAGENAME eq %s"' % 'iexplore.exe')
        if q.read().count('iexplore.exe') > 0:
            os.system("taskkill /F /IM iexplore.exe")

        win32api.ShellExecute(0, 'open', r'C:\Program Files (x86)\Sangfor\SSL\SangforCSClient\SangforCSClient.exe',
                              '', '', 1)

        count = 0
        while count < 60:
            count += 1
            time.sleep(1)
            q = os.popen('tasklist /FI "IMAGENAME eq %s"' % 'iexplore.exe')
            if q.read().count('iexplore.exe') > 0:
                return True

        os.system("taskkill /F /IM SangforCSClient.exe")
        return False
    else:
        return True


# 参数secretKey是开通google身份验证时的密钥
def calGoogleCode(secretKey):
    input = int(time.time()) // 30
    key = base64.b32decode(secretKey)
    msg = struct.pack(">Q", input)
    googleCode = hmac.new(key, msg, hashlib.sha1).digest()
    # o = ord(googleCode[19]) & 15
    o = googleCode[19] & 15
    googleCode = str((struct.unpack(">I", googleCode[o:o + 4])[0] & 0x7fffffff) % 1000000)
    if len(googleCode) == 5:  # 如果验证码的第一位是0，则不会显示。此处判断若是5位码，则在第一位补上0
        googleCode = '0' + googleCode
    return googleCode


class BeiDaSid(object):
    def __init__(self, server_ip, protocol):

        self.server_ip = server_ip
        self.protocol = protocol + '2'

        if self.protocol == 'ssh':
            self.type = 'cmd'
            self.protocol = 'ssh2'
        if self.protocol == 'sftp':
            self.type = 'xftp'

        self.host = BD_HOST
        self.user = BD_BL_USER
        self.passwd = base64.b64encode(BD_BL_PASSWD.encode('utf-8'))

        self.googleCode = calGoogleCode(OPT_KEY)
        self.otppasswd = base64.b64encode(self.googleCode.encode('utf-8'))

        self.session = requests.Session()

    def login(self):
        post_data = {
            'method': 'login',
            'user': self.user,
            'passwd': self.passwd,
            'otppasswd': self.otppasswd,
            'domain': 'cn=[D]jhoam',
        }
        url = self.host + '/iam/ac.do'
        response = self.session.post(url, data=post_data, verify=False)
        print(response.text)

    def get_host_rdn(self):
        url = self.host + '/iam/portal/sso/resrole_list.jsp'  # 主页
        response = self.session.get(url)
        ret = re.search(r'<li onclick=\"goto_resrole_auth_list\(\'(.*?)\', \'北大医院CKD随访和队列系统\', \'2\'\)\"',
                        response.text)
        if ret:
            host_rdn = ret.group(1)
        else:
            assert False
        return host_rdn

    def get_auth_rdn(self):
        post_data = {
            'method': 'list',
            'page_size': 20,
            'page_num': 0,
            'host_rdn': self.get_host_rdn()
        }
        url = self.host + '/iam/sso_auth_list.do'
        response = self.session.post(url, data=post_data)
        ret = re.search(r'(cn=.*?\[D\]jhoam);;\d;centos_unix;CentOS;北大医院随访和队列系统Node\d+;{};'.format(self.server_ip),
                        response.text)
        return ret.group(1)

    def fast_sso_do(self, auth_rdn):
        post_data = {
            'method': 'login',
            'auth_rdn': auth_rdn,
            'debug': 1
        }
        url = self.host + '/iam/fast_sso.do'
        response = self.session.post(url, post_data)
        resp = response.json()

        session_id = resp['meta']['sessionId']
        res_ip = resp['meta']['res_ip']
        return res_ip, session_id

    def sso_do(self, auth_rdn):
        post_data = {
            'method': 'login',
            'auth_rdn': auth_rdn,
            'acc_name': BD_SERVER_USER,
            'type': self.type,
            'protocol': self.protocol,
            'port': 22,
            'fort_ip': BD_FORT_IP,
            'acc_pwd': BD_SERVER_PASSWD
        }
        url = self.host + '/iam/sso.do'
        response = self.session.post(url, post_data)
        return response.text

    def get_sid(self):
        if start_easy_connect():
            self.login()
            auth_rdn = self.get_auth_rdn()
            sid = self.sso_do(auth_rdn)
            return sid
        else:
            print('vpn 连接失败')


if __name__ == '__main__':
    case = BeiDaSid('172.16.130.16', 'ssh2')
    print(case.get_sid())
