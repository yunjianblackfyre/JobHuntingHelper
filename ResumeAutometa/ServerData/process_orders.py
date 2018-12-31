# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-08-13
import redis
from ResumeAutometa.Foundations.utils import *
from ResumeAutometa.ServerData.server_db_handle import CServerDbHandle
from ResumeAutometa.Computation.preprocessor import CContentClassifier
from ResumeAutometa.Computation.preprocessor import ProdContentPreproc
from ResumeAutometa.Computation.preprocessor import string2vector
from ResumeAutometa.Foundations.my_threadpool import Pool
from ResumeAutometa.Computation.simm import simm
from ResumeAutometa.Config.interfaces import REDIS_DB_NAME_CFG

THREAD_POOL_SIZE = 10


class CProcessOrders(object):
    def __init__(self):
        mission_db = REDIS_DB_NAME_CFG["job_upload_cache"]
        vector_db = REDIS_DB_NAME_CFG["file_vector_cache"]
        self.redis_conn = redis.Redis(host="localhost", port=6379, decode_responses=True, db=mission_db)
        self.redis_mission_pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True, db=mission_db)
        self.redis_vector_pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True, db=vector_db)

        self.content_classifiers = [CContentClassifier() for i in range(THREAD_POOL_SIZE)]
        self.content_preprocs = [ProdContentPreproc() for i in range(THREAD_POOL_SIZE)]
        self._db = CServerDbHandle()

    @staticmethod
    def gen_candidates(mission_id, redis_mission_pool, redis_vector_pool, result_container,
                      content_preproc, content_classifier):
        # Initialize redis connections
        redis_mission_conn = redis.Redis(connection_pool=redis_mission_pool)
        redis_vector_conn = redis.Redis(connection_pool=redis_vector_pool)
        mission_str = redis_mission_conn.get(mission_id)

        # Initialize key variables
        mission_dict = json.loads(mission_str)
        content = mission_dict["detail"]
        content_id = mission_id
        current_season = get_current_season()

        # Classify documents
        content_keyword_dict = content_preproc.gen_words(content)
        tag_detail = ','.join([tag_detail[0] for tag_detail in
                               sorted(content_keyword_dict.items(), key=lambda tup: tup[1], reverse=True)])
        selected_topic, doc_vector_str = content_classifier.classify(content_keyword_dict)
        content_topic = selected_topic

        # Generate candidates
        doc_list = json.loads(redis_vector_conn.get(str(content_topic)))
        mission_vector = string2vector(doc_vector_str)
        simm_list = []
        for item in doc_list:
            compare_doc_vector = string2vector(item[1])
            score = simm(mission_vector, compare_doc_vector)
            doc_id = item[0]
            simm_list.append((doc_id, score))
        simm_list = sorted(simm_list, key=lambda tup: tup[-1], reverse=True)
        simm_list = [str(item[0]) for item in simm_list]

        # Load result
        result_container[content_id] = {
            "job_related": ','.join(simm_list[0:90]),
            "job_tag_detail": tag_detail,
            "job_summary": content,
            "job_topic": content_topic,
            "job_vector": doc_vector_str,
            "season_id": current_season
        }

    def write_db_batch(self, result_container):
        field_list = ["Fauto_id", "Fjob_related", "Ftag_detail", "Fjob_summary", "Fcluster_id", "Farticle_vector",
                      "Fseason_related"]
        result_list = []
        for key, value in result_container.items():
            tuple_tmp = (key,
                         value["job_related"],
                         value["job_tag_detail"],
                         value["job_summary"],
                         value["job_topic"],
                         value["job_vector"],
                         value["season_id"]
                         )
            result_list.append(str(tuple_tmp))
        self._db.set_db_table("db_documents", "t_job_documents_compare")
        self._db.update_batch(field_list, result_list)
        self._db.commit()

    def get_missions(self):
        mission_id_list = self.redis_conn.keys()
        result_container = dict()

        thread_pool = Pool(size=THREAD_POOL_SIZE)
        thread_pool.add_tasks([(self.gen_candidates, (mission_id_list[i], self.redis_mission_pool,
                                self.redis_vector_pool, result_container,
                                self.content_preprocs[i % THREAD_POOL_SIZE],
                                self.content_classifiers[i % THREAD_POOL_SIZE])) for i in range(len(mission_id_list))])
        thread_pool.run()
        print_dict(result_container)
        self.write_db_batch(result_container)


def test():
    redis_conn = redis.Redis(host="localhost", port=6379, decode_responses=True, db=0)
    redis_conn.flushdb()
    order_test = read_file_json("E:\PycharmProject\ResumeAutometa\Resources\order_test.txt")
    count = 0
    for item in order_test:
        redis_conn.set(str(count), json.dumps(item))
        count += 1


# 单次测试用
if __name__ == '__main__':
    # test()
    handler = CProcessOrders()
    handler.get_missions()