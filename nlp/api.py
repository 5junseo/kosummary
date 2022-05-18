import pytchat
import pafy
import time
from konlpy.tag import Okt
from Sentiment import predict_pos_neg
from database import dbModule
from frequency import emoticon_del
from frequency import noun_counters
from frequency import morph_counters

okt = Okt()


def Get_Api(key):
    pafy.set_api_key('AIzaSyCzJGbHRKjQTMtOfVlxBMslPehk5qXHlQ0')

    v_id = key
    # v = pafy.new(key)
    # title = v.title
    # author = v.author
    # published = v.published

    chat = pytchat.create(video_id=key)
    while chat.is_alive():
        try:
            data = chat.get()
            items = data.items
            for c in items:
                print(f"{c.datetime} [{c.author.name}]- {c.message}")
                print(noun_counters(c.message))
                print(morph_counters(c.message))
                predict_pos_neg(c.message)

                db_class = dbModule.Database()
                sql = "INSERT INTO summary.chatting(videoid, name, reaction_score) \
                       VALUES('%s', '%s', '%s')" % \
                      (v_id, c.author.name, predict_pos_neg(c.message))
                db_class.execute(sql)
                db_class.commit()

                data.tick()
                time.sleep(0.05)
        except KeyboardInterrupt:
            chat.terminate()
            break


Get_Api("py_phbQxy5Y")
