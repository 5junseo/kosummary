from flask import Flask, render_template, make_response
import json
from time import time
from random import random
import os

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


if __name__ == "__main__":
    #app.run(port=5000, debug=False)
    app.run(host='127.0.0.1', port=5000, debug=True)

