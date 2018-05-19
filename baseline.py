#coding: utf-8

from lxml import etree
import BagOfWords
import SearchXml
import CalucurateCoherence
import math
import os

# discrimination実験
def discrimination(numbers, n):
    for j in range(0, 20):
        exchange ={}
        i = int(n)
        import random
        random.shuffle(numbers)
        for num in numbers:
            exchange[i] = num
            i += 1
        yield exchange

# insertion実験
def insertion(numbers, n):
    exchange = {}
    for insertionNumber in range(len(numbers)):
        for sentenceNumber in range(len(numbers)):
            if insertionNumber != sentenceNumber and insertionNumber != sentenceNumber + 1:
                change = numbers[:]
                test = change[insertionNumber]
                del change[insertionNumber]
                change.insert(sentenceNumber, test)
                i = int(n)
                for c in change:
                    exchange[i] = c
                    i += 1
                yield exchange, insertionNumber, sentenceNumber


if __name__ == '__main__':

    alphas = ["0.1", "0.5", "0.9"]
    folder = "yoshi"
    method = "baseline"

    if method != 'baseline':
        segmentName = raw_input('segment >>>')
    else:
        segmentName = ''
        exchange ={}
        first = 0

    for alpha in alphas:
        for folderName in os.listdir('./{0}/output'.format(folder)):
            dataNumber = int(folderName[4])
            if folder == "tomi":
                abst = [4, 5, 6, 7]
            elif folder == "yoshi":
                abst = [5, 7]

            if dataNumber in abst:
                abstract = 1
            else:
                abstract = 0

            parser = etree.XMLParser(recover=True)
            tree = etree.parse('./{0}/output/{1}'.format(folder, folderName), parser=parser)
            elem = tree.getroot()

            data = elem.findall('.//sen')
            documents = {}
            segment = []
            for linedata in data:
                sentenceNumber = int(linedata.attrib["num"])
                if not (abstract == 0 and int(SearchXml.parentSet(elem, sentenceNumber)["chapter"]) == 0):
                    linedata = (linedata.text).rstrip('\n')
                    documents[sentenceNumber] = linedata
                    if method != 'baseline':
                        segmentNumber = SearchXml.parentSet(elem, sentenceNumber)[segmentName]
                        if not segmentNumber in segment:
                            segment.append(segmentNumber)

            # 類似度が0.1以上の文ペアを拾ってくる
            senAndDeg = BagOfWords.sentenceAndDegree(documents, 0.1)
            # coherenceを計算する
            u"""elem: xmlの親子情報
            　　senAndDeg: {(文ペア):類似度}のディクショナリ
            　　alpha: パラメータ
            　　abstract: 概要が0ある，1ない
            　　segmentName: 入れ替え実験の時に使う
            　　exchange: 入れ替え実験の時に使う"""
            coherence = CalucurateCoherence.allCoherence(elem, senAndDeg, float(alpha), abstract, segmentName, exchange)
            print coherence
            break
        break
