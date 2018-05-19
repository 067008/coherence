# coding: utf-8

from xml.etree.ElementTree import *

def iterparent(elem, childlen):
    u"""親を見つけるたびに返す"""
    for parent in elem.getiterator():
        for child in parent:
            if child == childlen:
                yield parent

def getParent(elem, childlen, childNum):
    u"""直属の親のみを返す"""
    for parent in elem.getiterator():
        for child in parent:
            if child.tag == childlen and child.attrib["num"] == childNum:
                if parent.tag != "doc":
                    return parent.tag, parent.attrib["num"]
                else:
                    return parent.tag, 0

def getChildNumber(elem, parentTag, parentNum, childTag):
    u"""親の子供のうち、childTagのみのものの数を返す"""
    numberOfChild = 0
    for parent in elem.getiterator():
        if parent.tag in ["chapter", "section", "item", "paragraph"]:
            if parent.tag == parentTag and parent.attrib["num"] == parentNum:
                for child in parent:
                    if (child.tag != "t") and (child.tag == childTag):
                        numberOfChild += 1
        elif parent.tag == parentTag:
            for child in parent:
                if child.tag == childTag:
                    numberOfChild += 1
    return numberOfChild

def parentSet(elem, sentenceNumber):
    u"""文の親をディクショナリ形式ですべて返す"""
    parents = {}
    search = ''
    sentenceImformation = elem.findall('.//sen[@num="{0}"]'.format(sentenceNumber))
    for sentence in sentenceImformation:
        child = sentence
        while search != 'chapter':
            for parent in iterparent(elem, child):
                parents[parent.tag] = parent.attrib["num"]
                search = parent.tag
                child = parent
    parents["sen"] = sentenceNumber
    return parents
