# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-01-03

'''
csdn资讯预处理程序
预处理结果分为以下几类

1.处理成功，无缺陷
2.处理成功，有缺陷
3.处理失败，有异常

缺陷和异常分为以下两种方式记录
1.单次记录，作为log输出
2.多次记录，作为statistic输出

预处理结果目前写日志文件
后续考虑替换为数据库
因为对预处理结果的观察学习
有助于后续预处理程序的优化
以及对于源数据的认知
'''

# import ssl
# import requests
# import urllib.request
# from urllib.request import Request

# import traceback

from ResumeAutometa.ServerData.utils import get_sql_in_condition_string
from ResumeAutometa.Foundations.utils import *
from ResumeAutometa.Computation.preprocessor import ProdContentPreproc
from ResumeAutometa.ServerData.server_db_handle import CServerDbHandle
from ResumeAutometa.Computation.preprocessor import CContentClassifier


def gen_season_num():
    today = datetime.now()
    this_month = today.month
    this_season = this_month // 3  # 3个月一个季度
    return this_season


class CJobPreproc(object):
    def __init__(self):
        # 初始化无火的灰烬
        self.firelinker = dict()

        # 初始化DB链接
        self._db = CServerDbHandle()

        # 初始化招聘文本预处理器
        self.content_proc_handler = ProdContentPreproc()

        self.classifier = CContentClassifier()

    def __compute_docvector(self, row):
        content = row["Fjob_detail"]
        try:
            content_keyword_dict = self.content_proc_handler.gen_words(content)
        except:
            raise Exception("Too few tag found in this document")

        # 标签按照TFIDF值从高到低排序
        analysis = [tag_detail[0] for tag_detail in sorted(content_keyword_dict.items(), key=lambda tup: tup[1], reverse=True)]
        selected_topic, doc_vector_str = self.classifier.classify(content_keyword_dict)

        # 结果打包
        self.firelinker["Fcluster_id"] = selected_topic
        self.firelinker["Ftag_detail"] = ','.join(analysis)  # json.dumps(analysis)
        self.firelinker["Farticle_vector"] = doc_vector_str

    # 更新或者插入t_job_document表
    def __insert_article(self, item):
        this_season = gen_season_num()
        doc_table = "t_" + "job_documents_" + str(this_season)
        self._db.set_db_table("db_documents", doc_table)
        datai = {
            "Fjob_name":        item["Fjob_name"],
            "Fsalary":          item["Fsalary"],
            "Fjob_url":         item["Fjob_url"],
            "Freq_year":        item["Freq_year"],
            "Freq_edu":         item["Freq_edu"],
            "Flocation":        item["Flocation"],
            "Fjob_detail":      item["Fjob_detail"],
            "Fgang_name":       item["Fgang_name"],
            "Fgang_detail":     item["Fgang_detail"],
            "Fcluster_id":      self.firelinker["Fcluster_id"],
            "Ftag_detail":      self.firelinker["Ftag_detail"],
            "Farticle_vector":  self.firelinker["Farticle_vector"],
            "Flstate":          1,
            "Fpub_time":        time_now(),
            "Fcreate_time":     time_now(),
            "Fmodify_time":     time_now()
        }
        self._db.insert(datai)
        self._db.commit()

    def __gen_new_tasks(self):
        this_season = gen_season_num()

        doc_table = "t_" + "job_documents_" + str(this_season)
        detail_table = "t_" + "zhilian_detail_" + str(this_season)

        self._db.set_db_table("db_documents", doc_table)
        field_list = ["Fjob_url"]
        where = "1"
        old_urls = self._db.query(field_list, where)
        old_urls = set([url_info["Fjob_url"] for url_info in old_urls])

        self._db.set_db_table("db_crawlers", detail_table)
        field_list = ["Fjob_url"]
        where = "1"
        cur_urls = self._db.query(field_list, where)
        cur_urls = set([url_info["Fjob_url"] for url_info in cur_urls])

        new_urls = cur_urls.difference(old_urls)
        return list(new_urls)
        
    def process_doc(self, item):
        try:
            self.__compute_docvector(item)  # 依赖于__gen_words
            self.__insert_article(item)
        except Exception as e:
            print("An error has ocurred %s" % str(e))
    
    def run(self):
        new_urls = self.__gen_new_tasks()
        field_list = ["*"]
        this_season = gen_season_num()
        detail_table = "t_" + "zhilian_detail_" + str(this_season)

        for sub_urls in list2chunks(new_urls, 1000):
            in_condition = get_sql_in_condition_string(sub_urls)
            where = "Fjob_url in %s" % in_condition
            self._db.set_db_table('db_crawlers', detail_table)
            items = self._db.query(field_list, where)
            self._db.commit()
            for item in items:
                self.process_doc(item)


# 单次测试用
if __name__ == '__main__':
    tool = CJobPreproc()
    tool.run()