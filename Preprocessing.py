# coding:utf-8

u"""文書の前処理を行う"""

# keitaisokaiseki---------------------------------------------
def pair(documents):
    import MeCab
    tagger = MeCab.Tagger('-u ./load/symbol.dic mecabrc')
    keys = ['hyoso', 'hinshi', 'one', 'two', 'katsu', 'genke']
    words = []
    for doc in documents:
        # if unicode(doc).startswith('<'):
        #     continue
        encode_text = doc.encode('utf-8')
        #encode_text = doc.encode('utf-8')
        result = tagger.parse(encode_text)
        #result = encode_result.decode('utf-8')
        #print result
        kekka = result.split('\n')
        onefrase = []
        for line in kekka:
            value = line.split('\t')
            if len(value) > 1:
                values = []
                values.append(value[0])
                part = value[1].split(',')
                values.append(part[0])
                values.append(part[1])
                values.append(part[2])
                values.append(part[5])
                values.append(part[6])
                word = dict(zip(keys, values))
                onefrase.append(word)
        words.append(onefrase)
    return words
#---------------------------------------------------------------------

def pair_cabocha(texts):

    keys = ['hyoso', 'hinshi', 'one', 'two', 'katsu', 'genke']
    words = []
    for text in texts:
        onefrase = []
        for tex in text:
            value = tex.split('\t')
            values = []
            values.append(value[0])
            part = value[1].split(',')
            values.append(part[0])
            values.append(part[1])
            values.append(part[2])
            values.append(part[5])
            values.append(part[6])
            word = dict(zip(keys, values))
            onefrase.append(word)
        words.append(onefrase)
    return words

# fukugoumeisi--------------------------------------------------------
def compound(words):
    search = [[{'position': 0, 'key': 'hinshi', 'value': '接頭詞'},
               {'position': 0, 'key': 'one', 'value': '名詞接続'},
               {'position': 1, 'key': 'hinshi', 'value': '名詞'}],
              [{'position': 0, 'key': 'one', 'value': '接尾'}],
              [{'position': 0, 'key': 'hinshi', 'value': '名詞'},
               {'position': 0, 'key': 'one', 'value': '一般'},
               {'position': 1, 'key': 'hinshi', 'value': '動詞'},
               {'position': 1, 'key': 'katsu', 'value': '連用形'}]]


    for n in range(len(search)):
        for i in range(len(words)):
            for j in range(len(words[i])):

                positions = []
                for cond in search[n]:
                    positions.append(cond['position'])

                matched = True
                for cond in search[n]:
                    if len(words[i]) == j + cond['position']:
                        matched = False
                        break
                    if not words[i][j + cond['position']][cond['key']] == cond['value']:
                        matched = False
                        break
                    elif words[i][j + cond['position']]['genke'] in ['する', 'ご', 'お', '元', 'いる']:
                        matched = False
                        break
                    elif words[i][j + cond['position']]['two'] in ['助数詞', '副詞可能']:
                        matched = False
                        break
                    elif words[i][j + cond['position']]['one'] in ['数']:
                        matched = False
                        break
                    elif words[i][j + cond['position'] - 1]['genke'] in ['する', 'ご', 'お', 'いる']:
                        matched = False
                        break
                    elif words[i][j + cond['position'] - 1]['one'] in ['数', '副詞可能', '代名詞']:
                        matched = False
                        break
                    elif words[i][j + cond['position'] - 1]['hinshi'] in ['記号', '助詞']:
                        matched = False
                        break

                if matched:
                    if max(positions) == 0:
                        fuku = words[i][j-1]['hyoso'] + words[i][j]['genke']
                        words[i][j-1]['hinshi'] = 'スキップ'
                        words[i][j] = {'hyoso': fuku, 'hinshi': '複合名詞', 'one': '*', 'two': '*', 'katsu': '*', 'genke': fuku}
                    else:
                        fuku = words[i][j]['genke'] + words[i][j+1]['hyoso']
                        words[i][j+1]['hinshi'] = 'スキップ'
                        words[i][j] = {'hyoso': fuku, 'hinshi': '複合名詞', 'one': '*', 'two': '*', 'katsu': '*', 'genke': fuku}
    return words
#-----------------------------------------------------------------------------

# wordextract----------------------------------------------------------------
def extraction(words):
    texts = []
    for i in range(len(words)):
        text = []
        for j in range(len(words[i])):
            if not words[i][j]['hinshi'] in {"助詞", "助動詞", "連体詞", "接続詞", "連語", "副詞", "接頭詞", "記号", "フィラー", "スキップ"}:
                if not words[i][j]['one'] in {"形容動詞語幹", "副詞可能", "代名詞", "ナイ形容詞語幹", "特殊", "数", "接尾", "非自立"}:
                    if words[i][j]['genke'] == '*':
                        if len(words[i][j]['hyoso']) > 1:
                            text.append(words[i][j]['hyoso'])
                        else:
                            continue
                    else:
                        text.append(words[i][j]['genke'])
        texts.append(text)
    return texts
#-------------------------------------------------------------------------

def extractionoun(words):
    texts = []
    for i in range(len(words)):
        text = []
        for j in range(len(words[i])):
            if words[i][j]['hinshi'] in ["名詞", "複合名詞"]:
                if not words[i][j]['one'] in {"形容動詞語幹", "副詞可能", "代名詞", "ナイ形容詞語幹", "特殊", "数", "接尾", "非自立"}:
                    if words[i][j]['genke'] == '*':
                        if len(words[i][j]['hyoso']) > 1:
                            text.append(words[i][j]['hyoso'])
                        else:
                            continue
                    else:
                        text.append(words[i][j]['genke'])
        texts.append(text)

    import codecs
    stop = codecs.open("./load/stop.txt", 'r', 'utf-8')
    for stopWord in stop:
        stoplist = stopWord.split()
    exclusion = []
    for line in stoplist:
        exclusion.append(line.encode('utf-8'))
    texts = [[word for word in text if word not in exclusion] for text in texts]

    return texts

#------------------------------------------------------------------------

def extractKeyword(documents):
    p = pair(documents)
    c = compound(p)
    texts = extraction(c)
    import codecs
    stop = codecs.open("./load/stop.txt", 'r', 'utf-8')
    for i in stop:
       stoplist = i.split()
    st = []
    for s in stoplist:
        st.append(s.encode('utf-8'))
    texts = [[word for word in text if word not in st] for text in texts]
    # for text in texts:
    #     print ','.join(text)
    return texts
