# AUTHOR: Sibyl System
# DATE: 2018-04-18
# DESC: 前程无忧 job列表API请求参数
#
#     搜索URL示例：
#     https://search.51job.com/list/040000,000000,0106,01,9,99,%2520,2,1.html 北京+计算机软件+高级软件工程师
#     https://search.51job.com/list/010000,000000,0106,01,9,99,%2520,2,1.html 深圳+计算机软件+高级软件工程师
#     https://search.51job.com/list/020000,000000,0106,01,9,99,%2520,2,1.html 上海+计算机软件+高级软件工程师
#     https://search.51job.com/list/020000,000000,0148,01,9,99,%2520,2,1.html 上海+计算机软件+算法工程师
#     https://search.51job.com/list/020000,000000,0148,31,9,99,%2520,2,1.html 上海+通信/电信+算法工程师
#     https://search.51job.com/list/01,000000,0106,01,9,99,%2520,2,1.html

# from scrapy import Request
from scrapy.crawler import CrawlerProcess
from ResumeAutometa.Crawlers.crawler_foundations.universal_spider import *

CITY_LIST = [
    "040000,000000",  # 北京
    "010000,000000",  # 深圳
    "020000,000000",  # 上海
    "030200,000000",  # 广州
    "180200,000000",  # 武汉
    "200200,000000",  # 西安
    "080200,000000",  # 杭州
    "070200,000000",  # 南京
    "090200,000000",  # 成都
    "060000,000000",  # 重庆
    "030800,000000",  # 东莞
    "230300,000000",  # 大连
    "230200,000000",  # 沈阳
    "070300,000000",  # 苏州
    "250200,000000",  # 昆明
    "190200,000000",  # 长沙
    "150200,000000",  # 合肥
    "080300,000000",  # 宁波
    "170200,000000",  # 郑州
    "050000,000000",  # 天津
    "120300,000000",  # 青岛
    "120200,000000",  # 济南

    "220200,000000",  # 哈尔滨
    "240200,000000",  # 长春
    "110200,000000",  # 福州
    "01,000000"  # 珠三角
]

CAT_LIST = [
    "0106,01,9,99",    # 高级软件工程师
    "0107,01,9,99",    # 软件工程师
    "0144,01,9,99",    # 软件UI设计师
    "0148,01,9,99",    # 算法工程师
    "0145,01,9,99",    # 仿真应用工程师
    "0146,01,9,99",    # ERP实施顾问
    "0117,01,9,99",    # ERP技术开发
    "0147,01,9,99",    # 需求工程师
    "0137,01,9,99",    # 系统集成工程师
    "0123,01,9,99",    # 系统分析员
    "0127,01,9,99",    # 系统工程师
    "0143,01,9,99",    # 系统架构设计师
    "0108,01,9,99",    # 数据库工程师
    "0141,01,9,99",    # 计算机辅助设计工程师
    "0142,01,9,99"     # 其他
]


class F1JobTaskSpider(JobTaskSpider):
    name = "51job"

    def __init__(self, task_interval=(0, 500)):
        super(F1JobTaskSpider, self).__init__(task_interval)
        self.headers["Host"] = "search.51job.com"

    # 本方法用于产生task spider的原生URL
    def _gen_search_requests(self):
        for city_elem in CITY_LIST:
            for cat_elem in CAT_LIST:
                url = "https://search.51job.com/list/" + city_elem + "," + cat_elem + ",%2520,2,1.html"
                task = dict()
                task["row"] = {"Ftask_info": json.dumps({"Fjob_cat": cat_elem})}
                task["url"] = url
                yield task


class F1JobDetailSpider(JobDetailSpider):
    name = "51job"

    def __init__(self):
        super(F1JobDetailSpider, self).__init__()
        self.headers["Host"] = "jobs.51job.com"

    def _load_detail_item(self, row, response):
        item = UniversalItem()
        item['row'] = {}
        item['from_url'] = response.meta["from_url"]
        item['settings'] = self.item_rule
        item['row'] = row
        if item["row"].get("Fjob_cat") is None:
            item["row"]["Fjob_cat"] = ""
        item['row']["Fjob_url"] = response.url
        item['row']["Fpub_time"] = time_now()
        item['row']["Fcreate_time"] = time_now()
        item['row']["Fmodify_time"] = time_now()
        return item


if __name__ == '__main__':
    try:
        process = CrawlerProcess()

        process.crawl(F1JobTaskSpider)
        process.start()  # the script will block here until the crawling is finished

    except Exception as e:
        print(traceback.format_exc())