#   AUTHOR: Sibyl System
#     DATE: 2018-09-18
#     DESC: tencent spider

# from scrapy import Request
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, parse_qs, urljoin, urlencode, ParseResult
from ResumeAutometa.Crawlers.crawler_foundations.universal_spider import *

LID_LIST = [    # 工作地点
    "2218",      # 深圳
    "2156",      # 北京
    "2175",      # 上海
    "2196",      # 广州
    "2268",      # 成都
    "2252",      # 杭州
    "2426",      # 昆明
    "33",        # 美国
    "2459",      # 中国香港
    "2418",      # 长春
    "2355",      # 武汉
    "2226",      # 重庆
    "90",        # 荷兰
    "2406",      # 沈阳
    "2381",      # 西安
    "59",        # 日本
    "2436",      # 贵阳
    "2393",      # 太原
    "2346",      # 郑州
    "2314",      # 南宁
    "2442",      # 呼和浩特
    "2458",      # 西宁
    "95",        # 雄安新区
    "81",        # 新加坡
    "2320",      # 合肥
    "2439",      # 兰州
    "2448",      # 银川
    "2225",      # 天津
    "2407",      # 大连
    "2453",      # 乌鲁木齐
    "2336",      # 石家庄
    "2283"      # 福州
]

TID_LIST = ["87"]


class TencentTaskSpider(JobTaskSpider):
    name = "tencent"

    def __init__(self, task_interval=(0, 1)):
        super(TencentTaskSpider, self).__init__(task_interval)
        self.headers["Host"] = "hr.tencent.com"

    # 本方法用于产生task spider的原生URL
    def _gen_search_requests(self):

        for lid_elem in LID_LIST:
            for tid_elem in TID_LIST:
                query_tup = (('lid', lid_elem), ('tid', tid_elem), ('isfilter', '1'))

                url_info = ParseResult(scheme='https', netloc='hr.tencent.com', path='/position.php',
                                       params='', query=urlencode(query_tup), fragment='')
                url = url_info.geturl()
                task = dict()
                task["data"] = dict()
                task["url"] = url
                task["cookie"] = dict()
                yield task

    # 本方法用于在某些情况下需要特殊方法产生下一页请求的场景
    def _gen_pagination(self, response):
        try:
            content_sel = Selector(response)
            next_page_url = content_sel.css("#next::attr(href)").extract_first()
            next_page_url = urljoin(response.url, next_page_url)
            meta = response.meta
            headers = deepcopy(self.headers)
            headers['Cookie'] = cookie_from_jar(response)  # 兵不厌诈，BENDEJO
            return Request(next_page_url, headers=headers, meta=meta, callback=self.parse_task,
                           dont_filter=True)
        except:
            return None

    def _load_task_item(self, row_item):
        item = UniversalItem()
        item['row'] = {}
        item['settings'] = self.item_rule
        task_url = urljoin("https://hr.tencent.com/", row_item["Ftask_url"])
        for dup_group in self.dup_groups:
            if task_url in dup_group:
                return None
        self.dup_groups[0].add(task_url)
        item['row']['Ftask_url'] = task_url
        return item


class TencentDetailSpider(JobDetailSpider):
    name = "tencent"

    def __init__(self):
        super(TencentDetailSpider, self).__init__()
        self.headers["Host"] = "hr.tencent.com"

    def _load_detail_item(self, data, url):
        item = UniversalItem()
        item['row'] = {}
        item['from_url'] = url
        item['settings'] = self.item_rule
        item['row'] = data
        item['row']['Fjob_detail'] = data["Fjob_detail_1"] + data["Fjob_detail_2"]
        item['row']["Freq_year"] = ''
        item['row']["Fsalary"] = ''
        item['row']["Fgang_detail"] = ''
        item['row']["Freq_edu"] = ''
        item['row']["Fgang_name"] = '深圳市腾讯计算机系统有限公司'  # 写死的哦，嘿嘿
        item['row']["Fpub_time"] = time_now()
        item['row']["Fcreate_time"] = time_now()
        item['row']["Fmodify_time"] = time_now()
        return item


if __name__ == '__main__':
    try:
        process = CrawlerProcess()

        process.crawl(TencentTaskSpider)
        process.start()  # the script will block here until the crawling is finished

    except Exception as e:
        print(traceback.format_exc())
