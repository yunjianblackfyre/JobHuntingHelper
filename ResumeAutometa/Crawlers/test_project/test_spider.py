#   AUTHOR: Sibyl System
#     DATE: 2018-09-28
#     DESC: 测试爬虫

import traceback
from scrapy.selector import Selector
from scrapy.http.cookies import CookieJar
from scrapy.crawler import CrawlerProcess
from scrapy import Request
from scrapy import Spider
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from ResumeAutometa.LogHandle.Log import Log
from ResumeAutometa.Crawlers.crawler_foundations.utils import *


# 专用测试爬虫类，用于处理复杂情况
class TestSpider(Spider):

    # 通用配置
    custom_settings = {
        'DNSCACHE_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        'RETRY_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 5,
        'DOWNLOAD_DELAY': 2.0,    # Greed is not good here
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS': 32,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 间隔时间随机化
        'HTTPERROR_ALLOW_ALL': True,  # 允许所有类型的返回通过中间件，调试用，发布时关闭
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'CONCURRENT_REQUESTS_PER_IP': 32,
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'ResumeAutometa.Crawlers.middlewares.downloader.random_user_agent.MyUserAgentMiddleware': 50,
            'ResumeAutometa.Crawlers.middlewares.downloader.exception_response.ExceptionResponse': 100
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
    
    name = "test"

    # 初始化爬虫，必须用名字
    def __init__(self):
        super(TestSpider, self).__init__()
        self.headers = self.HEADERS
        self.log_handler = Log(self.name + "_general", "crawler")
        self.cookie = None

    # 招聘信息菜单页请求
    def start_requests(self):
        # 开始重新全量爬取
        meta = dict()
        meta['cookiejar'] = CookieJar()
        start_urls = [
            # "http://www.httpbin.org/",              # HTTP 200 expected
            # "http://www.httpbin.org/status/404",    # Not found error
            # "http://www.httpbin.org/status/500",    # server issue
            # "http://www.httpbin.org:12345/",        # non-responding host, timeout expected
            # "http://www.httphttpbinbin.org/",       # DNS error expected
            "https://jobs.51job.com/shenzhen-lhxq/108448118.html"
        ]
        for request_url in start_urls:
            headers = deepcopy(self.headers)
            if self.cookie is not None:
                headers["Cookie"] = self.cookie
                print(self.cookie)
            yield Request(request_url, headers=headers, meta=meta, callback=self.parse_test, errback=self.errback_httpbin, dont_filter=False)
    
    # 进了这里就不会进parse_test了
    def errback_httpbin(self, failure):
        self.log_handler.log.error(repr(failure))

        if failure.check(DNSLookupError):
            request = failure.request
            self.log_handler.log.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.log_handler.log.error('TimeoutError on %s', request.url)
            
        else:
            request = failure.request
            self.log_handler.log.error('UnknownError on %s', request.url)
            self.log_handler.log.error('Detailed failure info: %s', str(failure))

    # 网页返回码异常后还是会进入这个方法（whitch sucks），所以这里需要手动检查一下response.status
    def parse_test(self, response):
        if response.status!=200:
            self.log_handler.log.error("WTF:%s", response.status)
            return
        try:
            self.cookie = cookie_from_jar(response)
            print(self.cookie)
            print("Response is good", response.status)
            sel = Selector(text=response.body)
            print(sel.css("div.tCompany_main > div:nth-child(3) > div").extract()[0])
            # print(response.body)
            
        except:
            print(traceback.format_exc())

    # 关闭爬虫时调用
    def closed(self, reason):
        print("spider closed")


if __name__ == '__main__':
    try:
        process = CrawlerProcess()

        process.crawl(TestSpider)
        process.start()  # the script will block here until the crawling is finished

    except Exception as e:
        print(traceback.format_exc())

