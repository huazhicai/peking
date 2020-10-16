# -*- coding: utf-8 -*-
import pymssql

from .config import *


class XueTouData(object):
    def __init__(self):
        connect = pymssql.connect(host=host, port=port, user=user, password=password,
                                  database=database, charset=charset)

    def main(self):
        pass


if __name__ == '__main__':
    instance = XueTouData()
    instance.main()
