#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: 爬虫专用通用方法、变量、类

import html
from copy import deepcopy
from ResumeAutometa.Foundations.utils import *

# 爬取任务状态码
TASK_STATE = {
    'failure': 1,
    'success': 0,
}

REQ_FAIL_MARK = "FAILED_REQUEST"
REQ_FAIL_PROCFUN = "inform_failure"
ONE_TIME_MAXINSERT = 500000
PARSE_ERROR_TOLERANCE = 0.2

# 宏
html_unescape = lambda v: html.unescape(v)


pattern_dict = {
    ("<\s*","\s+[^<>]*>"):"\n",
    ("<",">"):"\n",
}

# 下列都是有换行效果的html标签
pattern_list = [
    "br",
    "div",
    "p",
    "ul",
    "ol",
    "li",
    "h[1-6]",
    "table",
    "menu",
    "hr",
    "form"
]


# 提取cookie
def cookie_from_jar(response):
    cookie_jar = response.meta['cookiejar']
    cookie_jar.extract_cookies(response, response.request)
    cookie_string_list = []
    for cookie in cookie_jar:
        cookie_string = '='.join([cookie.name, cookie.value])
        cookie_string_list.append(cookie_string)
    cookie_res_string = ';'.join(cookie_string_list)
    if not cookie_res_string:
        return None
    else:
        return cookie_res_string


# 清理HTML标签
def clean_html(content):
    content = html_unescape(content)
    for key in pattern_list:
        for key_type in pattern_dict.keys():
            pattern = key_type[0]+key+key_type[1]
            sub_str = pattern_dict[key_type]
            content = re.sub(pattern, sub_str, content)
    content = re.sub('<[^<>]+>', '', content)
    return content


# 通用HTML解析方法
def parse_html(parse_rule, content_sel, row_in, row_list, pn_url_list):
    # 初始化变量
    fields = parse_rule.get('fields', {})
    children_path = parse_rule.get('children_path', '')
    children = parse_rule.get('children', {})
    sel_list = []
    parse_errs = []
    success = True
    children_count = 0
    children_failed_count = 0

    # 如果没有列表字段，则返回
    if children_path:
        try:
            sel_list = content_sel.css(children_path)
        except Exception as e:
            # 此为大错，一定会打LOG
            success = False
            parse_errs.append('children extraction failed, error: %s, path %s' % (str(e), children_path))

        for sel in sel_list:
            row = deepcopy(row_in)
            for key, value in children["fields"].items():
                try:
                    children_count += 1
                    row[key] = clean_html(sel.css(value).extract()[0])
                except Exception as e:
                    parse_errs.append('children field extraction failed, error: %s, path %s' % (str(e), value))
                    children_failed_count += 1
                    row[key] = None

            for key, value in fields.items():
                try:
                    row[key] = clean_html(content_sel.css(value).extract()[0])
                except Exception as e:
                    parse_errs.append('field extraction failed, error: %s, path %s' % (str(e), value))
                    row[key] = None

            row_list.append(row)

    elif fields:
        row = deepcopy(row_in)
        for key, value in fields.items():
            try:
                children_count += 1
                row[key] = clean_html(content_sel.css(value).extract()[0])
            except Exception as e:
                parse_errs.append('field extraction failed, error: %s, path %s' % (str(e), value))
                children_failed_count += 1
                row[key] = None
        row_list.append(row)

    # 开始提取下一页链接
    if parse_rule.get('page_next'):
        path = parse_rule['page_next']
        try:
            pn_url_list.extend(content_sel.css(path).extract())
        except Exception as e:
            parse_errs.append('field extraction failed, error: %s, path %s' % (str(e), path))
            success = False

    if (children_failed_count/(float(children_count) + 0.001)) > PARSE_ERROR_TOLERANCE:
        success = False

    return success, parse_errs
    

if __name__ == '__main__':
    mystring = "<body>hahaha<div>hehehe</div>xixi</body>"
    print( clean_html(mystring) )
    pass