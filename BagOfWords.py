# coding:utf-8

import Preprocessing

def similarityMatrix(documents):
    u"""Bag Of Words を作成する"""
    # 単語抽出
    texts = Preprocessing.extractKeyword(documents)

    from gensim import corpora, models, similarities
    # 辞書作成
    dictionary = corpora.Dictionary(texts)

    #　コーパス作成
    corpus = [dictionary.doc2bow(text) for text in texts]
    # tfidf = models.TfidfModel(corpus)
    # corpus_tfidf = [tfidf[corpus[i]] for i in range(len(corpus))]

    # 疎行列作成
    from scipy.sparse import lil_matrix, csr_matrix
    from scipy.sparse.linalg import svds
    import numpy as np
    dense = lil_matrix((len(dictionary), len(corpus)))
    for i in range(len(corpus)):
       for w, h in corpus[i]:
           if not h == 0:
               dense[w, i] = h
    dense = dense.T

    norms = np.sqrt(dense.multiply(dense).sum(axis=1))
    for j in range(dense.shape[0]):
        dense[j, :] /= norms[j]
    sims = dense.dot(dense.T)
    return sims

def sentenceAndDegree(documents, min):
    u"""類似している文ペアとその類似度"""
    dict = 0
    if not isinstance(documents, list):
        sentenceList = documents.values()
        numberList = documents.keys()
        dict = 1
    else:
        sentenceList = documents

    vector = similarityMatrix(sentenceList)
    vector = vector.toarray()

    import numpy as np
    row, col = np.where(min <= vector)
    pair = {}
    for i in range(len(row)):
        x = row[i]
        y = col[i]
        if x != y:
            if dict == 1:
                sentencePair = (numberList[x], numberList[y])
            else:
                sentencePair = (x, y)
            pair[sentencePair] = vector[x, y]
    return pair
