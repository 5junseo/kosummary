from konlpy.tag import Okt
from collections import Counter

okt = Okt()


def morph_counters(line):
    noun = tag_del(line)
    for i, v in enumerate(noun):
        if len(v) < 2:
            noun.pop(i)
    count = Counter(noun)
    noun_list = count.most_common(100)
    return noun_list


def noun_counters(line):
    noun = okt.nouns(line)
    for i, v in enumerate(noun):
        if len(v) < 2:
            noun.pop(i)
    count = Counter(noun)
    noun_list = count.most_common(100)
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
        print(i, " : ", tag)
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
