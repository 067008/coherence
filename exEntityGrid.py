#coding: utf-8

from pprint import pprint

def allElement(latList):
    chunk = []
    relationNumber = []
    wordRole = []
    syntaxRole = []
    for element in latList[:-2]:
        if element.startswith('* '):
            sentenceRole = element.split(" ")
            relationNumber.append(sentenceRole[2][:-1])
            if len(wordRole) > 0:
                chunk.append(wordRole)
                syntaxRole.append((keiJoshi, kakuJoshi))
            keiJoshi = 0
            kakuJoshi = 0
            wordRole = []
        else:
            particle = element.split(',')
            if particle[1] == "係助詞":
                keiJoshi = 1
            if particle[1] == "格助詞":
                kakuJoshi = 1
            wordRole.append(element)
    chunk.append(wordRole)
    syntaxRole.append((keiJoshi, kakuJoshi))
    return chunk, syntaxRole, relationNumber

def entity_grid(documents):
    import CaboCha
    allChunk = []
    allRerationNumber = []
    allSyntaxRole = []
    for doc in documents:
        pumpkin = CaboCha.Parser('-u ./load/symbol.dic')
        doc = doc.encode("utf-8")
        tree = pumpkin.parse(doc)
        lattice = tree.toString(CaboCha.FORMAT_LATTICE)
        latList = lattice.split("\n")
        allInformation = allElement(latList)
        allChunk.append(allInformation[0])
        allSyntaxRole.append(allInformation[1])
        allRerationNumber.append(allInformation[2])

    # ここまでは折れる、点があった
    syntaxRoles = []
    for i in range(len(allRerationNumber)):
        syntaxRole = []
        for j in range(len(allRerationNumber[i])):
            if int(allRerationNumber[i][j]) == len(allRerationNumber[i]) - 1:
                if allSyntaxRole[i][j][0] == 1:
                    syntaxRole.append(3)
                elif allSyntaxRole[i][j][1] == 1:
                    syntaxRole.append(2)
                else:
                    syntaxRole.append(1)
            else:
                syntaxRole.append(1)
        syntaxRoles.append(syntaxRole)

    import Preprocessing
    allEntity = []
    allWords = {}
    dictionaryNumber = 0
    for i, chunk in enumerate(allChunk):
         pair = Preprocessing.pair_cabocha(chunk)
         compoundProcess = Preprocessing.compound(pair)
         texts = Preprocessing.extractionoun(compoundProcess)
         # print texts
         # for t in texts:
         #     print ",".join(t)

         entity = {}
         for j, text in enumerate(texts):
             for word in text:
                 if not word in allWords:
                     allWords[word] = dictionaryNumber
                     dictionaryNumber += 1
                 if not word in entity:
                     entity[word] = []
                     entity[word].append(syntaxRoles[i][j])
                 else:
                     entity[word].append(syntaxRoles[i][j])
         allEntity.append(entity)

    # print allWords

    texts = []
    for entity in allEntity:
        text = []
        for noun, syntaxr in entity.items():
            if len(syntaxr) > 1:
                roleNumber = max(syntaxr)
            else:
                roleNumber = syntaxr[0]
            text.append((allWords[noun], roleNumber))
            # print noun, roleNumber
        texts.append(text)
    # for w, n in allWords.items():
    #     print w, n

    from scipy.sparse import lil_matrix, csr_matrix
    from scipy.sparse.linalg import svds
    import numpy as np
    dense = lil_matrix((len(allWords), len(texts)))
    for i in range(len(texts)):
       for word, role in texts[i]:
           if not role == 0:
               dense[word, i] = role
    dense = dense.T

    # for i, j in all_words.items():
    #     print i, j
    return dense.toarray()

def allweight(entity, weight):
    weightentity = []
    for i in range(len(entity)):
        line = []
        for j in range(len(entity)):
            cnt = 0
            if i < j:
                for k in range(len(entity[i])):
                    side1Role = entity[i][k]
                    side2Role = entity[j][k]
                    if side1Role != 0 and side2Role != 0:
                        if weight == "unweighted":
                            cnt = 1
                        if weight == "weighted":
                            cnt += 1
                        if weight == "acc":
                            cnt = cnt + (side1Role * side2Role)
                cnt = float(cnt) / (j - i)
            line.append(cnt)
        weightentity.append(line)
    return weightentity

def localcoherence(outdegree):
    allSum = 0
    for i in range(len(outdegree)):
        sentenceSum = 0
        for j in range(len(outdegree[i])):
            # if outdegree[i][j] > 0:
            #     outdegree[i][j] = float(outdegree[i][j]) / (j - i)
            sentenceSum = sentenceSum + outdegree[i][j]
        allSum = allSum + sentenceSum
    coherence = float(allSum) / len(outdegree)
    return coherence
