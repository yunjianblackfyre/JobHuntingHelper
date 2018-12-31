# -*- coding:utf-8 -*-
import sys

try:
    import jieba
    import jieba.posseg as pseg
except Exception as e:
    print("初始化失败，错误%s, 请检查文件格式是否损坏!" % str(e))
    sys.exit(-1)

import numpy as np
from numpy import linalg as LA
from gensim.test.utils import datapath
from gensim.models.ldamodel import LdaModel
from ResumeAutometa.Foundations.utils import *
# from ResumeAutometa.Config.file_paths import FILTERED_NEW_WORDS
from ResumeAutometa.Config.file_paths import NEW_WORDS_FOR_JIEBA
from ResumeAutometa.Config.file_paths import WORD_TO_IDF, LDA_MODEL_PATH, WORD_TO_ID_PATH
from ResumeAutometa.PyData.zhilian_allowed_words import ZHILIAN_ALLOWED_WORDS
from ResumeAutometa.PyData.stop_words import STOP_PATTERNS, STOP_WORDS, REPLACE_PATTERN

mark_tag_set = {'n', 'nz', 'vn', 'eng'}
TAG_NUM_THRESH = 4
PUNCTUATION_REGEX_PATTERN = "[。？！，、；：“”’‘（）［］〔〕【】——……·《》〈〉.?!,;:\"\'\(\)\[\]\{\}]+"  # 新词发现需要替换的符号

vector2string = lambda doc_vector: json.dumps([str(num) for num in list(doc_vector)])
string2vector = lambda doc_vector_str: np.array([float(num) for num in json.loads(doc_vector_str)])


def renew_jieba():
    """
    with open(FILTERED_NEW_WORDS, 'r') as f:
        filtered_new_words_dict = json.loads(f.read())

    # 将文件写成jieba可读的形式
    # 例如 机器学习 nv 612
    # 标注 词  词性（这里n是名词，v是动词） 词频
    with open(NEW_WORDS_FOR_JIEBA, 'wb') as f:
        for key, value in filtered_new_words_dict.items():
            line = '%s %s vn\n' % (key, str(value))  # 按照ICTPOS标记法，将所有新词标记为动名词
            f.write(line.encode())

    """
    # 更新结巴分词器
    jieba.load_userdict(NEW_WORDS_FOR_JIEBA)


def filter_words(sentence, freq_thresh=3, len_thresh=8):
    word_freq = {}
    fine_sentence = []
    # 获取词频
    for word in sentence:
        map_reduce(word_freq, word)
    # 根据词频过滤词
    for word in sentence:
        if word_freq[word] > freq_thresh and len(word) < len_thresh:
            fine_sentence.append(word)
    return fine_sentence


# 用于原始环境的内容预处理
class ContentPreproc(object):

    def __init__(self):
        renew_jieba()

    def extract_keyword(self, keyword_list, line):
        line = line.strip()
        if line:
            words_info = list(pseg.cut(line))
            for word, flag in words_info:
                if flag in mark_tag_set and len(word) > 1:  # 一个字的不要
                    keyword_list.append(word)

    def gen_words(self, content):
        content_keyword_list = []

        eng_words = re.findall('[a-zA-Z]{2,}', content)
        none_eng_words = re.findall('[\u4e00-\u9fff]', content)
        eng_ratio = len(eng_words) / (len(none_eng_words) + 0.001)
        if eng_ratio >= 0.5:
            raise Exception

        content = re.sub("\s+", " ", content)
        self.extract_keyword(content_keyword_list, content)

        return content_keyword_list


