import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import db
import config
import items

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    # all_items = items.get_items()
    return render_template("index.html")

@app.route("/item/<int:item_id>")
def show_item(item_id):
    # item = items.get_item(item_id)
    return render_template("show_item.html")

@app.route("/new_item")
def new_item():
    return render_template("new_item.html")

@app.route("/create_item", methods = ["GET", "POST"])
def create_item():
    if request.method == "GET":
        return render_template("new_item.html")
    
    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".png"):
            return "VIRHE: väärä tiedostomuoto"
        image = file.read()
        description = request.form["description"]
        category = request.form["category"]
        user_id = session["user_id"]
        items.add_item(description, user_id, image, category)
        return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods = ["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM Users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")