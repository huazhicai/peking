from config.base_config import outpatient_system_code
from config.utils import capital_to_lower, quchong


class MenZhenData(object):

    def __call__(self, args, io):
        shenfenzhenghao = args['shenfenzhenghao']
        binglihao = args['binglihao']
        jiuzhenkahao = args['jiuzhenkahao']
        xingming = args['xingming']
        chushengriqi = args['chushengriqi']
        # ['shenfenzhenghao', 'binglihao', 'jiuzhenkahao', 'xingming', 'chushengriqi']

        sql = '''select sfzh as shenfenzhenghao, bah as binglihao, jzkh as jiuzhenkahao, 
                          xm as xingming, csrq as chushengriqi from gy_brjbxxk where '''
        sfzh_sql = sql + "sfzh='{}'".format(shenfenzhenghao)
        blh_sql = sql + "bah='{}'".format(binglihao)
        jzkh_sql = sql + "jzkh='{}'".format(jiuzhenkahao)
        xm_rq_sql = sql + "xm='{}'".format(xingming)

        io.set_output('sfzh_sql', sfzh_sql)
        io.set_output('blh_sql', blh_sql)
        io.set_output('jzkh_sql', jzkh_sql)
        io.set_output('xm_rq_sql', xm_rq_sql)

        io.push_event('Out')


class MenZhenDetail(object):
    def split_yongyaojilu(self, arry):
        koufu = []
        zhenji = []
        for item in arry:
            if item.get('yongfa') and '口' in item['yongfa']:
                koufu.append({
                    60206: item['kaiyaoshijian'],
                    60201: item['yaowumingcheng'],
                    60202: item['yicijiliang'],
                    60203: item['danwei'],
                    60205: item['yongyaopinlv'],
                    60204: item['yongfa'],
                    60208: item['tingzhishijian'],
                    60209: outpatient_system_code,  # 数据来源
                })
            elif item:
                zhenji.append({
                    60306: item['kaiyaoshijian'],
                    60301: item['yaowumingcheng'],
                    60302: item['yicijiliang'],
                    60303: item['danwei'],
                    60305: item['yongyaopinlv'],
                    60304: item['yongfa'],
                    60308: item['tingzhishijian'],
                    60309: outpatient_system_code,  # 数据来源
                })
        return koufu, zhenji

    def fetch(self, sql):
        import subprocess, os
        curdir = os.path.split(os.path.realpath(__file__))[0]
        url = 'jbdc:oracle:thin:@192.168.1.114:1521:ORACLE82'
        usr = 'zjhis'
        pwd = 'dec456'
        cmd = '"{}/../jre1.2/bin/java.exe" -classpath "{}/../oracle";"{}/../oracle/classes12.zip" OracleCon {} {} {} "{}"' \
            .format(curdir, curdir, curdir, url, usr, pwd, sql)

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = p.communicate()
        output = eval(str(stdout, encoding="GB18030"))
        output = [capital_to_lower(i) for i in output]
        return output

    def replace_key(self, array):
        new_array = []
        for item in array:
            new_array.append({
                60109: item['zhenduanriqi'],
                60110: item['zhenduanmingcheng'],
                60111: 2,
            })
        return new_array

    def start(self, args, io):
        input_array = args['input_array']

        zd_sql = '''select ZJ_BL_ZD.ZDMC as zhenduanmingcheng, JZRQ as zhenduanriqi
                            from zj_bl_brbl left join zj_bl_zd on zj_bl_brbl.jzxh=zj_bl_zd.jzxh
                            where JZKH='{}' '''

        yy_sql = '''select mz_cfk1.cfrq as kaiyaoshijian, ypmc as yaowumingcheng, ypgg as guige, 
                          mz_cfk2.YCJL as yicijiliang, mz_cfk2.JLDW as danwei, GYFSMC as yongfa, 
                          mz_cfk2.PL as yongyaopinlv, mz_cfk2.TZSJ as tingzhishijian from mz_cfk1
                          left join mz_cfk2 on mz_cfk1.cfsb=mz_cfk2.cfsb
                          left join GY_YPCDJG on mz_cfk2.JGXH = GY_YPCDJG.xh 
                          left join zj_gyfs on zj_gyfs.GYFSBH=mz_cfk2.FYFS
                          where mz_cfk1.jzkh='{}' '''
        yyjl, zdjl = [], []
        seen = set()
        for item in input_array:
            jzkh = item['jiuzhenkahao']
            if jzkh not in seen:
                seen.add(jzkh)
                zdjl.extend(self.fetch(zd_sql.format(jzkh)))
                yyjl.extend(self.fetch(yy_sql.format(jzkh)))

        zdjl = self.replace_key(zdjl)

        # 是否要去掉时间戳，去重呢
        result = quchong(yyjl)
        koufu, zhenji = self.split_yongyaojilu(result)

        io.set_output('zhenduanjilu', zdjl)
        io.set_output('koufuyao', koufu)
        io.set_output('zhenjiyao', zhenji)
        io.push_event('Out')


if __name__ == '__main__':
    pass