import requests
import re, time
import json
import random

from datetime import datetime, timedelta
from retrying import retry
from pymongo import MongoClient
from migration.config import USER_AGENT, CITIES_CODE

HEADERS = {'User-Agent': random.choice(USER_AGENT)}

client = MongoClient('localhost')
db = client['migration']
collection = db['huiyan']


def get_requests(url, tries=0):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError as e:
        if tries < 4:
            tries += 1
            print("retry %s" % tries, url)
            time.sleep(2 * tries)
            return get_requests(url, tries)
        else:
            print(e)


def parse_data(doc):
    if doc:
        result = re.search(r'cb\((.*?)\)', doc)
        ret = json.loads(result.group(1))
        return ret['data']['list']


def get_history_data(start_date, end_date):
    while start_date < end_date:
        print(start_date)
        main(start_date)
        start_date += timedelta(days=1)
        time.sleep(1)


def main(date):
    date_arg = date.strftime('%Y%m%d')
    md_date = date.strftime('%Y-%m-%d')

    for s_key, s_value in CITIES_CODE.items():

        for key, value in s_value.items():
            print('Crawl %s' % key)
            if s_key == "直辖市":
                move_in_url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=province&id=%s&type=move_in&date=%s' % (
                    value, date_arg)

                move_out_url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=province&id=%s&type=move_out&date=%s' % (
                    value, date_arg)
            else:
                move_in_url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=city&id=%s&type=move_in&date=%s' % (
                    value, date_arg)
                move_out_url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=city&id=%s&type=move_out&date=%s' % (
                    value, date_arg)

            doc_in = get_requests(move_in_url)
            data_in = parse_data(doc_in)
            time.sleep(2)
            doc_out = get_requests(move_out_url)
            data_out = parse_data(doc_out)

            result = {'city': key, 'date': md_date, 'move_in': data_in, 'move_out': data_out}

            collection.update_one({'city': key, 'date': md_date}, {'$set': result}, upsert=True)
            time.sleep(2)


if __name__ == '__main__':
    # date = datetime.now() - timedelta(days=1)
    # main(date)

    start_date = datetime(2020, 1, 1)
    end_date = datetime.now() - timedelta(days=1)
    get_history_data(start_date, end_date)
