#   AUTHOR: Sibyl System
#     DATE: 2018-01-01
#     DESC: 所有文件路径

# ################ windows环境文件路径【小助手测试】 ################

DEBUG = True

CHROME_WEBDRIVER_PATH_FILE = "E:/PycharmProject/ResumeAutometa/UserInterface/files/chrome_path.txt"

LDA_MODEL_PATH = "E:/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/lda_training_model"

WORD_TO_ID_PATH = "E:/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/lda_training_wordid.txt"

WORD_TO_IDF = "E:/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/lda_training_wordidf.txt"

FILTERED_NEW_WORDS = "E:/PycharmProject/ResumeAutometa/Resources/JieBa/filtered_new_words.txt"

NEW_WORDS_FOR_JIEBA = "E:/PycharmProject/ResumeAutometa/Resources/JieBa/new_words4jieba.txt"

JIEBA_BASE_DICT = "E:/PycharmProject/jieba/dict.txt"

CRAWL_JOB_TOTEM = "E:/PycharmProject/ResumeAutometa/UserInterface/icons/crawl_job.png"

THROW_RESUME_TOTEM = "E:/PycharmProject/ResumeAutometa/UserInterface/icons/throw_resume.png"

MAIN_TOTEM = "E:/PycharmProject/ResumeAutometa/UserInterface/icons/Chrome.png"

WEB_DRIVER_ACTION_SETTINGS = "E:/PycharmProject/ResumeAutometa/UserInterface/files/settings.txt"

RESUME_HISTORY = "E:/PycharmProject/ResumeAutometa/UserInterface/files/throw_history.txt"

PROB_START_P = "prob_start.p"

PROB_TRANS_P = "prob_trans.p"

PROB_EMIT_P = "prob_emit.p"

CHAR_STATE_TAB_P = "char_state_tab.p"

DEFAULT_DICT_NAME = "dict.txt"
"""

# ################ windows环境文件路径【小助手发布】 ################
from ResumeAutometa.Foundations.utils import *

DEBUG = False

CHROME_WEBDRIVER_PATH_FILE = abs_path("resources/chrome_path.txt")

LDA_MODEL_PATH = abs_path("model/lda_training_model")

WORD_TO_ID_PATH = abs_path("model/lda_training_wordid.txt")

WORD_TO_IDF = abs_path("model/lda_training_wordidf.txt")

FILTERED_NEW_WORDS = abs_path("jieba/filtered_new_words.txt")

NEW_WORDS_FOR_JIEBA = abs_path("jieba/new_words4jieba.txt")

JIEBA_BASE_DICT = abs_path("jieba/dict.txt")

CRAWL_JOB_TOTEM = abs_path("resources/crawl_job.png")

THROW_RESUME_TOTEM = abs_path("resources/throw_resume.png")

MAIN_TOTEM = abs_path("resources/Chrome.png")

WEB_DRIVER_ACTION_SETTINGS = abs_path("resources/settings.txt")

RESUME_HISTORY = abs_path("resources/throw_history.txt")

PROB_START_P = "jieba\prob_start.p"

PROB_TRANS_P = "jieba\prob_trans.p"

PROB_EMIT_P = "jieba\prob_emit.p"

CHAR_STATE_TAB_P = "jieba\char_state_tab.p"

DEFAULT_DICT_NAME = "jieba\dict.txt"
"""

# ################ windows环境文件路径【后台数据更新】 ################

NEW_WORDS_EXTRACT_RESOURCES = "E:/PycharmProject/ResumeAutometa/Resources/Tag/new_words/"

IDF_FILTER_EXTRACT_RESOURCES = "E:/PycharmProject/ResumeAutometa/Resources/Tag/idf_filter/"

IFGAIN_FILTER_EXTRACT_RESOURCES = "E:/PycharmProject/ResumeAutometa/Resources/Tag/ifgain_filter/"

WORDVECTOR_FILTER_EXTRACT_RESOURCES = "E:/PycharmProject/ResumeAutometa/Resources/Tag/word_vector/"

CRAWLER_FOUNDATION = "E:/PycharmProject/ResumeAutometa/Crawlers/crawler_foundations/"

CRAWLER_RULE = "E:/PycharmProject/ResumeAutometa/Crawlers/crawler_foundations/crawler_rules/"

LDA_TRAINING_DATA_PATH = "E:/PycharmProject/ResumeAutometa/Resources/Train/"

LOG_CLUSTER_LOCATION = "E:/PycharmProject/ResumeAutometa/LogCluster/"

LOG_CONFIG_LOCATION = "E:/PycharmProject/ResumeAutometa/Config/log_config.ini"

# ################ Linux环境文件路径 ################
'''
CRAWLER_FOUNDATION = "/home/ubuntu/PycharmProject/ResumeAutometa/Crawlers/crawler_foundations/"

CRAWLER_RULE = "/home/ubuntu/PycharmProject/ResumeAutometa/Crawlers/crawler_foundations/crawler_rules/"

LDA_TRAINING_DATA_PATH = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/"

LDA_MODEL_PATH = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/lda_training_model"

WORD_TO_ID_PATH = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/lda_training_wordid.txt"

FILTERED_NEW_WORDS = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/JieBa/filtered_new_words.txt"

NEW_WORDS_FOR_JIEBA = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/JieBa/new_words4jieba.txt"

WORD_TO_IDF = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Train/lda_w2v/lda_training_wordidf.txt"

NEW_WORDS_EXTRACT_RESOURCES = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Tag/new_words/"

IDF_FILTER_EXTRACT_RESOURCES = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Tag/idf_filter/"

IFGAIN_FILTER_EXTRACT_RESOURCES = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Tag/ifgain_filter/"

WORDVECTOR_FILTER_EXTRACT_RESOURCES = "/home/ubuntu/PycharmProject/ResumeAutometa/Resources/Tag/word_vector/"

JIEBA_BASE_DICT = "/home/ubuntu/PycharmProject/jieba/dict.txt"

LOG_CLUSTER_LOCATION = "/home/ubuntu/PycharmProject/ResumeAutometa/LogCluster/"

LOG_CONFIG_LOCATION = "/home/ubuntu/PycharmProject/ResumeAutometa/Config/log_config.ini"

TOMCAT_BIN_LOCATION = "/home/ubuntu/servers/apache-tomcat-8.5.32/bin/"

ASYNC_LOCATION = "/home/ubuntu/PycharmProject/ResumeAutometa/ServerData/"
'''