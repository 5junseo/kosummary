from konlpy.tag import Okt
from collections import Counter

okt = Okt()


def noun_counters(line):
    noun = okt.nouns(line)
    for i, v in enumerate(noun):
        if len(v) < 2:
            noun.pop(i)

    count = Counter(noun)
    noun_list = count.most_common(100)
    return noun_list

