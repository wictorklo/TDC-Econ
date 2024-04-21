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
    if name in users.keys():
        return render_template("index.html", name=name)
    return render_template("index.html", name=f"{name} (Unknown user)")

@app.post("/login")
def login():
    print(request.form)
    if validateLogin(request.form["name"], request.form["code"]):
        resp = make_response(redirect("/"))
        resp.set_cookie("name", request.form["name"])
        return resp
    return redirect(url_for('static', filename='login.html'))

@app.get("/dashboard")
def overview():
    return render_template("overview.html")

@app.get("/person/<name>")
def person(name=None):
    #TODO: Check that user does not try to invest in themselves
    #Or leave it in as infinite money glitch?
    return render_template("player.html", user=users[name])

@app.post("/person/<name>/buy")
def invest(name=None):
        amount = request.form["amount"]
        return redirect("/")

@app.post("/person/<name>/sell")
def sell(name=None):
        amount = request.form["amount"]
        return redirect("/")

@app.get("/activity/<activity>")
def activity(activity=None):
    return render_template("activity.html", activity=activities[activity])

app.post("/activity/<activity>/bet")
def bet(activity=None):
     amount = request.form["amount"]
     player = request.form["player"]
     return redirect("/")

@app.get("/admin")
def adminMenu(name=None):
    name = request.cookies.get("name")
    if name in admins:
        return render_template("admin.html", user=users[name])
    return redirect("/")

def validateLogin(name, password):
    #TODO: Add some basic logic here so people dont fuck each other over...
    return True