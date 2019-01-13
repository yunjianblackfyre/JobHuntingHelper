# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: 爬虫启动器：接受参数输入，启动相应的爬虫

import traceback
import sys
from ResumeAutometa.LogHandle.Log import Log
from scrapy.crawler import CrawlerProcess
from ResumeAutometa.Crawlers.tencent_project.tencent_spider import TencentTaskSpider
from ResumeAutometa.Crawlers.tencent_project.tencent_spider import TencentDetailSpider
from ResumeAutometa.Crawlers.zhilian_project.zhilian_spider import ZhilianTaskSpider
from ResumeAutometa.Crawlers.zhilian_project.zhilian_spider import ZhilianDetailSpider

TASK_NAMES = [
    "zhilian_task",
    "tencent_task"
]

DETAIL_NAMES = [
    "zhilian_detail",
    "tencent_detail"
]


class CSpiderShell(object):
    def __init__(self, arg_list):
        self.log_handler = Log("spider_shell", "crawler")
        self.arg_list = arg_list

    def run(self):
        try:
            arg_list = self.arg_list
            if len(arg_list) not in [3, 5]:
                self.log_handler.log.info("Wrong number of arguments, exiting Spider Shell")
                return

            if len(arg_list) == 5:
                spider_name = arg_list[2]
                begin = int(arg_list[3])
                end = int(arg_list[4])
                task_interval = (begin, end)

                if spider_name in TASK_NAMES:
                    task_function = getattr(self, spider_name)
                    task_function(task_interval)
                else:
                    self.log_handler.log.info("no proper spider found, exiting Spider Shell")

            elif len(arg_list) == 3:
                spider_name = arg_list[2]
                if spider_name in DETAIL_NAMES:
                    detail_function = getattr(self, spider_name)
                    detail_function()
                else:
                    self.log_handler.log.info("no proper spider found, exiting Spider Shell")

        except:
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("spider shell critical error")
            self.log_handler.log.info(err_msg)

    def zhilian_task(self, task_interval):
        try:
            process = CrawlerProcess()
            process.crawl(ZhilianTaskSpider, task_interval=task_interval)
            process.start()
        except:
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("zhilian task spider critical error")
            self.log_handler.log.info(err_msg)

    def tencent_task(self, task_interval):
        try:
            process = CrawlerProcess()
            process.crawl(TencentTaskSpider, task_interval=task_interval)
            process.start()  # the script will block here until the crawling is finished
        except:
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("tencent task spider critical error")
            self.log_handler.log.info(err_msg)

    def zhilian_detail(self):
        try:
            process = CrawlerProcess()
            process.crawl(ZhilianDetailSpider)
            process.start()  # the script will block here until the crawling is finished
        except:
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("zhilian detail spider critical error")
            self.log_handler.log.info(err_msg)

    def tencent_detail(self):
        try:
            process = CrawlerProcess()
            process.crawl(TencentDetailSpider)
            process.start()  # the script will block here until the crawling is finished
        except:
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("tencent detail spider critical error")
            self.log_handler.log.info(err_msg)


if __name__ == '__main__':
    manager = CSpiderShell(["python3"] + list(sys.argv))
    manager.run()
