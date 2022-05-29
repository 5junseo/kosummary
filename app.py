from flask import Flask, render_template, make_response, request, redirect
import json
from time import time
from random import random
import os
import requests
import config
import pymysql

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database import dbModule

app = Flask(__name__)  # Flask 객체 선언
app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지

# YouTube API Build
DEVELOPER_KEY = config.key
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

conn = pymysql.connect(host='localhost', user='root', password=config.db_password, charset='utf8mb4')
cursor = conn.cursor()

conn1 = pymysql.connect(host='localhost', user='root', password=config.db_password, charset='utf8mb4')


# 단어 빈도수
@app.route('/live-words')
def live_words():
    cur1 = conn1.cursor()

    # 상위 5개 단어
    sql = "SELECT word, COUNT(word) FROM summary.chatting WHERE videoid=%s GROUP BY word HAVING COUNT(word) > 1 ORDER BY count(word) DESC"
    cur1.execute(sql, "py_phbQxy5Y")
    datas = cur1.fetchmany(5)
    conn1.commit()

    # print(datas)
    # for i in range(len(datas)):
    #   print(datas[i][0])

    results = [[datas[0][0], datas[0][1]], [datas[1][0], datas[1][1]], [datas[2][0], datas[2][1]], [datas[3][0], datas[3][1]], [datas[4][0], datas[4][1]]]
    # results.sort(key=lambda x: x[1], reverse=True)
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'

    return response


# 시청자 수 그래프
@app.route('/live-viewers')
def live_data():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(
        part="id, snippet, liveStreamingDetails",
        id="py_phbQxy5Y"
    ).execute()

    viewers = search_response['items'][0]['liveStreamingDetails']['concurrentViewers']

    results = [time() * 1000, int(viewers)]
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    return response


# 감정 분석 그래프
@app.route('/live-segment')
def live_segment():
    cur = conn.cursor()

    # 5분전 반응 조회
    sql = "SELECT reaction_score FROM summary.chatting WHERE videoid=%s AND created_at > date_add(now(), interval -5 minute)"
    cur.execute(sql, "py_phbQxy5Y")
    datas = cur.fetchall()
    conn.commit()

    num = 0
    for i in range(len(datas)):
        num += datas[i][0]

    try:
        avg_reaction = num / len(datas)
    except ZeroDivisionError:
        avg_reaction = 50

    print(int(avg_reaction))

    results = [int(avg_reaction), 100 - int(avg_reaction)]  # [긍정 비율, 부정 비율]
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    return response


@app.route("/")
def hello():
    return render_template('index.html')


# 채팅 수, 시청자 수, 방송 시간, 좋아요 수 return
@app.route("/summary/<video_id>", methods=['GET'])
def summary(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(
        part="id, snippet, liveStreamingDetails, statistics",
        id=video_id
    ).execute()

    cur = conn.cursor()

    # 채팅 수
    sql = "SELECT COUNT(id) FROM summary.chatting WHERE videoid = %s"
    cur.execute(sql, "py_phbQxy5Y")
    chat_num = cur.fetchall()

    # print(chat_num[0][0])

    conn.commit()

    viewers = search_response['items'][0]['liveStreamingDetails']['concurrentViewers']
    start_time = search_response['items'][0]['liveStreamingDetails']['actualStartTime']
    like_count = search_response['items'][0]['statistics']['likeCount']

    results = [chat_num[0][0], viewers, start_time, like_count]

    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    return response


@app.route("/test/<video_id>", methods=['GET'])
def testSelect(video_id):
    db_class = dbModule.Database()
    sql = "SELECT title, url FROM summary.search WHERE videoid=%s"

    data = db_class.executeAll(sql, video_id)
    db_class.commit()

    return str(data)


@app.route('/search', methods=['GET', 'POST'])
def index():
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    videos = []

    if request.method == 'POST':
        search_params = {
            'key': 'AIzaSyCzJGbHRKjQTMtOfVlxBMslPehk5qXHlQ0',
            'q': request.form.get('query'),
            'part': 'snippet',
            'maxResults': 9,
            'type': 'video',
            'eventType': 'live',
            # 'order' : 'title',  viewCount
            'regionCode': 'KR'
        }

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'key': 'AIzaSyCzJGbHRKjQTMtOfVlxBMslPehk5qXHlQ0',
            'id': ','.join(video_ids),
            'part': 'id,snippet,liveStreamingDetails',
            'maxResults': 9
        }

        r = requests.get(video_url, params=video_params)
        results = r.json()['items']
        for result in results:
            video_data = {
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'thumbnail': result['snippet']['thumbnails']['high']['url'],
                'title': result['snippet']['title'],
                'startTime': result['liveStreamingDetails']['actualStartTime'],
                'viewer': result['liveStreamingDetails']['concurrentViewers']

            }
            videos.append(video_data)

            # db_class = dbModule.Database()
            # sql = "INSERT INTO summary.search(videoid, url, thumbnail, title, viewer, starttime) \
            #                                VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % \
            #      (video_data["id"], video_data["url"], video_data["thumbnail"], video_data["title"],
            #       video_data["viewer"], video_data["startTime"])
            # db_class.execute(sql)
            # db_class.commit()

    return render_template('index1.html', videos=videos)


if __name__ == "__main__":
    # app.run(port=5000, debug=False)
    app.run(host='127.0.0.1', port=5000, debug=True)
