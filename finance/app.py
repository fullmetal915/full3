import os
import datetime


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])[0]['cash']
    portfolios = db.execute("SELECT * FROM portfolio WHERE user_id = :id", id=session["user_id"])
    if not portfolios:
        return apology("Sorry you have no holding")
    grand_total = cash
    for portfolio in portfolios:
        cas = lookup(portfolio["symbol"])['price']
        total = int(portfolio["quantity"]) * cas
        portfolio.update({'price': cas, 'total': total})
        grand_total += total
    return render_template("index.html", portfolios=portfolios, cashs=cash, total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # defining symbol
        symbol = request.form.get("symbol")

        # Validating symbol
        if not symbol:
            return apology("Enter Symbol", 403)

        info = lookup(symbol)
        if info == None:
            return apology("must provide a valid symbol :}", 403)

        #Validating share No.
        share = request.form.get("share")
        if not share:
            return apology("Enter Share", 403)

        if int(share) <= 0:
            return apology("can not buy negative share")

        #selecting cash from user table
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        #checking the validity of purchase
        net_purchase = info["price"] * int(share)

        if net_purchase > cash:
            return apology("Not enough cash", 403)

        #creating rows for table and updating cash
        date = datetime.datetime.now()
        db.execute("UPDATE users SET cash = cash - :net_purchase WHERE id = :id", net_purchase=net_purchase, id=session["user_id"])
        db.execute("INSERT INTO history (user_id, symbol, No_of_share, TOTAL_COST, TRANS_DATE, ACTION, NET_CASH) VALUES(:id, :symbol, :share, :net_purchase, :date, :action, :cash - :net_purchase)", id=session["user_id"], symbol=symbol, share=share, net_purchase=net_purchase, date=date, action="BOUGHT", cash=cash)

        checks = db.execute("SELECT symbol FROM portfolio where user_id = :id", id=session["user_id"])
        if not any(check["symbol"] == symbol for check in checks):
            db.execute("INSERT INTO portfolio (user_id, symbol, quantity) VALUES(?, ?, ?)", session["user_id"], symbol, share)
        else:
            db.execute("UPDATE portfolio SET quantity = quantity + :share WHERE symbol = :symbol AND user_id = :id", share=share, symbol=symbol, id=session["user_id"])
        return apology("U have purchased", 403)

    else:
        return render_template("buy.html")







@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    historyS = db.execute("SELECT symbol, No_of_share, ACTION, NET_CASH FROM history")
    return render_template("history.html", historys=historyS)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 403)


        info = lookup(symbol)
        if info == None:
            return apology("must provide a valid symbol :}", 403)


        return render_template("quoted.html", quote_dic=info)


    else:

        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        #req username and password and cash
        username = request.form.get("username")
        password = request.form.get("password")
        concur_password = request.form.get("concur_password")


        #checking validity of username
        if not username:
            return apology("must provide username", 403)


        username_list = db.execute("SELECT username FROM users")


        if username in username_list:
            return apology("username already exist", 403)


        #cheching validity of password
        if not password or not concur_password:
            return apology("must provide and concur password", 403)

        if password != concur_password:
            return apology("password doesn't match", 403)


        #hashing of password
        password_hash = generate_password_hash(password)


        #inserting into database and remembering user has logged in
        session["user_id"] = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)


        # Redirect user to home page
        return redirect("/")


    else:
        #form to register
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        #check forvalid symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 403)

        info = lookup(symbol)
        if info == None:
            return apology("INVALID SYMBOL", 403)

        historysymbols = db.execute("SELECT symbol FROM history")
        list = [historysymbol["symbol"] for historysymbol in historysymbols]
        if symbol not in list:
            return apology("U dont have it", 403)

        #check for number of stocks u want to sell
        no_of_share = request.form.get("no_of_share")
        if not no_of_share:
            return apology("must provide no_of_share", 403)

        sharetheyhave = db.execute("SELECT quantity FROM portfolio WHERE user_id = :id AND symbol = :symbol ", id=session["user_id"], symbol=symbol)[0]["quantity"]


        if int(no_of_share) > sharetheyhave or int(no_of_share) <= 0:
            return apology("u are not that rich -_-", 403)

        #calculating money
        moneymade = info["price"] * int(no_of_share)

        #checking the money which they already have
        moneytheyhave = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        #new money
        netmoneymade = moneymade + moneytheyhave[0]["cash"]

        # net share reduction

        #inserting new row with updated details
        date = datetime.datetime.now()
        db.execute("INSERT INTO history (user_id, symbol , No_of_share, TOTAL_COST, TRANS_DATE, ACTION, NET_CASH) VALUES(:id, :symbol, :share, :moneymade, :date, :action, :netmoneymade) ", id=session["user_id"], symbol=symbol, share=no_of_share, moneymade=moneymade, date=date, action="SOLD", netmoneymade=netmoneymade)
        db.execute("UPDATE users SET cash = cash + :moneymade WHERE id = :id", moneymade=moneymade, id=session["user_id"])
        db.execute("UPDATE portfolio SET quantity = quantity - :share WHERE user_id = :id", share=no_of_share, id=session["user_id"])
        return apology("SOLD", 303)

    else:
        portfolio = db.execute("SELECT symbol FROM portfolio")
        return render_template("sell.html",stocks=portfolio)


@app.route("/changepass", methords=["GET","POST])
@login_required
def changepass():
    if request.methord == "POST":
        oldpass = request.form.get("oldpass")

        if not oldpass:
            return apology("enter valid password")



