import word2vec


def find_synonyms(self, word):
    synonyms = []

    model = word2vec.load('corpusWord2Vec.bin')
    indexes = model.cosine(word)
    for index in indexes[0]:
        synonyms.append(model.vocab[index])

    return synonyms