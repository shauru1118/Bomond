import flask
import flask_cors

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route("/")
def root():
    return flask.jsonify({
        "status":"ok",
        "message":"no homework",
    })


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
