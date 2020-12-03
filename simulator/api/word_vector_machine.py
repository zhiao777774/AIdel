import pathlib
from gensim.models import word2vec
from gensim import models


_ROOT_PATH = str(pathlib.PurePath(__file__).parent)
_MODEL_PATH = f'{_ROOT_PATH}/data/word2vec.model'
_MODEL = models.Word2Vec.load(_MODEL_PATH)

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