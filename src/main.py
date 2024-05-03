from flask import (
    Flask,
    render_template,
    request,
    make_response,
    url_for,
    redirect,
    jsonify
)
from flask_socketio import SocketIO, emit
from threading import Thread
import json, time, random

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
        users[p]["tot_stocks"] = 0
        users[p]["password"] = str(random.randint(0, 9999)).zfill(4)
        print(f"Name: {p}, PIN: {users[p]['password']}")
        for i in cfg["people"]:
            users[p]["stocks"][i] = 0
            stock_prices[i] = 1
        # print(p, users[p])


app = Flask(__name__, static_url_path="/static")
sock = SocketIO(app)

def bet(better, activity, target, time):
    # TODO: Verify user can afford the bet
    # TODO: Calculate expiration time
    # TODO: Register bet
    # TODO: Emit info to clients
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
            stock_prices=stock_prices
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

@app.get("/api/players/money")
def getPlayerMoney():
    return jsonify(playerMoney())


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

    # Recevies -1 when buying maximum amount
    if amount == -1:
        amount = int(users[buyer]["money"] / stockPrice(name))

    # Calculate total price
    tot_price = round(amount * stockPrice(name), 2)

    # Check if user has enough money to proceed
    if users[buyer]["money"] > tot_price:
        print(f"{buyer} bought {amount} stocks in {name}")

        # Add the stock and subtract the money
        users[buyer]["stocks"][name] += amount
        users[buyer]["tot_stocks"] += amount
        users[buyer]["money"] -= tot_price

        # Update stock price
        upPrice(name, amount)

        # Update interface
        sock.emit("bought", {"name": buyer, "new": users[buyer]["stocks"][name], "amount": amount, "stock": name})
        sock.emit("update", {"type": "player", "name": buyer, "money": users[buyer]["money"], "tot_stocks": users[buyer]["tot_stocks"], "stock": users[buyer]["stocks"][name], "who": name, "price": stockPrice(name)})
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

    # Check if user has stocks
    if users[seller]["stocks"][name]:

        # Receives -1 when selling all stocks
        # setting amount to amount owned
        if amount == -1:
            amount = users[seller]["stocks"][name]

        print(f"{seller} sold {amount} stocks in {name}")

        # Remove the stocks and add the money
        users[seller]["stocks"][name] -= amount
        users[seller]["tot_stocks"] -= amount
        users[seller]["money"] += round(amount * stockPrice(name), 2)

        # Adjust stock price
        downPrice(name, amount)

        # Update interface
        sock.emit("sold", {"name": seller, "new": users[seller]["stocks"][name], "amount": amount, "stock": name})
        sock.emit("update", {"type": "player", "name": seller, "money": users[seller]["money"], "tot_stocks": users[seller]["tot_stocks"], "stock": users[seller]["stocks"][name], "who": name, "price": stockPrice(name)})
    else:
        pass
        # TODO: alert player they don't own the stock
    # TODO: Add to running log
    # TODO: Send update to all players
    return redirect("/")


@app.get("/activity/<activity>")
def activity(activity=None):
    return render_template("activity.html", activity=activities[activity])


@app.post("/activity/<activity>/bet")
def getBet(activity=None):
    amount = request.json["amount"]
    player = request.json["player"]
    time = request.json["time"]
    better = request.cookies.get("name")
    bet(better, activity, player, time)
    sock.emit("bet", {"name": better, "activity": activity, "amount": amount, "player": player})
    return redirect("/")


@app.get("/admin")
def adminMenu(name=None):
    name = request.cookies.get("name")
    if name in admins:
        return render_template("admin.html", users=users, activities=activities)
    return redirect("/")


@sock.on("connect")
def handleConnect():
    print("Client connected")
    emit("bet", {"data": "test"})

class looping(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running:
            print("Emitting")
            try:
                sock.emit("history", {"data": playerMoney()})
            except:
                return
            time.sleep(60)

    def stop(self):
        print("Stopping loop")
        self.running = False

def playerMoney():
    return [{"name": u, "money": users[u]["money"]} for u in users]


def validateLogin(name, password):
    """Validate login information"""
    if name in users:
        if users[name]["password"] == password:
            return True
    return False


if __name__ == '__main__':
    loop = looping()
    #loop.start()
    app.run(host="0.0.0.0", debug=True)
    #loop.stop()
    
    
