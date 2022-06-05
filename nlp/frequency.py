import random

from konlpy.tag import Okt
from collections import Counter

okt = Okt()


def morph_counters(line):
    text = emoticon_del(line)
    #print(text)
    if text != "":
        morph = tag_del(text)
        for i, v in enumerate(morph):
            if len(v) < 2:
                morph.pop(i)
        count = Counter(morph)
        morph_list = count.most_common(100)
    else:
        morph = okt.morphs("Emoticon")
        temp = Counter(morph)
        morph_list = temp.most_common(1)
    return morph_list


def noun_counters(line):
    text = emoticon_del(line)
    if text != "":
        noun = okt.nouns(text)
        if noun != "":
            for i, v in enumerate(noun):
                if len(v) < 2:
                    noun.pop(i)
            count = Counter(noun)
            noun_list = count.most_common(100)
        else:
            noun = okt.noun(str(random.random()))
            temp = Counter(noun)
            noun_list = temp.most_common(1)
    else:
        noun = okt.noun(str(random.random()))
        temp = Counter(noun)
        noun_list = temp.most_common(1)
    return noun_list


# 이모티콘 삭제
def emoticon_del(text):
    temp = text
    while temp.count(":") >= 2:
        qwe = temp.split(':', 2)
        temp = qwe[0] + qwe[2]
    return temp


# 이모티콘 추출
def emoticon_ext(text):
    temp = text
    temp2 = 0
    while temp.count(":") >= 2:
        qwe = temp.split(':', 2)
        temp = qwe[0] + qwe[2]
        if temp2 != 0:
            temp2 += ' ' + qwe[1]
        else:
            temp2 = qwe[1]
    return temp2


# 형태소 분석 태그 확인해서 필요없는 것 제거
#  tag_delite_list = ['Josa', 'Punctuation', 'Foreign']
def tag_del(text):
    analysis = okt.pos(text, norm=True, stem=True)
    for i, tag in enumerate(analysis):
        # print(i, " : ", tag)
        if 'Josa' in tag:
            analysis[i] = "None"
        elif 'Punctuation' in tag:
            analysis[i] = "None"
        elif 'Foreign' in tag:
            analysis[i] = "None"
    word_list = 0
    for word in analysis:
        if word != "None":
            if word_list != 0:
                word_list += ' ' + word[0]
            else:
                word_list = word[0]
    temp = okt.morphs(word_list)
    return temp
