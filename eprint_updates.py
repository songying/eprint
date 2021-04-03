import requests
import os
from os.path import exists
import re
import const
import xlwt
import xlrd
import json
from datetime import datetime
import sys

#Example python eprint.py 2021
#leave no argument for current year
const.YEAR = str(datetime.now().year)
if len(sys.argv)>1 :
    const.YEAR = sys.argv[1]

#basic path and url defination
const.XLS_FILENAME = const.YEAR+'.xls'
const.ID_LIST_FILENAME = const.YEAR+'_id_list.json'
const.URL = 'https://eprint.iacr.org/eprint-bin/search.pl?last=365&title=1'
const.HOST = 'https://eprint.iacr.org/'+const.YEAR+'/'

#regular expressions
const.LIST_PATTERN = re.compile(r'<a href="\/'+const.YEAR+'\/(\d*)">', re.I)
const.TITLE_PATTERN = re.compile(r'<b>(.*?)<\/b>',re.I)
const.AUTHOR_PATTERN = re.compile(r'<i>(.*?)<\/i>',re.I)
const.ABSTRACT_PATTERN = re.compile(r'<b>Abstract: <\/b>(.*?)<p',re.I|re.S)
const.ORIGIN_PATTERN = re.compile(r'<b>Original Publication</b><b> (\(.*?\):) <\/b>(.*?)<p',re.I|re.S)
const.KEYWORD_PATTERN = re.compile(r'<b>Category \/ Keywords: <\/b>(.*?)<p',re.I)

#initiate excel function and header
const.EXCEL_STYLE = xlwt.XFStyle()
const.EXCEL_STYLE.alignment.wrap = 1  #auto break line
const.EXCEL_HEADER = ['ID','Title','Author','Keyword','Abstract','Original Publication','URL']
const.BOOK = xlwt.Workbook(encoding='utf-8', style_compression=0)
const.SHEET = const.BOOK.add_sheet(const.YEAR, cell_overwrite_ok=True)
const.SHEET.col(0).width = 1200
const.SHEET.col(1).width = 6000
const.SHEET.col(2).width = 5000
const.SHEET.col(3).width = 6000
const.SHEET.col(4).width = 20000
const.SHEET.col(5).width = 6000
const.SHEET.col(6).width = 5000
i = 0
for k in const.EXCEL_HEADER:
    const.SHEET.write(0, i, k)
    i = i + 1

#save fetched id list
def save_id_list(_data):
    with open(const.ID_LIST_FILENAME,'w') as fw:
        json.dump(_data,fw)

#read fetched id list
def read_id_list():
    if exists(const.ID_LIST_FILENAME):
        with open(const.ID_LIST_FILENAME,'r') as f:
            data = json.load(f)
            return data
    return []

#main funciton, fetch the list page
def get_list():
    id_list = read_id_list()
    res = requests.request('get', const.URL)
    if (res.status_code==200):
        data = import_excel()
        m_list = const.LIST_PATTERN.findall(res.text)
        for _id in m_list :
            if _id in id_list:
                continue
            else:
                item = get_item(_id)
                print("Fetching: "+_id)
                data.append(item)
                id_list.append(_id)
        save_id_list(id_list)
        data.sort(reverse=True)
        export_excel(data)

#fetch the detail page
def get_item(_id):
    url = const.HOST+_id
    res = requests.request('get', url)
    if (res.status_code==200):
        title = const.TITLE_PATTERN.search(res.text).group(1)
        author = const.AUTHOR_PATTERN.search(res.text).group(1)
        abstract = const.ABSTRACT_PATTERN.search(res.text).group(1)
        keyword = const.KEYWORD_PATTERN.search(res.text).group(1)
        origins = const.ORIGIN_PATTERN.search(res.text)
        origin = ''
        if origins:
            origin = origins.group(1)+origins.group(2)
        data = [_id, title, author, keyword, abstract, origin, url]
        return data

#export to excel file
def export_excel(_data):
    row = 1
    for val in _data:
        for _i in range(0,7):
            const.SHEET.write(row, _i, val[_i], const.EXCEL_STYLE)
        row = row + 1
    const.BOOK.save(const.XLS_FILENAME)

#import excel file
def import_excel():
    if not exists(const.XLS_FILENAME):
        return []
    file = xlrd.open_workbook(const.XLS_FILENAME)
    table = file.sheets()[0]
    data = []
    for r in range(1, table.nrows):
        line = table.row_values(r)
        data.append(line)
    return data


if __name__ == '__main__' :
    get_list()
    #print get_item("392")
    #print get_item("338")
    #print get_item("422")
