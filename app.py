from flask import Flask, render_template, make_response, request, redirect
import json
from time import time
import os
import requests
import config

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database import dbModule

app = Flask(__name__)  # Flask 객체 선언
app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지


# YouTube API Build
DEVELOPER_KEY = config.key
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


# 시청자 수 그래프
@app.route('/live-data')
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


@app.route("/")
def hello():
    print(os.path.dirname(__file__))
    return render_template('index.html')


# 시청자 수, 방송 시간 return
@app.route("/summary/<video_id>", methods=['GET'])
def summary(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.videos().list(
        part="id, snippet, liveStreamingDetails",
        id=video_id
    ).execute()

    viewers = search_response['items'][0]['liveStreamingDetails']['concurrentViewers']
    start_time = search_response['items'][0]['liveStreamingDetails']['actualStartTime']

    results = [viewers, start_time]
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    return response


@app.route("/test/<video_id>", methods=['GET'])
def testSelect(video_id):
    db_class = dbModule.Database()
    sql = "SELECT title, url FROM summary.search WHERE videoid=%s"
    #db_class.execute(sql, video_id)
    #db_class.commit()

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

            db_class = dbModule.Database()
            sql = "INSERT INTO summary.search(videoid, url, thumbnail, title, viewer, starttime) \
                                            VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % \
                  (video_data["id"], video_data["url"], video_data["thumbnail"], video_data["title"],
                   video_data["viewer"], video_data["startTime"])
            db_class.execute(sql)
            db_class.commit()

    return render_template('index1.html', videos=videos)


if __name__ == "__main__":
    # app.run(port=5000, debug=False)
    app.run(host='127.0.0.1', port=5000, debug=True)
