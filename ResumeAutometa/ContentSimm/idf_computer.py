#   AUTHOR: Sibyl System
#     DATE: 2018-04-24
#     DESC: 关键词IDF值全量更新

'''
关键词IDF值全量更新
流水批量读取预处理成功的文档
提取文本信息，计数每个词所属文档数
'''

# import ssl
# import requests
# import urllib.request
# from urllib.request import Request

import numpy as np
from ResumeAutometa.Foundations.utils import *
from ResumeAutometa.Config.file_paths import LDA_TRAINING_DATA_PATH

SENTENCE_CACHE_SIZE = 1        # 每一份文档大约1MB左右，视内存大小而定
DB_UPDATE_BATCH_SIZE = 10000   # 单次更新DB的行数，视内存大小而定


class IdfComputer(object):

    def __init__(self, train_file, idf_file, wordid_file, idword_file):
        
        # 后续根据任务的进行会发生改变的变量
        self.train_file = LDA_TRAINING_DATA_PATH + train_file
        self.idf_file = LDA_TRAINING_DATA_PATH + idf_file
        self.wordid_file = LDA_TRAINING_DATA_PATH + wordid_file
        self.idword_file = LDA_TRAINING_DATA_PATH + idword_file
        self.Doc_count = 0
        self.word_count = 0
        self.id2word = {}
        self.word2idf = {}
        self.word2id = {}
        self.word2count = {}
        
    def __gen_words(self, line):
        line = line.strip()
        self.Doc_count += 1
        words = [word for word in line.split() if word.strip()]
                
        for word in set(words):
            map_reduce(self.word2count, word)
        
    def load_base_info(self):
        for word in self.word2count.keys():
            self.id2word[self.word_count] = word
            self.word2id[word] = self.word_count
            self.word_count += 1
                
    def compute_idf(self):
        arr_idf_wordidx = np.zeros(self.word_count, dtype='int32')
        arr_Doc_num = np.zeros(self.word_count, dtype='float64')
        arr_word_count = np.zeros(self.word_count, dtype='float64')
        # arr_idf = np.zeros(self.word_count, dtype='float64')
        
        # 填装IDF列表容器
        Doc_num = self.Doc_count
        loop_count = 0
        for word, word_count in self.word2count.items():
            word_idx = self.word2id[word]
            arr_idf_wordidx[loop_count] = word_idx
            arr_Doc_num[loop_count] = Doc_num
            arr_word_count[loop_count] = word_count
            loop_count += 1
            
        # NUMPY高速运算
        arr_idf = np.log(arr_Doc_num/arr_word_count)
        
        # 计算结果打包
        for loop_count in range(len(arr_idf)):
            idf = arr_idf[loop_count]
            word_idx = arr_idf_wordidx[loop_count]
            word = self.id2word[word_idx]
            self.word2idf[word] = idf
        
    def process_doc(self, line):
        try:
            self.__gen_words(line)
        except Exception as e:
            print(e)
    
    def wind_up(self):
        self.load_base_info()
        self.compute_idf()
        write_data2json(self.word2idf, self.idf_file)
        write_data2json(self.word2id, self.wordid_file)
        write_data2json(self.id2word, self.idword_file)
        
    def main(self):
        cache = read_lines(self.train_file)
        for line in cache:
            self.process_doc(line)
        self.wind_up()


# 单次测试用
if __name__ == '__main__':
    tool_testing = IdfComputer("lda_testing.txt", "lda_testing_wordidf.txt", 
                               "lda_testing_wordid.txt", "lda_testing_idword.txt")
    tool_testing.main()
    # tool_training = IdfComputer("lda_training.txt", "lda_training_wordidf.txt",
    #                            "lda_training_wordid.txt", "lda_training_idword.txt")
    # tool_training.main()