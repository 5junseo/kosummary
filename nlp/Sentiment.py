from keras.models import load_model
import numpy as np
from konlpy.tag import Okt
import nltk
import json
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

okt = Okt()


def read_data(filename):
    with open(filename, 'r', encoding='UTF8') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        # txt 파일의 헤더(id document label)는 제외하기
        data = data[1:]
    return data


train_data = read_data('ratings_train.txt')
test_data = read_data('ratings_test.txt')


def tokenize(doc):
    # norm은 정규화, stem은 근어로 표시하기를 나타냄
    return ['/'.join(t) for t in okt.pos(doc, norm=True, stem=True)]


if os.path.isfile('train_docs.json'):
    with open('train_docs.json', 'rt', encoding='UTF8') as f:
        train_docs = json.load(f)
    with open('test_docs.json', 'rt', encoding='UTF8') as f:
        test_docs = json.load(f)
else:
    train_docs = [(tokenize(row[1]), row[2]) for row in train_data]
    test_docs = [(tokenize(row[1]), row[2]) for row in test_data]
    # JSON 파일로 저장
    with open('train_docs.json', 'w', encoding="utf-8") as make_file:
        json.dump(train_docs, make_file, ensure_ascii=False, indent="\t")
    with open('test_docs.json', 'w', encoding="utf-8") as make_file:
        json.dump(test_docs, make_file, ensure_ascii=False, indent="\t")


def term_frequency(doc, selected_words):
    return [doc.count(word) for word in selected_words]


def predict_pos_neg(review):
    token = tokenize(review)
    tokens = [t for d in train_docs for t in d[0]]
    text = nltk.Text(tokens, name='NMSC')
    selected_words = [f[0] for f in text.vocab().most_common(10000)]
    tf = term_frequency(token, selected_words)

    model = load_model('korean_nlp_v2.h5')
    data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)
    score = float(model.predict(data))
    if score > 0.6:
        print("[{}]는 {:.2f}% 긍정 추측^_^\n".format(review, score * 100))
    elif (score <= 0.6 and score >= 0.4):
        print("[{}]는 {:.2f}% 중립 추측-_-\n".format(review, score * 100))
    else:
        print("[{}]는 {:.2f}% 부정 추측ㅠ_ㅠ;\n".format(review, (1 - score) * 100))

    return score * 100
