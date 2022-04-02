from flask import Flask, render_template, make_response, request, Response, jsonify, current_app, redirect
import json
from time import time
from random import random
import os

import requests

from db import dbModule

app = Flask(__name__)  # Flask 객체 선언
app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지


# Front로부터 json 파일 요청 처리
@app.route('/live-data')
def live_data():
    # DB에서 데이터 받아와 results에 저장
    results = [time() * 1000, random() * 100]
    response = make_response(json.dumps(results))
    response.content_type = 'application/json'
    return response


@app.route("/")
def hello():
    print(os.path.dirname(__file__))
    return render_template('index.html')


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
            # print(video_data)

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
