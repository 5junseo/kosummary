import pytchat
import pafy
import time
from konlpy.tag import Okt

import config
from Sentiment import predict_pos_neg
from database import dbModule
from frequency import emoticon_del
from frequency import noun_counters
from frequency import morph_counters

okt = Okt()
api_key = config.key


def DB_counters_send(text):
    x = morph_counters(text)
    print(x)
    for i in range(len(x)):
        print(x[i][0])
        print(x[i][1])


def Get_Api(key):
    pafy.set_api_key(api_key)

    v_id = key

    chat = pytchat.create(video_id=key)
    while chat.is_alive():
        try:
            data = chat.get()
            items = data.items
            for c in items:
                # print(f"{c.datetime} [{c.author.name}]- {c.message}")
                # print(morph_counters(c.message))

                x = noun_counters(c.message)

                for i in range(len(x)):
                    db_class = dbModule.Database()
                    sql = "INSERT INTO summary.chatting(videoid, reaction_score, word, word_count) \
                                           VALUES('%s', '%s', '%s', '%s')" % \
                          (v_id, predict_pos_neg(c.message), x[i][0], x[i][1])
                    db_class.execute(sql)
                    db_class.commit()

                data.tick()
                time.sleep(0.05)
        except KeyboardInterrupt:
            chat.terminate()
            break


Get_Api("py_phbQxy5Y")
