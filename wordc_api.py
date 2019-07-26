from requests import put, get, post
from flask import Flask, request, jsonify, redirect, url_for, request, render_template
from flask_restful import reqparse, abort, Api, Resource
import json
from load import diction

app = Flask(__name__)
api = Api(app)

class Ask_freq(Resource):
    def post(self):
        js = json.loads(request.form["req"])
        if js["id"] not in diction.keys() or js["method"] not in ["name", "memo"]:
            return "Invalid company id or command!"
        print(json.dumps(diction[js["id"]][js["method"]], ensure_ascii=False))
        return json.dumps(diction[js["id"]][js["method"]], ensure_ascii=False)

api.add_resource(Ask_freq, "/frequency")

@app.route("/ask", methods = ["GET", "POST"])
def ask():
    result = ""
    if request.method == "POST":
        req = {"id": str(request.form["id"]), "method": str(request.form["method"])}
        result = post('http://localhost:5000/frequency', data={'req': json.dumps(req)}).json()
        return render_template("ask.html", freq = result)
    return render_template("ask.html", freq = result)

def test():
    req = {"id": "133", "method": "memo"}
    result = post('http://localhost:5000/frequency', data={'req': json.dumps(req)}).json()
    print(result)

if __name__ == '__main__':
    app.run(debug=True)
