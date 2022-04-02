import pytchat
import pafy
import time
from processing import noun_counters
from preProcessing import predict_pos_neg
import json
import os

os.chdir(os.path.dirname(__file__))

def Get_Api(key):
    with open('train_docs.json', encoding="utf-8") as f:
        train_docs = json.load(f)
    with open('test_docs.json', encoding="utf-8") as f:
        test_docs = json.load(f)

    pafy.set_api_key('AIzaSyCzJGbHRKjQTMtOfVlxBMslPehk5qXHlQ0')

    v = pafy.new(key)
    title = v.title
    author = v.author
    published = v.published

    print(title)
    print(author)
    print(published)

    chat = pytchat.create(video_id = key)
    while chat.is_alive():
        try:
            data = chat.get()
            items = data.items
            for c in items:
                print(f"{c.datetime} [{c.author.name}]- {c.message}")
                print(noun_counters(c.message))
                predict_pos_neg(c.message, train_docs, test_docs)

                # DB insert
                data.tick()

                time.sleep(0.05)

        except KeyboardInterrupt:
            chat.terminate()
            break




Get_Api("GoXPbGQl-uQ")
