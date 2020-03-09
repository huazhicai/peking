import re, random
import time

import requests
from pymongo import MongoClient
from pyquery import PyQuery as pq
from datetime import datetime, timedelta

from migration.config import USER_AGENT, AIRPORT_CODE

HEADERS = {'User-Agent': random.choice(USER_AGENT)}

client = MongoClient('localhost')
db = client['migration']
collection = db['umetrip']


def get_airport_three_code():
    url = 'https://webresource.c-ctrip.com/code/cquery/resource/address/flight/flight_new_poi_gb2312.js'
    response = requests.get(url)
    resp_text = response.text
    city_list = re.findall(r'data:\".*?\|(.*?)\|.*?\"', resp_text, re.S)
    city_list.append('北京(大兴机场)(PKX)')
    result = set(city_list)
    result.remove('北京(BJS)')
    result.remove('上海(SHA)')

    ret = [i.strip(')').rsplit('(', 1) for i in result]
    city_doc = {i[0]: i[1] for i in ret}
    return city_doc


def get_city_flights():
    url = 'https://flights.ctrip.com/process/schedule/#B'
    doc = pq(url)
    items = doc('#mainbody > li > div.mod_box > div > div.natinal_m > ul > li > div > a').items()
    urls = ['https://flights.ctrip.com' + i.attr('href') for i in items]
    return urls


def dep_arr(url):
    # url = 'https://flights.ctrip.com/schedule/bjs..html'
    doc = pq(url)
    dep_arr = [tuple(i.text().split('-')) for i in doc('#ulD_Domestic > li > div > a').items()]
    return dep_arr


def get_airline_info(url, tries=0):
    # url = 'http://www.umetrip.com/mskyweb/tk/dm.do?dep=PEK&arr=SZX&begDate=2020-03-05'
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.content:
            return resp.json()
        else:
            raise requests.ConnectionError
    except requests.ConnectionError as e:
        if tries < 5:
            tries += 1
            print("retry %s" % tries, url)
            time.sleep(2 * tries)
            return get_airline_info(url, tries)
        else:
            print(e)


def parse_airline_data(dep, arr, date):
    air_line_url = f'http://www.umetrip.com/mskyweb/tk/dm.do?dep={dep}&arr={arr}&begDate={date}'
    ret = get_airline_info(air_line_url)
    if ret and ret.get('parray', None):
        flights = []
        for it in ret['parray']:
            item = {}
            item['airplan'] = it["pflynum"]
            item['dep_time'] = it['pbegtime']
            item['arr_time'] = it['pendtime']
            item['price'] = it['pprice']
            item['begin_code'] = it['pbegcode']
            item['end_code'] = it['pendcode']
            flights.append(item)
        return flights


def main():
    date = datetime.now() + timedelta(days=1)
    date = date.strftime('%Y-%m-%d')
    city_flights = get_city_flights()
    for link in city_flights:
        dep_arr_list = dep_arr(link)
        city_lines = {'date': date, 'depCity': dep_arr_list[0][0], 'airlines': []}
        for dep, arr in dep_arr_list:
            print(dep, arr)
            airline = {'arrCity': arr}

            if dep in ['北京', '上海']:
                dep_codes = AIRPORT_CODE[dep]
            else:
                dep_codes = [AIRPORT_CODE[dep]]

            if arr in ['北京', '上海']:
                arr_codes = AIRPORT_CODE[arr]
            else:
                arr_codes = [AIRPORT_CODE[arr]]

            result = []
            for dep_code in dep_codes:
                for arr_code in arr_codes:
                    print(dep_code, arr_code)
                    flight_data = parse_airline_data(dep_code, arr_code, date)
                    if flight_data:
                        result.extend(flight_data)

            airline['airplans'] = result

            if airline['airplans']:
                city_lines['airlines'].append(airline)
            time.sleep(2)

        if city_lines['airlines']:
            collection.update_one({'depCity': city_lines['depCity'], 'date': date}, {'$set': city_lines}, upsert=True)


if __name__ == '__main__':
    main()
