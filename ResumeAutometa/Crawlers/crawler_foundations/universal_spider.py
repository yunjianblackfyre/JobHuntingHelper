#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: universal spider, father to all spider

import traceback
from scrapy.selector import Selector
from scrapy.http.cookies import CookieJar
from scrapy import Request
from scrapy import Spider, Item, Field
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from ResumeAutometa.Crawlers.crawler_foundations.crawler_db_handle import CCrawlerDbHandle
from ResumeAutometa.Crawlers.crawler_foundations.utils import *
from ResumeAutometa.Config.file_paths import CRAWLER_RULE
from ResumeAutometa.Foundations.exception import NotImplementedException
from ResumeAutometa.LogHandle.Log import Log

MAX_CRAWL_DETAILS = 15000  # 一次限定爬取的详情页数目


# 条目通用转化类：爬取条目->入库条目
class RowBuilder(object):
    def __init__(self):
        self._db = CCrawlerDbHandle()
        self.data = {}
        self.item_format = {}
        self.item_db = ""
        self.item_table = ""
        self.data_res = {}
        self.log_handler = None

    # 接受新的条目及其配置
    def update(self, item):
        settings = item['settings']  # 入库规则配置
        self.data = item['row']         # 基础原始数据，只读
        self.item_format = settings['item_format']
        self.item_db = settings['item_db']
        self.item_table = settings['item_table']
        self.data_res = {}
        
    # 用配置转化
    def build_row_from_item(self):
        for key in self.item_format.keys():
            field_type = self.item_format[key]['type']
            raw_field = self.data.get(key)
            type_convert = TYPE_CONVERT_MAP[field_type]
            self.data_res[key] = type_convert(raw_field)
            is_default = (TYPE_DEFAULT_VALUE_MAP[self.item_format[key]['type']] == self.data_res[key])
            is_required = self.item_format[key]['req']
            if is_default and is_required:
                return False  # 建立数据行失败
        return True
    
    # 自定义转化
    def build_row_from_custom(self):
        self.data_res['Fcreate_time'] = time_now()
        
    # 写数据库
    def write_database(self):
        self._db.set_db_table(self.item_db, self.item_table)
        # 构造入库条件
        condition_list = []
        update_data = deepcopy(self.data_res)
        for key in self.item_format.keys():
            if self.item_format[key]['dup']:
                condition = key + '=' + '\'' + str(self.data_res[key]) + '\''
                update_data.pop(key)    # 去掉作为更新条件的字段
                condition_list.append(condition)

        self._db.insert(self.data_res)
        self._db.commit()
    
    # 条目转化开始工作
    def process(self, item, spider):
        self.log_handler = spider.log_handler
        self.update(item)

        if self.build_row_from_item():
            self.build_row_from_custom()
            self.write_database()
            # self.log_handler.log.info("Item successfully wrote into database")
        else:
            if item.get("from_url", ""):
                failure_info = {
                    "url": item["from_url"],
                    "info": "ItemNotQualifyError"
                }
                spider.report_failure(failure_info)
            self.log_handler.log.info('Item is not qualified for writing database: %s' % str(self.data_res))


# 通用爬取条目类
class UniversalItem(Item):
    # define the fields for your item here like:
    row = Field() # row就是一个dict item[row][FXXX]
    from_url = Field()
    settings = Field()
    row_builder = RowBuilder()


# 通用入库流水线类
class UniversalPipeline(object):

    def close_spider(self, spider):
        spider.log_handler.log.info("close UniversalPipeline")
        
    def process_item(self, item, spider):
        try:
            item.row_builder.process(item, spider)
        except:
            if item.get("from_url", ""):
                failure_info = {
                    "url":item["from_url"],
                    "info":"ItemDBError"    # 很少见的错误，该数据被数据库拒绝
                }
                spider.report_failure(failure_info)
            err_msg = str(traceback.format_exc())
            spider.log_handler.log.info("UniversalPipeline Exception: %s" % err_msg)
            
            
