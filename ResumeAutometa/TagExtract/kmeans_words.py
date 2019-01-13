#   AUTHOR: Sibyl System
#    DATE: 2018-03-06
#    DESC: 用kmeans尝试不同的聚类数目N
#    并且在单次聚类中初始化M次
#    找到最优的N，并且聚类结果
#    提交给人工过滤作为最终结果

import numpy as np
from ResumeAutometa.Foundations.utils import *
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from ResumeAutometa.Config.file_paths import IFGAIN_FILTER_EXTRACT_RESOURCES
from ResumeAutometa.Config.file_paths import WORDVECTOR_FILTER_EXTRACT_RESOURCES

# 全局变量
IDF_CEILING = 20
IDF_FLOOR = 0
model_save_path = WORDVECTOR_FILTER_EXTRACT_RESOURCES + "model/w2v_model"
label2words_path = WORDVECTOR_FILTER_EXTRACT_RESOURCES + "label2words.txt"
allowed_words_path = IFGAIN_FILTER_EXTRACT_RESOURCES + "allowed_words.txt"
    

class CKmeansWords(object):
    def __init__(self):
        self.label2words = dict()
        self.allowed_words = set()
        
    def __reset__(self):
        self.label2words = dict()
        self.allowed_words = set()
        
    def _load_words(self):
        self.allowed_words = set(read_file_json(allowed_words_path))
        
    def _load_vectors(self):
        model = Word2Vec.load(model_save_path)
        word_list = []
        vector_list = []
        
        for word in model.wv.index2word:
            if word in self.allowed_words:
                word_list.append(word)
                vector_list.append(model.wv[word])
        Xvector = np.array(vector_list)
        return Xvector, word_list, vector_list
        
    def _multi_clustering(self):
        Xvector, word_list, vector_list = self._load_vectors()
        best_cluster_quality = 100

        # 从10-150聚类 比较质点距离
        # 根据调优结果，最佳聚类数目为80
        for cluster_size in range(80,81):
            kmeans = KMeans(
                n_clusters=cluster_size, 
                init='k-means++',
                n_init=25,
                precompute_distances=True,
            ).fit(Xvector)
            Yvectors = kmeans.labels_
            print("-"*16, "Current cluster size: %s" % cluster_size, "-"*16)
            close_pair_num = self._show_clustering_quality(Yvectors, word_list, vector_list)
            
            cluster_quality = close_pair_num/(float(cluster_size)*cluster_size/2)
            if cluster_quality < best_cluster_quality:
                best_cluster_quality = cluster_quality
                print("current best cluster size and quality: %s, %s" % (cluster_size, cluster_quality))
                
    def _show_clustering_quality(self, Yvectors, word_list, vector_list):
        # 初始化变量
        label2words = dict()
        label2vectors = dict()
        label2centroid = dict()
        label2radius = dict()
        pair_key_set = set()
        close_pair_num = 0
        
        # 将聚类结果打包
        for idx in range(len(Yvectors)):
            label = str(Yvectors[idx])
            word = word_list[idx]
            vector = vector_list[idx]
            try:
                label2words[label].append(word)
                label2vectors[label].append(vector)
            except:
                label2words[label] = [word]
                label2vectors[label] = [vector]
        self.label2words = label2words
                
        # 计算类->中心点词典，与类->较远词列表
        for label in label2words.keys():
            vectors = label2vectors[label]
            words = label2words[label]
            centroid = sum(vectors)/len(vectors)
            label2centroid[label] = centroid

            distances = np.linalg.norm(vectors-centroid,axis=1)
            word_info_list = []
            for idx in range(len(words)):
                # word_info_tuple = (
                #     words[idx],
                #     distances[idx],
                # )
                # word_info_list.append(word_info_tuple)
                word_info_list.append(distances[idx])
                
            # 可根据词向量离质心平均距离进行排序
            # word_info_list = sorted(word_info_list, key=lambda tup: tup[1],reverse=True)
            word_info_list.reverse()
            
            # 计算类的半径
            if len(word_info_list) <= 10:
                radius = sum(word_info_list)/(len(word_info_list) + 0.01)
            else:
                sample_num = int((len(word_info_list)*0.1)+1)   # 取离中心距离较远的样本点10%
                radius = sum(word_info_list[0:sample_num])/sample_num
            
            label2radius[label] = radius
            
        # 寻找可以合并的聚类
        for label_1 in label2centroid.keys():
            for label_2 in label2centroid.keys():

                if label_1!=label_2:
                    pair_key = [str(label_1), str(label_2)]
                    pair_key.sort()
                    pair_key = "_".join(pair_key)
                    if pair_key not in pair_key_set:
                        pair_key_set.add(pair_key)
                    else:
                        continue

                    radius_1 = label2radius[label_1]
                    radius_2 = label2radius[label_2]
                    centroid_1 = label2centroid[label_1]
                    centroid_2 = label2centroid[label_2]
                    
                    centroid_distance = np.linalg.norm(centroid_1-centroid_2)
                    radius_sum = radius_1 + radius_2
                    
                    # 计算两个类的距离： >1.5 两个类相互独立 1与1.5之间 两个类很接近 <1 两个类可以合并
                    true_distance = (centroid_distance/radius_sum)
                    if true_distance < 1.0:
                        # print("%s, %s, These clusters are so close, they should get married %s" %
                        # (label_1, label_2, true_distance))
                        close_pair_num += 1
                        # print(label2words[label_1])
                        # print(label2words[label_2])
        
        return close_pair_num
    
    # 保存将机器最后的聚类结果
    def _save_clusters(self):
        write_data2json(self.label2words, label2words_path)
        # np.save('./models/kmeans_topics',np.array(self.centroids))
            
    # 构造word2vector训练数据
    def run(self):
        self._load_words()
        self._multi_clustering()
        self._save_clusters()
    
    # 主过程
    def process(self):
        print('kmeans start clustering...')
        self.run()
        self.__reset__()
        

if __name__ == '__main__':
    kmeans = CKmeansWords()
    kmeans.process()
