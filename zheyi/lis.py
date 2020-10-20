class LisData(object):
    def __call__(self, args, io):
        binglihao = args['binglihao']
        jiuzhenkahao = args['jiuzhenkahao']
        xingming = args['xingming']
        chushengriqi = args['chushengriqi']
        # # ['shenfenzhenghao', 'binglihao', 'jiuzhenkahao', 'xingming', 'chushengriqi']

        sql = '''select blh as binglihao, patientid as jiuzhenkahao, birthday as chushengriqi, 
                        PATIENTNAME as xingming, CHECKTIME as jianyanshijian, EXAMINAIM
                          as jianyanmudi , SAMPLENO as yangbenhao from L_PATIENTINFO  where '''
        blh_sql = sql + "blh='{}'".format(binglihao)
        jzkh_sql = sql + "patientid='{}'".format(jiuzhenkahao)
        xm_rq_sql = sql + "patientname='{}'".format(xingming)

        io.set_output('blh_sql', blh_sql)
        io.set_output('jzkh_sql', jzkh_sql)
        io.set_output('xm_rq_sql', xm_rq_sql)

        io.push_event('Out')


class LisDetailData(object):

    def fetch(self, sql):
        import subprocess, os, json, re
        curdir = os.path.split(os.path.realpath(__file__))[0]
        url = 'jbdc:oracle:thin:@192.168.1.7:1521:jyk'
        usr = 'zjhis'
        pwd = 'zjhis'
        cmd = '"{}/../jre1.2/bin/java.exe" -classpath "{}/../oracle";"{}/../oracle/classes12.zip" OracleCon {} {} {} "{}"' \
            .format(curdir, curdir, curdir, url, usr, pwd, sql)

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = p.communicate()

        output = eval(str(stdout, encoding="GB18030"))
        output = [MenZhenDetail.capital_to_lower(i) for i in output]
        return output

    def replace_jieguo_key(self, array):
        new_array = []
        for item in array:
            new_array.append({
                40301: item['jianyanxiangmu'],
                40302: item['ceshijieguo'],
                40303: item['cankaodixian'],
                40304: item['cankaogaoxian'],
                40305: item['jianyanshijian'],
                40203: item['danwei']
            })
        return new_array

    def replace_key(self, array):
        new_array = []
        for item in array:
            new_array.append({
                40106: item['binglihao'],
                40107: item['jiuzhenkahao'],
                40103: item['chushengriqi'],
                40101: item['xingming'],
                40105: item['jianyanmudi'],
                40201: item['yangbenhao'],
                'jieguo': self.replace_jieguo_key(item['jieguo'])
            })
        return new_array

    def __call__(self, args, io):
        input_array = args['input_array']

        sql = '''select B.CHINESENAME as jianyanxiangmu,B.ENGLISHAB as jianyanxiangmuen,TESTRESULT as ceshijieguo,
                REFLO as cankaodixian,REFHI as cankaogaoxian,MEASURETIME as jianyanshijian,L_TESTRESULT.UNIT as danwei 
                from L_TESTRESULT left join L_TESTDESCRIBE B on L_TESTRESULT.TESTID=B.TESTID  where SAMPLENO='{}' '''
        jianyanjieguo = []
        seen = set()
        for item in input_array:
            sample = item['yangbenhao']
            if len(sample) < 4 or sample in seen:  # 过滤无效的sample
                continue
            seen.add(sample)
            jianyanjieguo.extend(self.fetch(sql.format(sample)))
            jieguo = MenZhenDetail.quchong(jianyanjieguo)
            item.update({'jieguo': jieguo})

        io.set_output('out_data', input_array)
        io.push_event('Out')
