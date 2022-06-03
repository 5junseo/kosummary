from flask import Flask, render_template, make_response, request, redirect
import json
from time import time
from random import random
import os
import requests
import config
import pymysql
from datetime import datetime
from googleapiclient.discovery import build

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
    #     # for i in range(len(datas)):
    #     #   print(datas[i][0])

    results = [[datas[0][0], datas[0][1]], [datas[1][0], datas[1][1]], [datas[2][0], datas[2][1]], [datas[3][0], datas[3][1]], [datas[4][0], datas[4][1]]]
    # results.sort(key=lambda x: x[1], reverse=True)
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

    # print(int(avg_reaction))

    results = [int(avg_reaction), 100 - int(avg_reaction)]  # [긍정 비율, 부정 비율]
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    return response


@app.route("/")
def hello():
    return render_template('index.html')


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
    cur.execute(sql, video_id)
    chat_num = cur.fetchall()

    # print(chat_num[0][0])
    conn.commit()

    # 현재 시청자 수
    viewers = search_response['items'][0]['liveStreamingDetails']['concurrentViewers']

    # 누적 시청자 수
    viewers_accumulate = search_response['items'][0]['statistics']['viewCount']

    # 방송 제목
    streaming_title = search_response['items'][0]['snippet']['title']

    # 구독자 수
    channel_id = search_response['items'][0]['snippet']['channelId']

    channel_response = youtube.channels().list(
        part='id, snippet, statistics',
        id=channel_id
    ).execute()

    subscriber = channel_response['items'][0]['statistics']['subscriberCount']

    # 좋아요 수
    like_count = search_response['items'][0]['statistics']['likeCount']

    # 실시간 방송 썸네일
    thumbnail = search_response['items'][0]['snippet']['thumbnails']['medium']['url']

    # 방송 런타임
    start_time = search_response['items'][0]['liveStreamingDetails']['actualStartTime']
    now = datetime.now()
    past = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    diff = now - past
    daysH = diff.days * 24
    hour = int(diff.seconds / 3600)
    min = int(diff.seconds / 60) - hour * 60
    sec = int(diff.seconds % 60)
    runtime = "%d 시간 %d 분 %d 초" % (hour + daysH, min, sec)

    # 실시간 방송 차트 시간
    now = datetime.now()
    now_time = now.strftime('%H:%M:%S')
    viewers_chart = [float(int(now_time[3:5])) + int(now_time[6:8]) * 0.01, int(viewers)]

    results = [chat_num[0][0], runtime, viewers, viewers_accumulate, streaming_title, subscriber, like_count, thumbnail, viewers_chart]

    response = make_response(json.dumps(results, ensure_ascii=False))
    response.content_type = 'application/json'
    return response


@app.route('/search', methods=['GET', 'POST'])
def index():
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    key = config.key

    videos = []

    if request.method == 'POST':
        search_params = {
            'key': key,
            'q': request.form.get('query'),
            'part': 'snippet',
            'maxResults': 9,
            'type': 'video',
            'eventType': 'live',
            'regionCode': 'KR'
        }

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'key': key,
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
            }
            videos.append(video_data)

    return render_template('index1.html', videos=videos)


if __name__ == "__main__":
    # app.run(port=5000, debug=False)
    app.run(host='127.0.0.1', port=5000, debug=True)
