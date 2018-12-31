#   AUTHOR: Sibyl System
#     DATE: 2018-04-25
#     DESC: 

'''
构造word2vector模块所需的训练数据和测试数据集
训练数据构建方法大致描述：
将文本用结巴分词成词序列，并且过滤之，如下：
文档1:C++ 教学 模块 训练 指针
文档2:python3 AI 大数据 人工智能
文档3:区块链 去中心化
......
将这些序列换行保存在两个.txt文件中，分别为测试和训练
预计该文件的计量单位为G级别
'''

import traceback
import time
from ResumeAutometa.Foundations.utils import *
from ResumeAutometa.Foundations.batch_proc import BatchProc
from multiprocessing import Pool
from ResumeAutometa.ServerData.server_db_handle import CServerDbHandle
from ResumeAutometa.Computation.preprocessor import LdaTrainContentPreproc
from ResumeAutometa.Config.file_paths import LDA_TRAINING_DATA_PATH

TRAINING_DATA_RATIO = 0.98    # 训练数据占比
TRAINING_SAMPLE_TOLERANCE = 50000  # 最小训练样本数 
TASK_NUM_TOLERANCE = 5  # 最大进程数

DB_NAME = "db_crawlers"
DB_TABLE_NAME = "t_zhilian_detail_3"


class IdListGenerator(object):
    
    def __init__(self):
        self._db = CServerDbHandle()
        
    def get_training_id(self):
        field_list = ["Fauto_id"]
        self._db.set_db_table(DB_NAME, DB_TABLE_NAME)
        where = "Fcreate_time>'2018-11-01 01:01:01'"
        DB_res_zhilian = self._db.query(field_list, where)
        self._db.commit()

        id_list = [item["Fauto_id"] for item in DB_res_zhilian]
        write_data2json(id_list, LDA_TRAINING_DATA_PATH + "id_list.txt")


class TrainDataBuilder(BatchProc):

    def __init__(self, batch_size, proc_id, chunck_file):
        super(TrainDataBuilder, self).__init__("train_data_builder")
        self.batch_size = batch_size
        self.proc_id = proc_id
        self.current_chunck_idx = 0
        self.chunck_file = chunck_file
        self.training_data = []
        self.testing_data = []
        self.content_preproc_handler = LdaTrainContentPreproc()
        
    def __load_content(self, idx, items, sample_indexes):
        item = items[idx]
        content = item["Fjob_detail"]
        key_word_list = self.content_preproc_handler.gen_words(content)
        if key_word_list:
            if idx in sample_indexes:
                self.training_data.extend(key_word_list)
                self.training_data.append('\n')
            else:
                self.testing_data.extend(key_word_list)
                self.testing_data.append('\n')
                
    def save2file(self):
        file_name = "_".join(["lda_training", DB_NAME, DB_TABLE_NAME, str(self.proc_id), str(self.current_chunck_idx)])
        file_name = LDA_TRAINING_DATA_PATH + file_name + ".txt"
        with open(file_name, 'w') as file_handler:
            sentence_cache = " ".join(self.training_data)
            file_handler.writelines(sentence_cache)
            file_handler.close()
        self.training_data = []
        
        file_name = "_".join(["lda_testing", DB_NAME, DB_TABLE_NAME, str(self.proc_id), str(self.current_chunck_idx)])
        file_name = LDA_TRAINING_DATA_PATH + file_name + ".txt"
        with open(file_name, 'w') as file_handler:
            sentence_cache = " ".join(self.testing_data)
            file_handler.writelines(sentence_cache)
            file_handler.close()
        self.testing_data = []
    
    # 将每批处理结果讯息打印日志
    def gen_batch_report(self):
        UPlay = self.abyss["UPlay"]
        UPoison = self.abyss["UPoison"]
        URdead = self.abyss["URdead"]
        Usurvive = self.abyss["Usurvive"]
        
        if UPlay != 0:
            self.log_handler.log.info("You played %s times, survive %s times, \
            poisoned %s times, died %s times.\n \
                survival rate: %s, poison rate: %s, death rate: %s."
                                 % (UPlay, Usurvive, UPoison, URdead, Usurvive/UPlay, UPoison/UPlay, URdead/UPlay))
        else:
            self.log_handler.log.info("You processed zero content, please check your Sql")
        
    def process_doc(self, idx, items, sample_indexes):
        try:
            self.__load_content(idx, items, sample_indexes)
        except:
            item = items[idx]
            self._you_are_dead(item)
        finally:
            self._extract_soul()
        
    def process_batch_cluster(self, items):
        upper_bound = len(items)
        lower_bound = 0
        sample_num = int(upper_bound*TRAINING_DATA_RATIO)
        sample_indexes = sample_rand(lower_bound, upper_bound, sample_num)
        sample_indexes = set(sample_indexes)
        
        for idx in range(len(items)):
            self.process_doc(idx, items, sample_indexes)
        
    def process_batch(self, items):
        batch_cluster_dict = dict()
        for item in items:
            job_category = item["Fjob_cat"]
            map_reduce_list(batch_cluster_dict, job_category, item)

        for key, value in batch_cluster_dict.items():
            self.process_batch_cluster(value)
            
        try:
            self.gen_batch_report()
            self.save2file()
        except:
            self.log_handler.log.info(traceback.format_exc())
        finally:
            self._bonfire()
            
    def run(self):
        id_list = read_file_json(LDA_TRAINING_DATA_PATH + self.chunck_file)
        
        for chunck in list2chunks(id_list, self.batch_size):
            
            id_list_condition = get_sql_in_condition_string(chunck)
            
            where = "Fauto_id in %s" % id_list_condition
            # print("proc %s process id list: %s" % (self.proc_id, id_list_condition))
            
            field_list = ["Fjob_cat", "Fjob_detail"]
            self._db.set_db_table(DB_NAME, DB_TABLE_NAME)
            items = self._db.query(field_list, where)
            self._db.commit()
            
            self.process_batch(items)
            self.current_chunck_idx += 1
            # break      # 调试用，记删
            time.sleep(2)
            
            
