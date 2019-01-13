# AUTHOR: Sibyl System
# DATE: 2018-04-18
# DESC: 新版智联job列表API请求参数
#
#     1. pageSize:60  # 固定参数：列表长度（默认60行）
#     2. cityId: 773  # 动态参数：城市ID
#     3. industry:10100 # 固定参数：行业（默认互联网/IT）
#     4. workExperience: # 固定参数： 工作经验
#     5. education: -1 # 固定参数：教育背景
#     6. jobType: 666 # 动态参数：职位类型（系统集成工程师）
#     6. companyType: -1 # 固定参数：公司类型（默认不限）
#     7. employmentType: -1 # 固定参数：工作类型（默认不限）
#     8. jobWelfareTag: -1 # 固定参数：公司福利类型（默认不限）
#     9. kt: 3 # 固定参数：不知道是什么鬼（默认为3）

from scrapy.crawler import CrawlerProcess
from urllib.parse import parse_qs, urlencode, ParseResult
from ResumeAutometa.Crawlers.crawler_foundations.universal_spider import *

city_id_list = ["765", "530", "538", "763", "531", "801", "653", "736", "600", "613", "635", "702",
                "599", "854", "719", "749", "551", "622", "636", "654", "680", "682", "565", "664", "773"]

job_type_list = ["045", "044", "864", "2040", "079", "054", "047", "2039", "669",
                   "687", "057", "2034", "667", "2041", "2038", "053", "671", "665",
                   "2042", "679", "666", "048", "861", "317", "2035", "672", "863",
                   "668", "2037", "2043", "2036", "060"]


class ZhilianTaskSpider(JobTaskSpider):

    name = "zhilian"
    
    def __init__(self, task_interval=(0, 1000000)):
        super(ZhilianTaskSpider, self).__init__(task_interval)
        self.headers["Host"] = "fe-api.zhaopin.com"
    
    # 本方法用于产生task spider的原生URL
    def _gen_search_requests(self):
        for city_id in city_id_list:
            for job_type in job_type_list:
                query_tup = (("cityId", city_id), ("education", "-1"), ("work_experience", "-1"),
                             ("industry", "10100"), ("companyType", "-1"), ("employmentType", "-1"),
                             ("jobWelfareTag", "-1"), ("kt", "3"), ("pageSize", "60"), ("jobType", job_type))
                url_info = ParseResult(scheme='https', netloc='fe-api.zhaopin.com', path='/c/i/sou',
                                       params='', query=urlencode(query_tup), fragment='')
                url = url_info.geturl()
                task = dict()
                task["url"] = url
                task["row"] = {"Ftask_info": json.dumps({"Fjob_cat": job_type})}
                yield task

    # 解析招聘信息列表页（有被重写的可能，如果返回不是html文件）
    def parse_task(self, response):
        try:
            # 解析页面，获取元数据
            response_dict = json.loads(response.body.decode())
            for job_item in response_dict["data"]["results"]:
                row_item = dict()
                row_item.update(response.meta["row"])
                row_item["Ftask_url"] = job_item["positionURL"]
                final_item = self._load_task_item(row_item)
                if final_item is not None:
                    yield final_item

            if response_dict["data"]["results"]:
                url_info = urlparse(response.url)
                parse_dict = parse_qs(url_info.query, keep_blank_values=True)

                current_offset = parse_dict.get("start", ['0'])[0]
                next_offset = str(int(current_offset) + 60)
                parse_dict["start"] = [next_offset]
                query_list = []
                for key, value in parse_dict.items():
                    if value:
                        query_list.append((key, value[0]))
                next_page_query = urlencode(query_list)
                url_info = url_info._replace(query=next_page_query)
                next_page_url = url_info.geturl()
                headers = deepcopy(self.headers)
                headers['Cookie'] = cookie_from_jar(response)
                yield Request(next_page_url, headers=headers, meta=response.meta,
                              callback=self.parse_task, dont_filter=True)

        except:
            # 解析的页面结构变化，报警
            err_msg = str(traceback.format_exc())
            self.log_handler.log.info("Parsing task page exception with url %s, err_msg %s" %
                                      (response.url, err_msg))

    # 本方法用于在某些情况下需要特殊方法产生下一页请求的场景
    def _gen_pagination(self, response):
        raise NotImplementedException


class ZhilianDetailSpider(JobDetailSpider):
    name = "zhilian"

    def __init__(self):
        super(ZhilianDetailSpider, self).__init__()
        # self.headers["Host"] = "jobs.zhaopin.com"

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

        process.crawl(ZhilianDetailSpider)
        process.start()  # the script will block here until the crawling is finished
    
    except Exception as e:
        print(traceback.format_exc())
