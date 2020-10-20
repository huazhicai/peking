# -*- coding:utf-8 -*-


def special_rule_1(dataTree, key_path, value, group_path):
    if group_path:
        group_path = group_path[:-1]
    dataTree.set_value(key_path, value, group_path)
