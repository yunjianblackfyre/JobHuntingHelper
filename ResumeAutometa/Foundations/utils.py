# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-01-01
#     DESC: 最通用变量、方法、类

import time
import random
import json
import re
import os
import sys
from urllib.parse import urlparse
from datetime import datetime


def list2chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


# 判断一个路径到底是css还是xpath路径
def is_xpath(path):
    elements = [element for element in path.split("/") if element.strip()]
    if len(elements) > 1:
        return True
    else:
        return False


# 通用类型转换
def tryconvert(value, default, *types):
    for t in types:
        try:
            if value == None:
                return default
            else:
                return t(value)
        except:
            continue
    return default


# 返回一个范围内的非重复随机数列表
def sample_rand(lower_bound, upper_bound, sample_num):
    if sample_num < 1:
        return []
    elif upper_bound - lower_bound <= sample_num:
        return []
    elif upper_bound - lower_bound > 1:
        return random.sample(range(lower_bound, upper_bound), sample_num)
    if upper_bound - lower_bound == 1:
        return [lower_bound]
    else:
        return []


# MapReduce函数
def map_reduce(mydict, key, inc=1):
    if key in mydict.keys():
        mydict[key] += inc
    else:
        mydict[key] = inc
        

def map_reduce_list(input_dict, input_key, input_value):
    if input_key in input_dict.keys():
        input_dict[input_key].append(input_value)
    else:
        input_dict[input_key] = [input_value]


# 词典排序，输出结果为元组列表
def sort_dict(mydict):
    return sorted(mydict.items(), key=lambda d: d[1])


def write_data2json(data, file_path):
    out = open(file_path, 'wb')
    out.write(bytes(json.dumps(data).encode()))
    out.close()


def read_file_json(file_path):
    f = open(file_path, 'rb')
    data = json.loads(f.read().decode())
    return data


def read_lines(file_name):
    f = open(file_name)
    cache = f.readlines()
    f.close()
    return cache
    
    
def write_lines(data, file_name):
    # open不支持utf8编码，which sucks
    f = open(file_name, "w")
    # f = codecs.open(file_name, "w", encoding='utf-8')
    for line in data:
        # write line to output file
        try:
            line = line.strip()
            f.write(line)
            f.write("\n")
        except:
            print([line])
    f.close()


# 内存友好的读文件方式
def read_in_chunks(file_name, chunk_size=1024):
    file_obj = open(file_name, "r")
    while True:
        data = file_obj.read(chunk_size)
        if not data:
            break
        yield data
    
    
def intergrate_files(group_name, group_path):
    file_list = []
    pattern = "^" + group_name + ".+\.txt"
    final_file = group_path + group_name + ".txt"
    for file_name in os.listdir(group_path):
        if re.match(pattern, file_name):
            file_list.append(file_name)

    great_list = []
    for file_name in file_list:
        cache = read_lines(group_path + file_name)
        great_list.extend(list(cache))
    write_lines(great_list, final_file)

    time.sleep(2) # 等待此文件写完后，再删除小组文件
    for file_name in file_list:
        os.remove(group_path + file_name)
        
        
def remove_group_files(group_name, group_path):
    file_list = []
    pattern = "^" + group_name + ".+\.txt"
    final_file = group_path + group_name + ".txt"
    for file_name in os.listdir(group_path):
        if re.match(pattern, file_name):
            file_list.append(file_name)

    time.sleep(2)  # 等待此文件写完后，再删除小组文件
    file_list.append(final_file)
    for file_name in file_list:
        os.remove(group_path + file_name)


int_data_convert = lambda v: tryconvert(v, 0, int)
str_data_convert = lambda v: tryconvert(v, '', str)
time_now = lambda: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))


# 全局变量
TYPE_CONVERT_MAP = {
    'str': str_data_convert,
    'int': int_data_convert,
}

# 数据类型默认值
TYPE_DEFAULT_VALUE_MAP = {
    'str': '',
    'int': 0,
}


# 获取当前的季度
def get_current_season():
    today = datetime.now()
    this_month = today.month
    this_season = this_month // 3  # 3个月一个季度
    return this_season


# 通用对象详情打印
def dump_object(obj):
    for attr in dir(obj):
        if hasattr(obj, attr):
            print("obj.%s = %s" % (attr, getattr(obj, attr)))


# 通用调试组
def print_dict(dict_src, params={}):
    if params.get('newline'):
        for key, value in dict_src.items():
            print(key, ':', str(value), '\n')
    else:
        for key, value in dict_src.items():
            print(key, ':', str(value))


def print_list(list_src, params={}):
    if params.get('newline'):
        for item in list_src:
            print(item, '\n')
    else:
        for item in list_src:
            print(item)


# 返回一个对象的真实大小
def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects

    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


# 从字符串中获取格式化时间
def gettime_from_string(time_str):
    # 输入字符格式 2018年04月17日 12:57:40
    # 标准时间格式 1970-01-01 00:00:00
    month = 0
    year = 0
    day = 0
    hour = 0
    minute = 0
    second = 0

    result = re.findall('(\d+)年(\d+)月(\d+)日', time_str)
    if result:
        result = result[0]
        year = int(result[0])
        month = int(result[1])
        day = int(result[2])
    else:
        return ''

    result = re.findall('(\d+)[:：](\d+)[:：](\d+)', time_str)
    if result:
        result = result[0]
        hour = int(result[0])
        minute = int(result[1])
        second = int(result[2])

    try:
        dt = datetime(year, month, day, hour, minute, second)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ''


def check_url(url):
    # URL 检测函数，scheme netloc path必须都有
    url_info = urlparse(url)
    if not (url_info.scheme and url_info.netloc and url_info.path):
        return False
    else:
        return True
        
     
def get_sql_in_condition_string(id_list):
    for idx in range(len(id_list)):
        id_list[idx] = "'"+str(id_list[idx])+"'"
    if len(id_list) > 1:
        id_list_str = '(' + ','.join(id_list) + ')'
    elif len(id_list)==1:
        id_list_str = '(' + id_list[0] + ')'
    else:
        id_list_str = ""
    return id_list_str


# 通用计时器
class StopWatch(object):

    def __init__(self):
        self.reset()

    def get_elapsed_milliseconds(self):
        return "%0.2f" % ((time.time() - self._start_time) * 1000)

    def get_elapsed_seconds(self):
        return "%0.2f" % (time.time() - self._start_time)

    def reset(self):
        self._start_time = time.time()

        
if __name__ == '__main__':
    for piece in read_in_chunks("./test.txt", 10):
        print(piece)
