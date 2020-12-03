from gensim.models import word2vec
from gensim import models

import file_controller as fc


MODEL_PATH = f'{fc.ROOT_PATH}/data/word2vec.model'
_MODEL = models.Word2Vec.load(MODEL_PATH)

def find_synonyms(query, n = 100):
    synonyms = []

    res = _MODEL.most_similar(query, topn = n)
    for word, confidence in res:
        synonyms.append((word, confidence))

    return synonyms

def compare_synonym(query):
    return _MODEL.similarity(query[0], query[1])

def compare_similarity(query, n = 100):
    return _MODEL.most_similar([query[0], query[1]], [query[2]], topn = n)


if __name__ == '__main__':
    while True:
        try:
            print("提供 3 種測試模式:\n")
            print("輸入一個詞，則去尋找前一百個該詞的相似詞")
            print("輸入兩個詞，則去計算兩個詞的餘弦相似度")
            print("輸入三個詞，進行類比推理")

            query = input()
            q_list = query.split()

            if len(q_list) == 1:
                print('相似詞前 100 排序')

                res = find_synonyms(q_list[0], 100)
                for word, confidence in res:
                    print(f'{word}: {confidence}')
            elif len(q_list) == 2:
                print('計算 Cosine 相似度')

                prob = compare_synonym((q_list[0], q_list[1]))
                print(prob)
            else:
                print(f'{q_list[0]}之於{q_list[2]}，如{q_list[1]}之於')

                res = compare_similarity(q_list, 100)
                for word, confidence in res:
                    print(f'{word}: {confidence}')
        except Exception as e:
            print(e)
            break