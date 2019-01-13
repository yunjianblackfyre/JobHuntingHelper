#   AUTHOR: Sibyl System
#     DATE: 2019-01-08
#     DESC: 类信息增益过滤器

import numpy as np
from ResumeAutometa.Foundations.utils import *
from ResumeAutometa.Config.file_paths import IFGAIN_FILTER_EXTRACT_RESOURCES

SENTENCE_CACHE_SIZE = 1        # 每一份文档大约1MB左右，视内存大小而定
DB_UPDATE_BATCH_SIZE = 10000   # 单次更新DB的行数，视内存大小而定
TOL = 0.000000001
DENSITY_THRESH = 0.01
ENTROPY_THRESH = 2.5
np.set_printoptions(edgeitems=7, linewidth=200)


class IfGainComputer(object):

    def __init__(self, train_file, ifgain_file, catid_file, 
                 idcat_file, wordid_file, idword_file, allowed_file):
        
        # 后续根据任务的进行会发生改变的变量
        self.train_file = IFGAIN_FILTER_EXTRACT_RESOURCES + train_file
        self.ifgain_file = IFGAIN_FILTER_EXTRACT_RESOURCES + ifgain_file
        self.catid_file = IFGAIN_FILTER_EXTRACT_RESOURCES + catid_file
        self.idcat_file = IFGAIN_FILTER_EXTRACT_RESOURCES + idcat_file
        self.wordid_file = IFGAIN_FILTER_EXTRACT_RESOURCES + wordid_file
        self.idword_file = IFGAIN_FILTER_EXTRACT_RESOURCES + idword_file
        self.allowed_file = IFGAIN_FILTER_EXTRACT_RESOURCES + allowed_file
        self.Doc_count = 0
        self.word_count = 0
        self.cat_count = 0
        self.id2cat = dict()
        self.cat2id = dict()
        self.cat2count = dict()
        self.matrix_cat_plus_word_prob = None
        
        self.id2word = dict()
        self.word2ifgain = dict()
        self.allowed = []
        self.word2id = dict()
        self.word2count = dict()
        
    def __gen_words(self, line):
        line = line.strip()
        line = line.split("########")
        if line:
            cat = line[0]
            content = line[1]
            words = set([word for word in content.split() if word.strip()])
            self.Doc_count += 1
            map_reduce(self.cat2count, cat)
            for word in words:
                map_reduce(self.word2count, word)
                
    def __gen_matrix(self, line):
        line = line.strip()
        line = line.split("########")
        if line:
            cat = line[0]
            content = line[1]
            words = set([word for word in content.split() if word.strip()])
            for word in words:
                w_idx = self.word2id[word]
                c_idx = self.cat2id[cat]
                self.matrix_cat_plus_word_prob[c_idx][w_idx]+=1
        
    def load_base_info(self):
        for cat in self.cat2count.keys():
            self.id2cat[self.cat_count] = cat
            self.cat2id[cat] = self.cat_count
            self.cat_count += 1
        for word in self.word2count.keys():
            self.id2word[self.word_count] = word
            self.word2id[word] = self.word_count
            self.word_count += 1
        self.matrix_cat_plus_word_prob = np.zeros((self.cat_count, self.word_count), dtype="float64")
        print("word_count: ", self.word_count)
        print("cat_count: ", self.cat_count)
        
    @classmethod
    def right_side_entropy(cls, matrix_cat_cond_word_prob, arr_word_prob):
        matrix_tmp = -np.log(np.clip(matrix_cat_cond_word_prob + TOL, 0.0, 1.0))*matrix_cat_cond_word_prob
        arr_tmp = matrix_tmp.sum(axis=0)
        return arr_tmp
        
    def compute_ifgain(self):
        arr_word_prob = np.zeros(self.word_count, dtype="float64")
        arr_cat_prob = np.zeros(self.cat_count, dtype="float64")
        
        for idx in range(self.word_count):
            word = self.id2word[idx]
            count = self.word2count[word]
            arr_word_prob[idx] = count
            
        arr_word_prob = arr_word_prob/self.Doc_count
        
        for idx in range(self.cat_count):
            cat = self.id2cat[idx]
            count = self.cat2count[cat]
            arr_cat_prob[idx] = count
        arr_cat_prob = arr_cat_prob/self.Doc_count
        arr_cat_prob_expand = np.reshape(np.repeat(arr_cat_prob, self.word_count),[self.cat_count, self.word_count])
        
        self.matrix_cat_plus_word_prob = self.matrix_cat_plus_word_prob/self.Doc_count
        
        matrix_cat_cond_word_prob = self.matrix_cat_plus_word_prob/arr_word_prob
        matrix_word_cond_cat_prob = self.matrix_cat_plus_word_prob/arr_cat_prob_expand
        arr_word_cond_cat_max_prob = matrix_word_cond_cat_prob.max(axis=0)

        print("Pcat: \n", arr_cat_prob)
        print("-"*32)
        print("Pword: \n", arr_word_prob)
        print("-"*32)
        print("Pcat_expand: \n", arr_cat_prob_expand)
        print("-"*32)
        print("P(cat, word): \n", self.matrix_cat_plus_word_prob)
        print("-"*32)
        print("P(word/cat): \n", matrix_word_cond_cat_prob)
        print("-"*32)
        print("P(word/max_cat): \n", arr_word_cond_cat_max_prob)
        print("-"*32)
        print("P(cat/word): \n", matrix_cat_cond_word_prob)
        print("-"*32)
        
        arr_ifgain = self.right_side_entropy(matrix_cat_cond_word_prob, arr_word_prob)
        
        for idx in range(self.word_count):
            if arr_word_cond_cat_max_prob[idx] > DENSITY_THRESH:
                word = self.id2word[idx]
                ifgain_value = arr_ifgain[idx]
                if ifgain_value < ENTROPY_THRESH or re.match(".*[A-Za-z]+.*", word):
                    self.word2ifgain[word] = ifgain_value
                    self.allowed.append(word)
        
    def process_doc(self, line):
        try:
            self.__gen_words(line)
        except Exception as e:
            print(e)
            
    def process_doc_again(self, line):
        try:
            self.__gen_matrix(line)
        except Exception as e:
            print(e)
    
    def wind_up(self):
        self.compute_ifgain()
        write_data2json(self.allowed, self.allowed_file)
        write_data2json(self.word2ifgain, self.ifgain_file)
        write_data2json(self.cat2id, self.catid_file)
        write_data2json(self.id2cat, self.idcat_file)
        write_data2json(self.word2id, self.wordid_file)
        write_data2json(self.id2word, self.idword_file)
        
    def main(self):
        cache = read_lines(self.train_file)
        for line in cache:
            self.process_doc(line)
        self.load_base_info()
        for line in cache:
            self.process_doc_again(line)
        self.wind_up()


# 单次测试用
if __name__ == '__main__':
    tool_training = IfGainComputer("ifgain_filter_data_training.txt", "ifgain_filter_wordifgain.txt",
                                   "ifgain_filter_catid.txt", "ifgain_filter_idcat.txt",
                                   "ifgain_filter_wordid.txt", "ifgain_filter_idword.txt", "allowed_words.txt")
    tool_training.main()
