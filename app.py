import os

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///skinbuddy.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect("/routine")

    # Render home page
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    category = "info"
    checked = request.form.get("checktac")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            error = "must provide a username"
            flash( error, category)

        # Ensure full name was submitted
        elif not request.form.get("name"):
            error = "must provide a name"
            flash( error, category)

        # Ensure email is submitted
        elif not request.form.get("email"):
            error = "Must provide an email"
            flash( error, category)

        elif not "@" in request.form.get("email"):
            error = "Must provide a valid email"
            flash( error, category)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            flash( error, category)

        elif len(request.form.get("password")) < 4 or request.form.get("password").lower() == request.form.get("password") or request.form.get("password").upper() == request.form.get("password") or request.form.get("password").isalnum() or not any(i.isdigit() for i in request.form.get("password")):
            error = "Password should contain: at least 4 characters, 1 digit or more, 1 symbol or more, 1 uppercase letter or more, 1 lowercase letter or more."
            flash( error, category)

        # Ensure password confirmation was submitted
        elif not request.form.get("password"):
            error = "Must confirm password"
            flash( error, category)

        # Ensure password matches with confirmation of password
        elif request.form.get("password") != request.form.get("confirmation"):
            error = "Passwords don't match"
            flash( error, category)

        # Ensure Terms and Conditions are checked
        elif checked == None:
            error = "You must accept Terms of Service"
            flash( error, category)

        # Ensure username doesn't exists
        elif len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) != 0 or len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").upper())) != 0:
            error = "Username exists, try a different username"
            flash( error, category)

        # Ensure email doesn't exists
        elif len(db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))) != 0 or len(db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email").upper())) != 0:
            error = "Email exists"
            flash( error, category)

        else:

            # Save it to Database
            db.execute("INSERT INTO users (username, name, email, hash) VALUES (?, ?, ?, ?)", request.form.get(
                "username").upper(), request.form.get("name"), request.form.get("email").upper(), generate_password_hash(request.form.get("password")))

            # Remember which user has logged in
            session["user_id"] = db.execute(
                "SELECT * FROM users WHERE email = ?", request.form.get("email").upper())[0]["id"]

            return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    error = None
    category = "info"

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            error = "Must provide an email"
            flash( error, category)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "must provide password"
            flash( error, category)

        # Ensure email exists and password is correct
        elif len(db.execute("SELECT * FROM users WHERE email = ?",
                            request.form.get("email").upper())) != 1 or not check_password_hash(db.execute("SELECT * FROM users WHERE email = ?",
                                                                                                           request.form.get("email").upper())[0]["hash"], request.form.get("password")):
            error = "invalid username and/or password"
            flash( error, category)

        else:

            rows = db.execute("SELECT * FROM users WHERE email = ?",
                              request.form.get("email").upper())

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/routine")
@login_required
def routine():

    morning = "Morning"
    night = "Night"
    state = "Active"

    mhistory = db.execute(
        "SELECT history.user_id, history.product_id AS p_id, brand, name, fullname, ingredients, history.routine, history.state, history.rating FROM history INNER JOIN products ON history.product_id = products.p_id WHERE history.user_id = ? AND history.routine = ? AND state = ?", session["user_id"], morning, state)

    nhistory = db.execute(
        "SELECT history.user_id, history.product_id AS p_id, brand, name, fullname, ingredients, history.routine, history.state, history.rating FROM history INNER JOIN products ON history.product_id = products.p_id WHERE history.user_id = ? AND history.routine = ? AND state = ?", session["user_id"], night, state)

    return render_template("routine.html", mhistory=mhistory, nhistory=nhistory)


@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    if q:
        products = db.execute(
            "SELECT * FROM products WHERE fullname LIKE ? LIMIT 10", "%" + q + "%")
    else:
        products = []

    return jsonify(products)


@app.route("/addMorning", methods=["GET", "POST"])
@login_required
def addMorning():

    routine = "Morning"
    status = "added to"

    if request.method == "POST":
        product = request.form.get("productListInput1")

        rows = db.execute(
            "SELECT * FROM products WHERE fullname = ?", product)

        product_id = rows[0]["p_id"]

        user_id = session["user_id"]

        time = datetime.now()

        ratings = db.execute(
            "SELECT * FROM history WHERE product_id = ? AND user_id = ?", product_id, user_id)

        currentList = db.execute(
            "SELECT * FROM history WHERE product_id = ? AND user_id = ? AND state = ? AND routine = ?", product_id, user_id, "Active", routine)

        if len(currentList) == 0:

            if len(ratings) == 0:

                rating = 0

                db.execute("INSERT INTO history (user_id, product_id, routine, status, state, rating, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       user_id, product_id, routine, status, "Active", rating, time)

            else:

                rating = ratings[0]["rating"]

                db.execute("INSERT INTO history (user_id, product_id, routine, status, state, rating, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       user_id, product_id, routine, status, "Active", rating, time)

            return redirect("/routine")

        else:
            flash("Product already exist in the routine!", "info")

            return redirect("/routine")

    return render_template("routine.html")



@app.route("/addNight", methods=["GET", "POST"])
@login_required
def addNight():

    routine = "Night"
    status = "added to"

    if request.method == "POST":
        product = request.form.get("productListInput2")

        rows = db.execute(
            "SELECT * FROM products WHERE fullname = ?", product)

        product_id = rows[0]["p_id"]

        user_id = session["user_id"]

        time = datetime.now()

        ratings = db.execute(
            "SELECT * FROM history WHERE product_id = ? AND user_id = ?", product_id, user_id)

        currentList = db.execute(
            "SELECT * FROM history WHERE product_id = ? AND user_id = ? AND state = ? AND routine = ?", product_id, user_id, "Active", routine)

        if len(currentList) == 0:


            if len(ratings) == 0:

                rating = 0

                db.execute("INSERT INTO  history (user_id, product_id, routine, status, state, rating, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       user_id, product_id, routine, status, "Active", rating, time)

            else:

                rating = ratings[0]["rating"]

                db.execute("INSERT INTO history (user_id, product_id, routine, status, state, rating, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       user_id, product_id, routine, status, "Active", rating, time)

            return redirect("/routine")

        else:

            flash("Product already exist in the routine!", "info")

            return redirect("/routine")

    return render_template("routine.html")

@app.route("/removeMorning", methods=["GET", "POST"])
@login_required
def removeMorning():

    routine = "Morning"
    status = "removed from"

    if request.method == "POST":

        product_id = request.form.get("id")

        user_id = session["user_id"]

        rating = request.form.get("ratingValue")

        time = datetime.now()

        db.execute("INSERT INTO history (user_id, product_id, routine, status, state, rating, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_id, product_id, routine, status, "Deleted", rating, time)

        db.execute("UPDATE history SET state = ? WHERE product_id = ? AND user_id = ? AND routine = ?",
                   "Deleted", product_id, user_id, routine)

        return redirect("/routine")

    return render_template("routine.html")


@app.route("/removeNight", methods=["GET", "POST"])
@login_required
def removeNight():

    routine = "Night"
    status = "removed from"

    if request.method == "POST":

        product_id = request.form.get("id")

        user_id = session["user_id"]

        rating = request.form.get("ratingValue")

        time = datetime.now()

        db.execute("INSERT INTO history (user_id, product_id, routine, status, state, rating, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_id, product_id, routine, status, "Deleted", rating, time)

        db.execute("UPDATE history SET state = ? WHERE product_id = ? AND user_id = ? AND routine = ?",
                   "Deleted", product_id, user_id, routine)

        return redirect("/routine")

    return render_template("routine.html")


@app.route("/history")
@login_required
def history():

    user_id = session["user_id"]

    products = db.execute("SELECT history.product_id, history.user_id, history.routine, history.status, history.time, history.rating, brand, name FROM history INNER JOIN products ON p_id = history.product_id WHERE history.user_id = ? ORDER BY history.time ASC;", user_id)

    return render_template("history.html", products=products)


@app.route("/rateMorning", methods=["GET", "POST"])
@login_required
def rateMorning():

    routine = "Morning"

    if request.method == "POST":

        rating = request.form.get("rating")

        product_id = request.form.get("id")

        user_id = session["user_id"]

        db.execute("UPDATE history SET rating = ? WHERE product_id = ? AND user_id = ? AND routine = ?",
                   rating, product_id, user_id, routine)

        return redirect("/routine")

    return render_template("routine.html")


@app.route("/rateNight", methods=["GET", "POST"])
@login_required
def rateNight():

    routine = "Night"

    if request.method == "POST":

        rating = request.form.get("rating")

        product_id = request.form.get("id")

        user_id = session["user_id"]

        db.execute("UPDATE history SET rating = ? WHERE product_id = ? AND user_id = ? AND routine = ?",
                   rating, product_id, user_id, routine)

        return redirect("/routine")

    return render_template("routine.html")

if __name__ == "__main__":
    app.run(debug=True)