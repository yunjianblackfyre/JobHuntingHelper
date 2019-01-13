#   AUTHOR: Sibyl System
#     DATE: 2018-03-03
#     DESC: 训练词向量

from gensim.models import Word2Vec
from ResumeAutometa.Config.file_paths import WORDVECTOR_FILTER_EXTRACT_RESOURCES
from gensim.models.word2vec import LineSentence

training_data_path = WORDVECTOR_FILTER_EXTRACT_RESOURCES + "wordvector_filter_data_training.txt"
model_save_path = WORDVECTOR_FILTER_EXTRACT_RESOURCES + "model/w2v_model"


class MyWord2Vector(object):
    # 构造word2vector训练数据
    def run(self):
        sentences = LineSentence(training_data_path)
        model = Word2Vec(sentences, size=32, window=5, min_count=1, workers=4,compute_loss=True)
        print("Total loss:%s" % model.get_latest_training_loss())
        model.save(model_save_path)
        

if __name__ == '__main__':
    word2vector = MyWord2Vector()
    word2vector.run()
