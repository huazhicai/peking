# -*- coding:utf-8-*-
from pypinyin import lazy_pinyin
from openpyxl import load_workbook


def read_one_column(sheet, col_num):
    data = [cell.value for cell in sheet[col_num] if cell.value]
    data.pop(0)  # 去除列头
    return data


def hanzi_to_pinyin(hanzi_list):
    pinyin_array = []
    for single in hanzi_list:
        py_str = lazy_pinyin(single)
        single_str_py = ''
        if len(py_str) > 5:
            for i in py_str:
                if i in single:
                    single_str_py = single_str_py + '_{}'.format(i.lower())
                single_str_py = single_str_py + i[0]
        else:
            for i in py_str:
                single_str_py = single_str_py + i.lower()
        pinyin_array.append(single_str_py)
    return pinyin_array


if __name__ == '__main__':
    filename = 'xuetou.xlsx'
    sheet_name = '化验信息'
    workBook = load_workbook(filename)
    sheet = workBook.get_sheet_by_name(sheet_name)

    huayan_num_keys = read_one_column(sheet, 'AC')
    huayan_fields = read_one_column(sheet, 'AD')
    assert len(huayan_fields) == len(huayan_num_keys)
    print(hanzi_to_pinyin(huayan_fields))
