#coding: utf-8
import SearchXml
import math

def searchCommon(elem, side1Parents, side2Parents, target, exchange):
    u"""類似している親同士の情報から共通の親を探索する"""
    hierarchy = ["paragraph", "item", "section", "chapter", "doc"]
    matchedParent = [parent for parent in side1Parents.keys() if parent in side2Parents]
    minFlag = 0
    pairParent = {}
    for role in hierarchy:
        if role in matchedParent:
            if side1Parents[role] == side2Parents[role] and minFlag == 0:
                CommonParent = role
                parentNumber = side1Parents[role]
                minFlag += 1
        if minFlag > 0:
            break
    if minFlag == 0:
        CommonParent = "doc"
        parentNumber = 0

    rvHierarchy = hierarchy[::-1]
    down = rvHierarchy.index(CommonParent)
    if down == len(hierarchy) - 1:
        key = "sen"
    else:
        for i in range(down + 1, len(hierarchy)):
            if rvHierarchy[i] in side1Parents.keys():
                key = rvHierarchy[i]
                break
    if key == target:
        dis1 = int(exchange[int(side1Parents[key])])
        dis2 = int(exchange[int(side2Parents[key])])
    else:
        dis1 = int(side1Parents[key])
        dis2 = int(side2Parents[key])
    childlist = [dis1, dis2, key]

    return CommonParent, parentNumber, childlist

def calculationCoherence(elem, abstract, parentKey, key, value):
    u"""網羅割合，構造同士の距離，類似度，枝数から一貫性を算出する"""
    sigma = 0
    upgrade = 0
    coverage = []
    numberOfarc = len(value)
    for dis, degree in value:
        # print dis
        if not dis[0] in coverage:
            coverage.append(dis[0])
        if not dis[1] in coverage:
            coverage.append(dis[1])
        distance = abs(dis[0] - dis[1]) # 構造同士の距離
        degreeDevideDistance = float(degree) / distance
        sigma = sigma + degreeDevideDistance # 構造ごとに「類似度/距離」を足し合わせる
    if abstract == 0 and dis[2] == "chapter":
        numberOfchildlen = SearchXml.getChildNumber(elem, parentKey, key, dis[2]) - 1
    else:
        numberOfchildlen = SearchXml.getChildNumber(elem, parentKey, key, dis[2])

    if not parentKey in ["chapter", "doc"]:
        directParentNumber = SearchXml.getParent(elem, parentKey, key)
        parentChildren = SearchXml.getChildNumber(elem, directParentNumber[0], directParentNumber[1], parentKey)
        if parentChildren == 1:
            upgrade = 1 # 上の構造の子供が一人だったらフラグを立てる

    coverageRatio = float(len(coverage)) / numberOfchildlen # 網羅割合を計算する
    localCoherence = coverageRatio * sigma / numberOfarc # いほり一貫性の計算
    # test出力
    # print coverageRatio, sigma, numberOfarc, localCoherence

    return localCoherence, upgrade

def globalCoherence(elem, coherenceIreko, alpha_input):
    u"""coherenceIrekoから下の階層の平均を掛け合わせた値を算出する"""
    import math
    alpha = float(alpha_input)
    hierarchy = ["paragraph", "item", "section", "chapter"]
    for role in hierarchy:
        addAverage = {}
        if role in coherenceIreko.keys():
            for key in coherenceIreko[role].keys():
                parent = SearchXml.getParent(elem, role, key)
                parentRole = parent[0]
                parentNum = parent[1]
                # print role, key, parent
                if not parentRole in addAverage:
                    addAverage[parentRole] = {}
                    if not parentNum in addAverage[parentRole]:
                        addAverage[parentRole][parentNum] = []
                        addAverage[parentRole][parentNum].append(coherenceIreko[role][key])
                    else:
                        addAverage[parentRole][parentNum].append(coherenceIreko[role][key])
                else:
                    if not parentNum in addAverage[parentRole]:
                        addAverage[parentRole][parentNum] = []
                        addAverage[parentRole][parentNum].append(coherenceIreko[role][key])
                    else:
                        addAverage[parentRole][parentNum].append(coherenceIreko[role][key])
            for Parent in addAverage.keys():
                if Parent in coherenceIreko.keys():
                    for key, value in addAverage[Parent].items():
                        if key in coherenceIreko[Parent].keys():
                            coherenceSum = 0
                            for coherence in value:
                                coherenceSum = coherenceSum + coherence
                            coherenceAverage = coherenceSum / len(value)
                            coherenceIreko[Parent][key] = (coherenceIreko[Parent][key]**alpha) * (coherenceAverage**(1 - alpha))
                            # print Parent, key, coherenceIreko[Parent][key]
                            # coherenceIreko[Parent][key] = coherenceIreko[Parent][key] * coherenceAverage
    return coherenceIreko["doc"][0]

def allCoherence(elem, senAndDeg, alpha, abstract, target, exchange):
    ireko = {}
    for pair in senAndDeg.keys():
        u"""類似している文ペアの要素"""
        sen1, sen2 = pair

        u"""文の親をディクショナリ形式ですべて取り出す"""
        parents1 = SearchXml.parentSet(elem, sen1)
        parents2 = SearchXml.parentSet(elem, sen2)

        u"""文ペアの同じ親と構造同士の距離を取り出す"""
        common = searchCommon(elem, parents1, parents2, target, exchange)
        commonParent = common[0]
        parentNumber = common[1]
        childlenNumber = common[2]

        u"""親の構造，構造番号ごとに[子供の構造の距離, 構造の種類]，類似度をirekoディクショナリにまとめる"""
        childPair = (childlenNumber, senAndDeg[pair])
        if not commonParent in ireko:
            ireko[commonParent] = {}
            if not parentNumber in ireko[commonParent]:
                ireko[commonParent][parentNumber] = []
                ireko[commonParent][parentNumber].append(childPair)
            else:
                ireko[commonParent][parentNumber].append(childPair)
        else:
            if not parentNumber in ireko[commonParent]:
                ireko[commonParent][parentNumber] = []
                ireko[commonParent][parentNumber].append(childPair)
            else:
                ireko[commonParent][parentNumber].append(childPair)


    u"""irekoディクショナリのvalueを一貫性の値に変更し，
    子供が1人しかいない親は1つ上げる:coherenceIreko"""
    import copy
    coherenceIreko = copy.deepcopy(ireko)
    for parentKey in ireko.keys():
        # sum_segment = 0
        for key, value in ireko[parentKey].items():
            # test出力
            # print parentKey, key, len(value)
            # sum_segment = sum_segment + len(value)
            localCoherence = calculationCoherence(elem, abstract, parentKey, key, value)
            ireko[parentKey][key] = localCoherence[0]
            if localCoherence[1] == 1:
                upgrade = SearchXml.getParent(elem, parentKey, key)
                coherenceIreko[upgrade[0]][upgrade[1]] = localCoherence[0]
                del coherenceIreko[parentKey][key]
            else:
                coherenceIreko[parentKey][key] = localCoherence[0]
        # print parentKey, sum_segment, float(sum_segment)/len(ireko[parentKey])

    # test出力
    # for i, j in coherenceIreko.items():
    #     print i, len(j)
    #     for k, l in j.items():
    #         print k, l

    u"""文章全体の一貫性の値"""
    return globalCoherence(elem, coherenceIreko, alpha)
