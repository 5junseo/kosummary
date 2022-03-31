from flask import Flask

app = Flask(__name__)  # Flask 객체 선언
app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지


@app.route("/")
def hello():
    return "home"


@app.route("/test")
def test():
    return "<p>test<p>"


if __name__ == "__main__":
    #app.run(port=5000, debug=False)
    app.run(host='127.0.0.1', port=5000, debug=True)