def final_step():
    intergrate_files("lda_testing", LDA_TRAINING_DATA_PATH)
    intergrate_files("lda_training", LDA_TRAINING_DATA_PATH)


def run_task(batch_size, proc_id, chunck_file):
    tool = TrainDataBuilder(batch_size, proc_id, chunck_file)
    tool.main()
    
    
def distribute_task(batch_size, task_num=2):
    id_list = read_file_json(LDA_TRAINING_DATA_PATH + "id_list.txt")
    id_list.sort()
    
    # 训练样本少于10W，或者进程数大于5就给我滚
    if len(id_list) < TRAINING_SAMPLE_TOLERANCE or task_num > TASK_NUM_TOLERANCE:
        print("Are you fucking kiding me?")
        return
        
    proc_chunck_size = len(id_list)//task_num
    proc_chuncks = []
    for chunck in list2chunks(id_list, proc_chunck_size):
        proc_chuncks.append(chunck)
    
    chunck_file_list = []
    for idx in range(len(proc_chuncks)):
        chunck_file = "id_list_task_%s.txt" % idx
        chunck_file_list.append(chunck_file)
        write_data2json(proc_chuncks[idx], LDA_TRAINING_DATA_PATH + chunck_file)
        time.sleep(1)
        
    p = Pool()           #开辟进程池
    for idx in range(len(chunck_file_list)):
        chunck_file = chunck_file_list[idx]
        p.apply_async(run_task, args=(batch_size, idx, chunck_file))
        
    p.close() #关闭进程池
    p.join()
    time.sleep(2)
    
    
def main():
    try:
        global DB_NAME
        global DB_TABLE_NAME
        DB_NAME = "db_crawlers"
        DB_TABLE_NAME = "t_51job_detail_3"
        generator = IdListGenerator()
        generator.get_training_id()
        
        distribute_task(10000, task_num=2)
        
        DB_NAME = "db_crawlers"
        DB_TABLE_NAME = "t_zhilian_detail_3"
        generator.get_training_id()
        distribute_task(10000, task_num=2)
        
        final_step()
    except:
        print(traceback.format_exc())

    
# 单次测试用
if __name__ == '__main__':
    main()
