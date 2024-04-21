from flask import Flask, render_template, request, make_response, url_for, redirect
import json


activities = {}
users = {}
admins = []

with open("config.json", "r") as file:
    cfg = json.load(file)
    file.close()
    print(cfg)
    activities = cfg["activities"]
    admins = cfg["admins"]
    for p in cfg["people"]:
        users[p] = {}
        users[p]["money"] = cfg["start_cash"]
        users[p]["bets"] = []
        users[p]["investments"] = []
        print(p, users[p])



app = Flask(__name__, static_url_path='/static')



@app.route("/")
def index():
    name = request.cookies.get("name")
    print(name, name == None)
    if name == None:
        return redirect(url_for('static', filename='login.html'))
    return render_template("index.html", name=name)

@app.post("/login")
def login():
    print(request.form)
    if validateLogin(request.form["name"], request.form["code"]):
        resp = make_response(redirect("/"))
        resp.set_cookie("name", request.form["name"])
        return resp
    return redirect(url_for('static', filename='login.html'))


def validateLogin(name, password):
    #TODO: Add some basic logic here so people dont fuck each other over...
    return True