#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: 异常响应截取，并记录到数据库

from scrapy import signals
from pydispatch import dispatcher
from ResumeAutometa.Crawlers.crawler_foundations.utils import *


class ExceptionResponse(object):
    """This middleware enables processing response with unexpected status code"""

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        spider.log_handler.log.info("close ExceptionResponse")

    def process_response(self, request, response, spider):
        status_code = response.status
        if response.status == 200:
            return response

        record_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        spider.log_handler.log.info("ERROR RESPONSE STATUS is: %s, url: %s, time: %s" %
                                    (status_code, response.url, record_time))

        try:
            self.inform_failure(request, response, spider)  # 将失败的请求写入数据库
            spider.log_handler.log.info("ERROR RESPONSE INFO IS :%s" % str(request.meta))
        except Exception as e:
            spider.log_handler.log.info("MIDDLEWARE PROCESS EXCEPTION:%s" % e)

        return response

    # 失败请求会写通用表
    def inform_failure(self, request, response, spider):
        fail_url = request.url
        status_code = response.status
        info = "HttpError:%s" % status_code
        failure_info = {
            "url":fail_url,
            "info":info
        }
        spider.report_failure(failure_info)