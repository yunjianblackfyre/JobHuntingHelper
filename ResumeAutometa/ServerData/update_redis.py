# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-08-12
#     DESC：批量更新排序库存

import redis
import json
from ResumeAutometa.ServerData.server_db_handle import CServerDbHandle
from ResumeAutometa.ServerData.job_preproc import gen_season_num
from ResumeAutometa.Config.interfaces import REDIS_DB_NAME_CFG

TOPIC_NUM = 10


class CLoadDocVector(object):
    def __init__(self):
        redis_db = REDIS_DB_NAME_CFG["file_vector_cache"]
        self.redis_conn = redis.Redis(host="localhost", port=6379, decode_responses=True, db=redis_db)
        self._db = CServerDbHandle()

    def load2redis(self):
        this_season = gen_season_num()
        doc_table = "t_" + "job_documents_" + str(this_season)
        field_list = ["Fauto_id", "Farticle_vector"]
        self.redis_conn.flushdb()
        for idx in range(TOPIC_NUM):
            where = "Fcluster_id='%s'" % idx
            self._db.set_db_table("db_documents", doc_table)
            DB_res = self._db.query(field_list, where)
            vectors = [(item["Fauto_id"], item["Farticle_vector"]) for item in DB_res]
            self.redis_conn.set(str(idx), json.dumps(vectors))


# 单次测试用
if __name__ == '__main__':
    tool = CLoadDocVector()
    tool.load2redis()