from flask import (
    Flask,
    render_template,
    request,
    make_response,
    url_for,
    redirect,
    jsonify,
)
import json

# https://marketsplash.com/how-to-use-flask-with-websockets/

price_constant = 0.02

activities = {}
users = {}
admins = []
log = []
stock_prices = {}

with open("config.json", "r") as file:
    cfg = json.load(file)
    file.close()
    print(cfg)
    activities = cfg["activities"]
    admins = cfg["admins"]
    for i, p in enumerate(cfg["people"]):
        users[p] = {}
        users[p]["money"] = cfg["start_cash"]
        users[p]["bets"] = []
        users[p]["stocks"] = {}
        users[p]["password"] = cfg["passwords"][i]
        for i in cfg["people"]:
            users[p]["stocks"][i] = 0
            stock_prices[i] = 1
        # print(p, users[p])


app = Flask(__name__, static_url_path="/static")


def bet(better, activity, target, time):
    pass


def stockPrice(name):
    return stock_prices[name]


def upPrice(name, amount=1):
    """Adjust the price of a stock upwards"""
    for _ in range(amount):
        stock_prices[name] = round(stock_prices[name] * (1 + price_constant), 4)
    print(name, "new price: ", stock_prices[name])


def downPrice(name, amount=1):
    """Adjust the price of a stock downwards"""
    for _ in range(amount):
        stock_prices[name] = round(stock_prices[name] / (1 + price_constant), 4)
    print(name, "new price: ", stock_prices[name])


@app.route("/")
def index():
    name = request.cookies.get("name")
    print(name, name == None)
    if name == None:
        return redirect(url_for("static", filename="login.html"))
    if name in users.keys():
        return render_template(
            "index.html",
            name=name,
            user=users[name],
            activities=activities,
            users=users,
        )
    return redirect(url_for("static", filename="login.html"))


@app.post("/login")
def login():
    print(request.form)
    if validateLogin(request.form["name"], request.form["code"]):
        print(True)
        resp = make_response(redirect("/"))
        resp.set_cookie("name", request.form["name"])
        return resp
    return redirect(url_for("static", filename="login.html"))


@app.get("/dashboard")
def overview():
    return render_template("overview.html")


@app.get("/person/<name>")
def person(name=None):
    # TODO: Check that user does not try to invest in themselves
    # Or leave it in as infinite money glitch?
    return render_template("player.html", user=users[name])


@app.post("/person/<name>/buy")
def invest(name=None):
    print(request.json)
    amount = request.json["amount"]
    buyer = request.cookies.get("name")
    tot_price = round(amount * stockPrice(name), 2)
    if users[buyer]["money"] > tot_price:
        print(f"{buyer} bought {amount} stocks in {name}")
        users[buyer]["stocks"][name] += amount
        users[buyer]["money"] -= tot_price
        upPrice(name, amount)
    else:
        pass
        # TODO: allert player they don't have enough money to buy
    # TODO: Add to running log
    # TODO: Send update to all players
    return redirect("/")


@app.post("/person/<name>/sell")
def sell(name=None):
    print(request.json)
    amount = request.json["amount"]
    seller = request.cookies.get("name")
    if users[seller]["stocks"][name]:
        print(f"{seller} sold {amount} stocks in {name}")
        users[seller]["stocks"][name] -= amount
        users[seller]["money"] += round(amount * stockPrice(name), 2)
        downPrice(name, amount)
    else:
        pass
        # TODO: allert player they don't own the stock
    # TODO: Add to running log
    # TODO: Send update to all players
    return redirect("/")


@app.get("/activity/<activity>")
def activity(activity=None):
    return render_template("activity.html", activity=activities[activity])


app.post("/activity/<activity>/bet")


def bet(activity=None):
    amount = request.form["amount"]
    player = request.form["player"]
    time = request.form["time"]
    better = request.cookies.get("name")
    # TODO: Add to running log
    # TODO: Send update to all players
    bet(better, activity, player, time)
    return redirect("/")


@app.get("/admin")
def adminMenu(name=None):
    name = request.cookies.get("name")
    if name in admins:
        return render_template("admin.html", user=users[name])
    return redirect("/")


def validateLogin(name, password):
    """Validate login information"""
    if name in users:
        if users[name]["password"] == password:
            return True
    return False
