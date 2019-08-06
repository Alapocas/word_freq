from requests import put, get, post
from flask import Flask, request, jsonify, redirect, url_for, request, render_template
from flask_restful import reqparse, abort, Api, Resource
from flask_restful.representations.json import output_json
from flask_cors import CORS

import os, json,threading, pickle, fcntl
from load import diction
from key import PATH, DBS

app = Flask(__name__)
CORS(app, resources=r'/*')

app.config['RESTFUL_JSON'] = {"ensure_ascii": False, "indent": None, "sort_keys": False}
app.config["DEFAULT_REPRESENTATIONS"] = [("application/json; charset=utf-8;", output_json)]
api = Api(app)

class Reload(Resource):
    def get(self):
        global diction
        diction = pickle.load(open(PATH, "rb"))

class Ask_freq(Resource):
    def get(self):
        global diction
        r = {"code": 500, "data": ""}
        js = {"source": request.args.get("source"), "id": request.args.get("id"), "method": request.args.get("method")}
        if js["source"] not in DBS.keys():
            r["data"] = "Invalid database request!"
        elif js["id"] not in diction[js["source"]].keys() or js["method"] not in ["name", "memo"]:
            r["data"] = "Invalid company id or command!"
        else:
            r["code"] = 200
            r["data"] = diction[js["source"]][js["id"]][js["method"]]
        return r

api.add_resource(Ask_freq, "/frequency")
api.add_resource(Reload, "/reload")

@app.route("/ask", methods = ["GET", "POST"])
def ask():
    result = ""
    if request.method == "POST":
        req = {"id": str(request.form["id"]), "method": str(request.form["method"])}
        result = post('http://localhost:5000/frequency?id={}&method={}'.format(req["id"], req["method"])).json()
        return render_template("./ask.html", freq = result)
    return render_template("./ask.html", freq = result)

def test():
    req = {"id": "133", "method": "memo"}
    result = get('http://localhost:5000/frequency?id=133&method=memo').json()
    print(result)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000,  debug=True)