# 通用爬虫类
class JobDetailSpider(Spider):

    # 通用配置
    custom_settings = {
        'DNSCACHE_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        'RETRY_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 60,
        'DOWNLOAD_DELAY': 0.8,  # Greed is not good here
        'CONCURRENT_REQUESTS': 32,
        'HTTPERROR_ALLOW_ALL': True,  # 允许所有类型的返回通过中间件，调试用，发布时关闭
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'CONCURRENT_REQUESTS_PER_IP': 32,
        'COOKIES_ENABLED': True,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 间隔时间随机化
        'DOWNLOADER_MIDDLEWARES': {
            'ResumeAutometa.Crawlers.middlewares.downloader.random_user_agent.MyUserAgentMiddleware': 50,
            'ResumeAutometa.Crawlers.middlewares.downloader.exception_response.ExceptionResponse': 100
        },
        'ITEM_PIPELINES': {
            'ResumeAutometa.Crawlers.crawler_foundations.universal_spider.UniversalPipeline': 100
        }
    }
    
    # 通用请求报头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh,zh-HK;q=0.8,zh-CN;q=0.7,en-US;q=0.5,en;q=0.3,el;q=0.2',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }
    
    # 初始化爬虫
    def __init__(self):
        super(JobDetailSpider, self).__init__()
        self.log_handler = Log(self.name + "_detail", "crawler")
        self.headers = self.HEADERS
        self.cookie = None
        self._db = CCrawlerDbHandle()
        self.__load_config_file()
        self.__find_new_tasks()

    # 读取解析逻辑与入库逻辑
    def __load_config_file(self):
        item_rule_file = CRAWLER_RULE + self.name + "_detail_item_rule.txt"
        item_parse_rule = CRAWLER_RULE + self.name + "_detail_parse_rule.txt"
        self.item_rule = read_file_json(item_rule_file)
        self.parse_rule = read_file_json(item_parse_rule)

    # 寻找需要爬取的新任务
    def __find_new_tasks(self):
        self.dup_groups = []
        today = datetime.now()
        this_month = today.month
        url2info = dict()
        self.this_season = this_month // 3  # 3个月一个季度

        self.item_rule["item_table"] = "t_" + self.name + "_detail_" + str(self.this_season)
        self.item_rule["task_table"] = "t_" + self.name + "_task_" + str(self.this_season)
        self.item_rule["failed_table"] = "t_" + self.name + "_failed_" + str(self.this_season)

        # 获取detail表url集合
        self._db.set_db_table("db_crawlers", self.item_rule["item_table"])
        field_list = ["Fjob_url"]
        where = "1"
        old_urls = self._db.query(field_list, where)
        old_urls = set([url_info["Fjob_url"] for url_info in old_urls])

        # 获取task表url集合
        self._db.set_db_table("db_crawlers", self.item_rule["task_table"])
        field_list = ["Ftask_url", "Ftask_info"]
        where = "1"
        tasks = self._db.query(field_list, where)
        for task in tasks:
            task_url = task["Ftask_url"]
            task_info = task["Ftask_info"]
            url2info[task_url] = task_info
        cur_urls = set([task["Ftask_url"] for task in tasks])
        
        # 获取failure表url集合
        self._db.set_db_table("db_crawlers_failure", self.item_rule["failed_table"])
        field_list = ["Ffail_url"]
        where = "Fretry_time > 2"
        dead_urls = self._db.query(field_list, where)
        dead_urls = set([url_info["Ffail_url"] for url_info in dead_urls])
        
        new_urls = cur_urls.difference(old_urls)
        new_urls = new_urls.difference(dead_urls)
        new_urls = list(new_urls)

        for url in new_urls[0:MAX_CRAWL_DETAILS]:
            task = dict()
            task["url"] = url
            try:
                task["data"] = json.loads(url2info[url])
            except:
                task["data"] = dict()
            yield task
    
    # 网络请求异常记录写入数据库
    def report_failure(self, failure_info):
        request_url = failure_info["url"]
        info = failure_info["info"]
        if not request_url:
            return
        request_url_safe = self._db.escape(request_url)

        self._db.set_db_table("db_crawlers_failure", self.item_rule["failed_table"])
        field_list = ["Fauto_id", "Fretry_time"]
        where = "Ffail_url='%s' limit 1" % request_url_safe
        DB_res = self._db.query(field_list, where)
        self._db.commit()
        
        if DB_res:
            auto_id = DB_res[0]["Fauto_id"]
            retry_time = int(DB_res[0]["Fretry_time"])
            where = "Fauto_id=%s" % auto_id
            datau = {
                "Fretry_time":retry_time + 1,
                "Finfo":info,
                "Fmodify_time":time_now()
            }
            self._db.update(datau, where)
            self._db.commit()
        else:
            datai = {
                "Ffail_url": request_url_safe,
                "Fretry_time": '0',
                "Finfo": info
            }
            self._db.insert(datai)
            self._db.commit()
        
    # 招聘信息产生新请求
    def start_requests(self):
        # 开始重新全量爬取
        # tmp_list = [{"data": {"Fjob_cat": -1}, "url": "https://jobs.zhaopin.com/CC469217519J00090118811.htm"}]
        # for task in tmp_list:
        for task in self.__find_new_tasks():
            meta = dict()
            meta["row"] = task["data"]
            meta["from_url"] = task["url"]
            meta["cookiejar"] = CookieJar()
            headers = deepcopy(self.headers)
            if self.cookie is not None:
                headers['Cookie'] = self.cookie

            request_url = task['url']
            # self.log_handler.log.info("Send detail request %s" % request_url)
            yield Request(request_url, headers=headers, meta=meta, callback=self.parse_detail, 
                          errback=self.errback_httpbin, dont_filter=True)
    
    # 请求无返回异常处理
    def errback_httpbin(self, failure):
        request = failure.request
        if failure.check(DNSLookupError):
            info = "DNSLookupError"
            self.log_handler.log.info('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError):
            info = "TimeoutError"
            self.log_handler.log.info('TimeoutError on %s', request.url)
        else:
            info = "UnknownError"
            self.log_handler.log.info('UnknownError on %s', request.url)
            # self.log_handler.log.info('Detailed failure info: %s', str(failure))
            
        fail_url = request.url
        failure_info = {
            "url": fail_url,
            "info": info
        }
        self.report_failure(failure_info)

    # 解析招聘信息详情页
    def parse_detail(self, response):
        if response.status != 200:
            return
        try:
            # Detail Spider独有，通过任意一个返回获取cookie
            # if self.cookie is None:
            self.cookie = cookie_from_jar(response)
            # 解析页面，获取元数据
            row_list = []
            row = response.meta['row']
            content_sel = Selector(response)
            success, parse_errs = parse_html(self.parse_rule, content_sel, row, row_list, [])

            if not success:
                parse_err_msg = "\n".join(parse_errs)
                self.log_handler.log.info("Parsing detail page failed with url %s, err_msg %s" %
                                          (response.url, parse_err_msg))

            for row in row_list:
                yield self._load_detail_item(row, response)
        except:
            # 解析的页面结构变化，报警
            failure_info = {
                "url": response.meta["from_url"],
                "info": "PageParseError"
            }
            self.report_failure(failure_info)
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("Parsing detail page exception with url %s, err_msg %s" %
                                      (response.url, err_msg))

    # 本方法用于预处理爬到的数据（包括去重）并提交item pipeline
    def _load_detail_item(self, data, url):
        raise NotImplementedException

    # 关闭爬虫时调用
    def closed(self, reason):
        self.log_handler.log.info(str(self.stats))
        self._db.destroy()
        self.log_handler.log.info("CLOSE_REASON:%s" % reason)


# 通用招聘任务爬虫类
class JobTaskSpider(Spider):

    # 通用配置
    custom_settings = {
        'DNSCACHE_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        'RETRY_ENABLED': True,
        'DOWNLOAD_TIMEOUT': 5,
        'DOWNLOAD_DELAY': 1.0,    # Greed is not good here
        'LOG_LEVEL': 'ERROR',
        'CONCURRENT_REQUESTS': 32,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 间隔时间随机化
        'HTTPERROR_ALLOW_ALL': True,  # 允许所有类型的返回通过中间件，调试用，发布时关闭
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'CONCURRENT_REQUESTS_PER_IP': 32,
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'ResumeAutometa.Crawlers.middlewares.downloader.random_user_agent.MyUserAgentMiddleware': 50,
            'ResumeAutometa.Crawlers.middlewares.downloader.exception_response.ExceptionResponse': 100
        },
        'ITEM_PIPELINES': {
            'ResumeAutometa.Crawlers.crawler_foundations.universal_spider.UniversalPipeline': 100
        }
    }

    # 通用请求报头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh,zh-HK;q=0.8,zh-CN;q=0.7,en-US;q=0.5,en;q=0.3,el;q=0.2',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
    }

    # 初始化爬虫，必须用名字
    def __init__(self, task_interval):
        super(JobTaskSpider, self).__init__()
        self.headers = self.HEADERS
        self.cookie = None
        self.task_interval = task_interval
        self._db = CCrawlerDbHandle()
        self.__load_config_file()
        self.__build_dup_filter()
        self.log_handler = Log(self.name + "_task", "crawler")

    # 建立URL去重组，确保爬取任务不重复
    def __build_dup_filter(self):
        self.dup_groups = []
        today = datetime.now()
        this_month = today.month
        self.this_season = this_month // 3  # 3个月一个季度
        self.item_rule["item_table"] = "t_" + self.name + "_task_" + str(self.this_season)
        seasons = list(range(0, self.this_season + 1))
        seasons.reverse()

        for idx in seasons:
            table_name = '_'.join(['t', self.name, 'task', str(idx)])
            self._db.set_db_table("db_crawlers", table_name)
            field_list = ["Ftask_url"]
            where = "1"
            url_items = self._db.query(field_list, where)
            self._db.commit()
            urls = [item["Ftask_url"] for item in url_items]
            unique_urls = set(urls)
            self.dup_groups.append(unique_urls)
        # print_list(self.dup_groups)

    # 读取解析逻辑与入库逻辑
    def __load_config_file(self):
        item_rule_file = CRAWLER_RULE + self.name + "_task_item_rule.txt"
        item_parse_rule = CRAWLER_RULE + self.name + "_task_parse_rule.txt"
        self.item_rule = read_file_json(item_rule_file)
        self.parse_rule = read_file_json(item_parse_rule)

    # 招聘信息菜单页请求
    def start_requests(self):
        # 开始重新全量爬取
        task_interval = self.task_interval
        task_requests = list(self._gen_search_requests())
        for task in task_requests[task_interval[0]:task_interval[1]]:
            headers = deepcopy(self.headers)
            if self.cookie is not None:
                headers['Cookie'] = self.cookie

            meta = dict()
            meta['cookiejar'] = CookieJar()
            meta['row'] = task['row']
            request_url = task['url']
            yield Request(request_url, headers=headers, meta=meta,
                          callback=self.parse_task, errback=self.errback_httpbin, dont_filter=True)

    # 请求无返回异常处理
    def errback_httpbin(self, failure):
        request = failure.request
        if failure.check(DNSLookupError):
            self.log_handler.log.info('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError):
            self.log_handler.log.info('TimeoutError on %s', request.url)
        else:
            self.log_handler.log.info('UnknownError on %s', request.url)
            self.log_handler.log.info('Detailed failure info: %s', str(failure))

    # 解析招聘信息列表页（有被重写的可能，如果返回不是html文件）
    def parse_task(self, response):
        try:
            # 解析页面，获取元数据
            content_sel = Selector(response)
            row = response.meta['row']
            # if self.cookie is None:
            self.cookie = cookie_from_jar(response)
            row_list = []
            pn_url_list = []

            success, parse_errs = parse_html(self.parse_rule, content_sel, row, row_list, pn_url_list)

            if not success:
                parse_err_msg = "\n".join(parse_errs)
                self.log_handler.log.info("Parsing task page failed with url %s, err_msg %s" %
                                          (response.url, parse_err_msg))

            # 产生最终数据行
            for row_item in row_list:
                final_item = self._load_task_item(row_item)
                if final_item is not None:
                    yield final_item
            
            if "page_next" not in self.parse_rule.keys():
                request = self._gen_pagination(response)
                if request is not None:
                    yield request

            # 提交下一页请求
            if pn_url_list:
                pn_url = pn_url_list[0]
                meta = response.meta
                headers = deepcopy(self.headers)
                headers['Cookie'] = cookie_from_jar(response)  # 兵不厌诈，BENDEJO
                yield Request(pn_url, headers=headers, meta=meta, callback=self.parse_task,
                              dont_filter=True)
            
        except:
            # 解析的页面结构变化，报警
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("Parsing task page exception with url %s, err_msg %s" %
                                      (response.url, err_msg))

    # 本方法用于预处理爬到的数据（包括去重）并提交item pipeline
    def _load_task_item(self, row_item):
        item = UniversalItem()
        item['row'] = {}
        item['settings'] = self.item_rule
        task_url = row_item["Ftask_url"]
        task_info = row_item["Ftask_info"]
        for dup_group in self.dup_groups:
            if task_url in dup_group:
                return None
        self.dup_groups[0].add(task_url)
        item['row']['Ftask_url'] = task_url
        item['row']['Ftask_info'] = task_info
        return item

    # 本方法用于在某些情况下需要特殊方法产生下一页请求的场景
    def _gen_pagination(self, response):
        raise NotImplementedException

    # 本方法用于产生task spider的原生URL
    def _gen_search_requests(self):
        raise NotImplementedException

    # 关闭爬虫时调用
    def closed(self, reason):
        self.log_handler.log.info(str(self.stats))
        self._db.destroy()
        self.log_handler.log.info("CLOSE_REASON:%s" % reason)


if __name__ == '__main__':
    pass
