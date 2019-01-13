# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-08-10
#     DESC：职位文档批量处理专用通用方法、变量、对象


def get_sql_in_condition_string(index_list):
    for idx in range(len(index_list)):
        index_list[idx] = "'"+index_list[idx]+"'"
    if len(index_list) > 1:
        index_list_str = '(' + ','.join(index_list) + ')'
    elif len(index_list)==1:
        index_list_str = '(' + index_list[0] + ')'
    else:
        index_list_str = ""
    return index_list_str