# 用于新词发现的内容预处理
class NewWordContentPreproc(object):

    @staticmethod
    def content_preprocess(content):

        # 过滤标点符号
        content = re.sub(PUNCTUATION_REGEX_PATTERN, ' ', content)

        # 文章的英文含量超标，则跳过
        eng_words = re.findall('[a-zA-Z]{2,}', content)
        none_eng_words = re.findall('[\u4e00-\u9fff]', content)
        eng_ratio = len(eng_words) / (len(none_eng_words) + 0.001)
        if eng_ratio >= 0.25:
            return ''

        # 正则过滤停用词
        for pattern in STOP_PATTERNS:
            content = re.sub(pattern, ' ', content)

        # 替换停用词（例如 智能->智慧）
        for replace_target, replace_pattern in REPLACE_PATTERN.items():
            content = content.replace(replace_target, replace_pattern)

        # 去除停用词
        for word in STOP_WORDS:
            content = content.replace(word, ' ')

        # 将所有的空白符或者连续空白符统一转成space
        content = re.sub("\s+", ' ', content)

        # 边角消除
        content = content.strip()

        return content
        
        
# 用于LDA训练的内容预处理 
class LdaTrainContentPreproc(ContentPreproc):

    def __init__(self):
        super(LdaTrainContentPreproc, self).__init__()
        self.allowed_words = ZHILIAN_ALLOWED_WORDS

    def gen_words(self, content):
        content_keyword_list = super(LdaTrainContentPreproc, self).gen_words(content)

        # 过滤词
        refined_content_keyword_list = []
        for word in content_keyword_list:
            word = word.upper()
            if word in self.allowed_words:
                refined_content_keyword_list.append(word)
        return refined_content_keyword_list
        

# 用于生产环节的内容预处理 
class ProdContentPreproc(ContentPreproc):

    def __init__(self):
        super(ProdContentPreproc, self).__init__()

        self.word2idf = read_file_json(WORD_TO_IDF)
        # self.word2vector = read_file_json(WORD_TO_VECTOR)

    def gen_words(self, content):
        content_keyword_dict = {}
        content_keyword_list = super(ProdContentPreproc, self).gen_words(content)

        # 过滤词
        content_keyword_list = filter_words(content_keyword_list, freq_thresh=0, len_thresh=15)
        content_filtered_keyword_list = []

        for word in content_keyword_list:
            word = word.upper()
            if word in self.word2idf.keys():
                content_filtered_keyword_list.append(word)

        content_filtered_keyword_len = len(content_filtered_keyword_list)

        if content_filtered_keyword_len <= TAG_NUM_THRESH:
            raise Exception

        # 计算TFIDF值
        for word in content_filtered_keyword_list:
            map_reduce(content_keyword_dict, word, float(1/content_filtered_keyword_len)*self.word2idf[word])

        return content_keyword_dict


class CContentClassifier(object):
    topic_vectors = [
        np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    ]

    def __init__(self):
        # 装载主题向量
        self.topic_vectors = self.topic_vectors

        # 装载LDA模型
        fname = datapath(LDA_MODEL_PATH)
        self.lda_model = LdaModel.load(fname)
        self.lda_word2id = read_file_json(WORD_TO_ID_PATH)

    def classify(self, content_keyword_dict):
        # 初始化变量
        doc = []
        for word, weight in content_keyword_dict.items():
            doc.append((self.lda_word2id[word], weight))

        # 计算文章向量
        doc_vector = np.zeros(20, dtype="float32")
        for item in self.lda_model.get_document_topics(doc, minimum_probability=0.000):
            idx = item[0]
            doc_vector[idx] = item[1]

        # 归类主题
        max_simm = -1
        selected_topic = 0
        for idx in range(len(self.topic_vectors)):
            dot_product = np.dot(doc_vector, self.topic_vectors[idx])
            norm_product = LA.norm(doc_vector) * LA.norm(self.topic_vectors[idx])
            simm = (dot_product / norm_product)
            if simm > max_simm:
                max_simm = simm
                selected_topic = idx

        # 结果打包
        return selected_topic, json.dumps([str(num) for num in list(doc_vector)])   # np.array to string


if __name__ == '__main__':
    test_dict = {
        "机器学习": 2,
        "深度学习": 3
    }
    test_text = "熟悉机器学习，热爱数据挖掘"

    clsf_handler = CContentClassifier()
    prc_handler = ProdContentPreproc()
    print(clsf_handler.classify(test_dict))
    print(prc_handler.gen_words(test_text))
