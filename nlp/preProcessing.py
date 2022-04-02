from keras.models import load_model
import numpy as np
from konlpy.tag import Okt

import json
import os
import nltk


def read_data(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        data = data[1:]
    return data

def tokenize(doc):
    okt = Okt()
    return ['/'.join(t) for t in okt.pos(doc, norm=True, stem=True)]

def term_frequency(doc, selected_words):
    return [doc.count(word) for word in selected_words]


def predict_pos_neg(review, train_docs, test_docs):


    tokens = [t for d in train_docs for t in d[0]]

    text = nltk.Text(tokens, name='NMSC')

    selected_words = [f[0] for f in text.vocab().most_common(1000)]


    model = load_model('korean_nlp.h5')

    token = tokenize(review)
    tf = term_frequency(token, selected_words)
    data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)
    score = float(model.predict(data))
    if(score > 0.5):
        print("[{}]는 {:.2f}% 확률로 긍정 리뷰이지 않을까 추측해봅니다.^^\n".format(review, score * 100))
    else:
        print("[{}]는 {:.2f}% 확률로 부정 리뷰이지 않을까 추측해봅니다.^^;\n".format(review, (1 - score) * 100))
