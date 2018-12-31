#   AUTHOR: Sibyl System
#     DATE: 2018-03-03
#     DESC: word2vector encapsulation

'''
详细说明：
训练词向量
'''

# import re
# import math
# import json
# import sys
# import os
# from gensim.test.utils import common_dictionary, common_corpus
from gensim.test.utils import datapath
from gensim.models.ldamodel import LdaModel
from ResumeAutometa.Config.file_paths import LDA_TRAINING_DATA_PATH
from ResumeAutometa.Foundations.utils import *


class MyLda(object):

    def __init__(self, train_file, idf_file, wordid_file, idword_file, model_file):
        self.train_data = read_lines(LDA_TRAINING_DATA_PATH + train_file)
        self.word2idf = read_file_json(LDA_TRAINING_DATA_PATH + idf_file)
        self.word2id = read_file_json(LDA_TRAINING_DATA_PATH + wordid_file)
        self.id2word = read_file_json(LDA_TRAINING_DATA_PATH + idword_file)
        self.model_file = LDA_TRAINING_DATA_PATH + model_file
        self.corpus = []

    def preprocess_json(self):
        tmp_dict = dict()
        for key, value in self.id2word.items():
            tmp_dict[int(key)] = value
        self.id2word = tmp_dict
            
    def __build_corpus_row(self, words):
        row_dict = dict()
        word_count = len(words)
        res_list = []
        for word in words:
            map_reduce(row_dict, word)

        for word, freq in row_dict.items():
            try:
                idf = self.word2idf[word]
                word_id = self.word2id[word]
                tf = freq/word_count
                tfidf = tf*idf
                res_list.append((word_id, tfidf))
            except Exception as e:
                pass
        return res_list

    def __build_base_info(self):
        for line in self.train_data:
            words = [word for word in line.split() if word.strip()]# do something
            if words:
                corpus_row = self.__build_corpus_row(words)
                self.corpus.append(corpus_row)
        
    def run_lda(self):
        model = LdaModel(self.corpus, id2word=self.id2word, chunksize=5000, num_topics=20)
        temp_file = datapath(self.model_file)
        model.save(temp_file)
    
    # 主过程
    def process(self):
        print('lda start training...')
        self.preprocess_json()
        self.__build_base_info()
        self.run_lda()
        

if __name__ == '__main__':
    lda_trainer = MyLda("lda_testing.txt", "lda_testing_wordidf.txt",
                        "lda_testing_wordid.txt", "lda_testing_idword.txt", "lda_testing_model")
    lda_trainer.process()
    
    
    
