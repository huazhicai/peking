from sz_sid import ShenZhenSid
from bd_sid import BeiDaSid
from config import BD_SERVER_IP, SZ_SERVER_IP


class CrawlSid(object):
    def __init__(self, tag, host, protocol):
        assert tag in ['bd', 'sz']
        assert protocol in ['sftp', 'ssh']

        self.tag = tag
        self.protocol = protocol

        if self.tag == 'bd':
            assert host in BD_SERVER_IP
            self.bd = BeiDaSid(host, protocol)

        if self.tag == 'sz':
            assert host in SZ_SERVER_IP
            self.sz = ShenZhenSid(host, protocol)

    def get_sid(self):
        ret = {'user': '', 'pwd': ''}
        if self.tag == 'bd':
            user = 'user'
            if self.protocol == 'sftp':
                user = 'xftp'
            sid = self.bd.get_sid()
            ret.update({'user': user, 'pwd': sid})
            return ret

        if self.tag == 'sz':
            user, pwd = self.sz.get_sid()
            ret.update({'user': user, 'pwd': pwd})
            return ret
