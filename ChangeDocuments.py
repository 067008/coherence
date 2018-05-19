#coding: utf-8

def insertion(documents):
    from numpy import *
    index = range(0, len(documents) - 1)
    changeNumber = random.choice(index, 30, replace=False)
    changeSentence = changeNumber[:20]

    for insertionNumber in changeSentence:
        for sentenceNumber in range(len(documents)):
            change = documents[:]
            test = change[insertionNumber]
            del change[insertionNumber]
            change.insert(sentenceNumber, test)
            yield change, insertionNumber, sentenceNumber


def discrimination(documents):
    for i in range(0, 20):
        import random
        random.shuffle(documents)
        yield documents
