# coding: utf-8

from lxml import etree
import BagOfWords
import SearchXml
import ChangeDocuments
import math
import CalucurateCoherence
import os
import exEntityGrid
import codecs

def insertion(documents):
    for insertionNumber in range(len(documents)):
        for sentenceNumber in range(len(documents)):
            newdocuments = []
            if insertionNumber != sentenceNumber and insertionNumber != sentenceNumber + 1:
                change = documents[:]
                test = change[insertionNumber]
                del change[insertionNumber]
                change.insert(sentenceNumber, test)
                for chan in change:
                    newdocuments = newdocuments + chan
                yield newdocuments, insertionNumber, sentenceNumber

def discrimination(documents):
    for i in range(0, 20):
        newdocuments = []
        import random
        random.shuffle(documents)
        for doc in documents:
            newdocuments = newdocuments + doc
        yield newdocuments

if __name__ == "__main__":

    date = "sentence"
    segmentName = "sen"
    whichs = [0.1, 0.5, 0.9]
    folder = "yoshi"
    method = "insertion"


    for which in whichs:
        os.makedirs("./{0}/{1}/{2}/{3}".format(date, which, folder, method))
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
            tree = etree.parse('./{0}/output/data{1}.xml'.format(folder, dataNumber), parser=parser)
            elem = tree.getroot()
            data = elem.findall('.//sen')

            documents = []
            numberChange = {}
            i = 0
            segmentNumber = -1
            segment = []
            for linedata in data:
                sentenceNumber = int(linedata.attrib["num"])
                if not (abstract == 0 and int(SearchXml.parentSet(elem, sentenceNumber)["chapter"]) == 0):
                    if segmentNumber != SearchXml.parentSet(elem, sentenceNumber)[segmentName]:
                        segmentNumber = SearchXml.parentSet(elem, sentenceNumber)[segmentName]
                        if len(segment) > 0:
                            documents.append(segment)
                        segment = []
                    linedata = (linedata.text).rstrip('\n')
                    segment.append(linedata)
                    numberChange[i] = sentenceNumber
                    i += 1
            documents.append(segment)

            print "data" + str(dataNumber)

            # insertion
            os.makedirs("./{0}/{1}/{2}/{3}/data{4}".format(date, which, folder, method, dataNumber))

            for doc in insertion(documents):
                sentenceNumber1 = doc[1]
                sentenceNumber2 = doc[2]
                # ihori
                target = ""
                exchange = {}
                senAndDeg = BagOfWords.sentenceAndDegree(doc[0], 0.1)
                coherence = CalucurateCoherence.allCoherence(elem, senAndDeg, float(which), abstract, target, exchange)

                import codecs
                f = codecs.open("./{0}/{1}/{2}/{3}/data{4}/data{5}.txt".format(date, which, folder, method, dataNumber, sentenceNumber1), 'a', 'utf-8')
                print sentenceNumber1, sentenceNumber2
                f.write("data" + str(sentenceNumber2) + "\n")
                f.write("coherence:" + str(coherence) + "\n")
        break
    break
            #discrimination
            # for i, doc in enumerate(discrimination(documents)):
            #
            #     # eintity grid
            #     # entity = exEntityGrid.entity_grid(doc)
            #     # outdegree = exEntityGrid.allweight(entity, which)
            #     # coherence = exEntityGrid.localcoherence(outdegree)
            #
            #     # ihori
            #     target = ""
            #     exchange = {}
            #     senAndDeg = BagOfWords.sentenceAndDegree(doc, 0.1)
            #     coherence = CalucurateCoherence.allCoherence(elem, senAndDeg, float(which), abstract, target, exchange)
            #
            #     f = codecs.open("./{0}/{1}/{2}/{3}/data{4}.txt".format(date, which, folder, method, dataNumber), 'a', 'utf-8')
            #     f.write("data" + str(i) + "\n")
            #     print "data" + str(i)
            #     f.write("coherence:" + str(coherence) + "\n")
            #     print coherence
