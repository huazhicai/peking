# -*- coding: utf-8 -*-
import decimal
import pymssql

from datetime import datetime

from config.base_config import *
from config.xue_config import *
from data_structure.singleton_structure_content import new_content


class XueTouData(object):
    def __init__(self, connect):

        self.cursor = connect.cursor()
        self.data_source_code = 10704

    def convert_gender(self, array, key):
        """性别'男'转为数字 1， '女'：2"""
        for doc in array:
            if doc[key] == '男':
                doc[key] = 1
            elif doc[key] == '女':
                doc[key] = 2

    def add_data_source(self, data):
        for row in data:
            row[self.data_source_code] = dialysis_system_code

    def yongyao_from_yizhu(self, data):
        """从医嘱里提取出口服用药和针剂用药"""
        koufu, zhenji = [], []
        for item in data:
            assert item
            if item.get('yongfa') and '口' in item['yongfa']:
                koufu.append({
                    10901: item['kaiyaoshijian'],
                    10902: item['yaowumingcheng'],
                    10903: item['yicijiliang'],
                    10904: item['yongyaopinlv'],
                    10905: item['yongfa'],
                    10906: dialysis_system_code,  # 数据来源
                    10907: item['danwei'],
                })
            elif item.get('guige') and ('针' in item.get('guige') or '注' in item.get('guige')):
                zhenji.append({
                    11001: item['kaiyaoshijian'],
                    11002: item['yaowumingcheng'],
                    11003: item['yicijiliang'],
                    11004: item['yongyaopinlv'],
                    11005: item['yongfa'],
                    11006: dialysis_system_code,  # 数据来源
                    11007: item['danwei'],
                })
        return koufu, zhenji

    def get_data(self, sql, keys):
        out_data = []
        self.cursor.excute(sql)
        row = self.cursor.fetchone()
        while row:
            row_data = dict(zip(keys, row))
            for key, val in row_data.items():
                if val in ['-9999.0', '-9999']:
                    val = None
                if isinstance(val, decimal.Decimal):
                    val = float(val)
                if isinstance(val, datetime):
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
                row_data[key] = val
            out_data.append(row_data)
            row = self.cursor.fetchone()
        return out_data

    def main(self, pid):
        ybzl = self.get_data(ybzl_sql.format(pid), ybzl_keys)
        self.convert_gender(ybzl, sex_key)  # 性别转化为数字

        bingshi = self.get_data(bingshi_sql.format(pid), bingshi_keys)
        self.add_data_source(bingshi)  # 数据来源

        xgtl = self.get_data(xgtl_sql.format(pid), xgtl_keys)
        lshjl = self.get_data(lshjl_sql.format(pid), lshjl_keys)
        crrtjl = self.get_data(crrtjl_sql.format(pid), crrtjl_keys)
        hpjl = self.get_data(hpjl_sql.format(pid), hpjl_keys)
        tpejl = self.get_data(tpejl_sql.format(pid), tpejl_keys)
        dfppjl = self.get_data(dfppjl_sql.format(pid), dfppjl_keys)
        iajl = self.get_data(iajl_sql.format(pid), iajl_keys)
        txjl = self.get_data(txjl_sql.format(pid), txjl_keys)
        zhgjl = self.get_data(zhgjl_sql.format(pid), zhgjl_keys)

        zhenduan = self.get_data(zhenduan_sql.format(pid), zhenduan_keys)
        self.add_data_source(zhenduan)  # 数据来源

        yizhu = self.get_data(yizhu_sql.format(pid), yizhu_keys)
        koufu, zhenji = self.yongyao_from_yizhu(yizhu)
        yongyao = [{'changqikoufuyongyao': koufu, 'changqizhenjiyongyao': zhenji}]

        shshjl = self.get_data(shshjl_sql.format(pid), shshjl_keys)
        yyzpl = self.get_data(yyzpl_sql.format(pid), yyzpl_keys)
        jlzpl = self.get_data(jlzpl_sql.format(pid), jlzpl_keys)
        aisengkerenge = self.get_data(aisengkerenge_sql.format(pid), aisengkerenge_keys)
        zhengzhuangziping = self.get_data(zhengzhuangziping_sql.format(pid), zhengzhuangziping_keys)
        lingwushehui = self.get_data(lingwushehui_sql.format(pid), lingwushehui_keys)
        zhgzhxyyzhkpg = self.get_data(zhgzhxyyzhkpg_sql.format(pid), zhgzhxyyzhkpg_keys)
        shhzhlwj = self.get_data(shhzhlwj_sql.format(pid), shhzhlwj_keys)
        pixiazhifan = self.get_data(pixiazhifan_sql.format(pid), pixiazhifan_keys)
        shwzkpg = self.get_data(shwzkpg_sql.format(pid), shwzkpg_keys)
        wolipinggu = self.get_data(wolipinggu_sql.format(pid), wolipinggu_keys)
        qshqkpg = self.get_data(qshqkpg_sql.format(pid), qshqkpg_keys)
        siwang = self.get_data(siwang_sql.format(pid), siwang_keys)

        content = new_content()
        content.push_group([ybzl, bingshi, xgtl, lshjl, crrtjl, hpjl, tpejl, dfppjl, wolipinggu, qshqkpg,
                            iajl, txjl, zhgjl, yongyao, shshjl, yyzpl, jlzpl, aisengkerenge, shwzkpg, siwang,
                            zhengzhuangziping, lingwushehui, zhgzhxyyzhkpg, shhzhlwj, pixiazhifan])
        return content 


if __name__ == '__main__':
    connect = pymssql.connect(host=host, port=port, user=user, password=password,
                              database=database, charset=charset)
    instance = XueTouData(connect)
    instance.main('pid')
