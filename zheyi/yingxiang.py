import random

from lxml import etree

import requests
from datetime import datetime
from config.base_config import user_agent

headers = {'User-Agent': random.choice(user_agent)}


class YingXiang(object):

    def __init__(self):
        self.host = 'http://192.168.33.115'

    def get_index(self, **post_data):
        url = self.host + '/Home/GetWorkListView'
        if post_data.get('PatientsID'):  # 提取访问详情页需要的参数
            resp = requests.post(url, data=post_data, headers=headers)
            paras = etree.HTML(resp.text).xpath('//table/tbody/tr/td[1]/text()')
            return paras
        elif post_data.get('PatientsAlias'):
            resp = requests.post(url, data=post_data, headers=headers)
            blh_arry = etree.HTML(resp.text).xpath('//table/tbody/tr/td[5]/text()')
            return blh_arry

    def get_other_index_data(self, resp, page, **post_data):
        p = lambda x, y: ''.join(etree.HTML(x).xpath(y)).strip()
        total = p(resp.text, '//*[@id="hidResultTotal"]/@value')
        item_num = p(resp.text, '//*[@id="hidPageNum"]/@value')
        pages = int(total) // int(item_num) + 1
        ret = []
        while page < pages:
            page += 1
            post_data.update({"CurrentPageIndex": page})
            ret.extend(self.get_index(**post_data))
        return ret

    def get_data(self, key, page=1):
        url = self.host + '/Home/GetWorkListView'
        post_data = {
            'AdmissionSource': '50,10,100,1',
            'OrderBy': 'False',
            'StartTime': '2000-01-01',
            'EndTime': datetime.now().strftime('%Y-%m-%d'),
            'CurrentPageIndex': page,
        }
        if key.isdigit():  # key为病历号, 病历号检索
            post_data.update({'PatientsID': key})
            resp = requests.post(url, data=post_data)
            # 提取请求每条记录所需的参数
            paras = etree.HTML(resp.text).xpath('//table/tbody/tr/td[1]/text()')
            others = self.get_other_index_data(resp, page, **post_data)
            paras.extend(others)
            return paras
        else:  # key 为姓名, 用姓名搜索病历号
            name = key.encode('unicode-escape').decode().replace('\\', '%')
            post_data.update({'PatientsAlias': name})
            resp = requests.post(url, post_data)
            blh_s = etree.HTML(resp.text).xpath('//table/tbody/tr/td[5]/text()')
            others = self.get_other_index_data(resp, page, **post_data)
            blh_s.extend(others)
            # print(blh_s)
            return blh_s

    def get_detail(self, para):
        url = self.host + '/Report/Report'
        values = para.split('|')
        keys = ('StudiesIndex', 'ResultsIndex', 'AccessionNumber', 'AdmissionID', 'PatientsID')
        param = dict(zip(keys, values))
        param.update({'DBclick': 'true'})
        resp = requests.get(url, data=param)
        p = lambda x: ''.join(etree.HTML(resp.text).xpath(x)).strip().replace('&nbsp', '')
        # [50106, 50101, 0, 50103, 50105]
        result = {
            50101: param.get('PatientsID'),
            50103: p('//*[@id="fldPatientInfo"]/table/tr[2]/td/label/text()'),
            50105: p('//*[@id="fldPatientInfo"]/table/tr[7]/td/label/text()'),
            50106: p('//*[@id="fldPatientInfo"]/table/tr[8]/td/label/text()'),

            50111: p('//*[@id="tdContentMiddle"]/div/table/tr[3]/td/fieldset/text()'),
            50108: p('//*[@id="fldPatientInfo"]/table/tr[14]/td/label/text()'),
            50107: p('//*[@id="fldPatientInfo"]/table/tr[10]/td/label/text()'),
            50110: p('//*[@id="tdContentMiddle"]/div/table/tr[2]/td/fieldset/text()'),
            50109: p('//*[@id="fldPatientInfo"]/table/tr[18]/td/label/text()'),
        }
        # print(result)
        return result

    def main(self, blh, name=None):
        if name:
            blh_array = self.get_data(name)
            if blh: blh_array.append(blh)
            result = []
            for i in set(blh_array):
                result.extend([self.get_detail(para) for para in set(self.get_data(i))])
        elif blh:
            result = [self.get_detail(para) for para in set(self.get_data(blh))]
        else:
            result = []
        result = [i for i in result if i]
        return result

    def start(self, args, io):
        # blh = '00764982'
        # name = '孙玉祥'
        name = args['Name']
        blh = args['Binglihao']

        result = self.main(blh, name)

        io.set_output('Array', result)
        io.push_event('Out')


if __name__ == '__main__':
    pass
