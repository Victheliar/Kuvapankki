import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, make_response, abort
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import db
import config
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_images = items.get_images()
    all_items = items.get_items()
    return render_template("index.html", images = all_images, items = all_items)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    posts = users.get_posts(user_id)
    return render_template("user.html", user = user, posts = posts)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("find_item.html", query = query, results = results)

@app.route("/add_image", methods = ["POST"])
def add_image():
    require_login()
    file = request.files["image"]
    if not file.filename.endswith(".png"):
        return "VIRHE: väärä tiedostomuoto"
    image = file.read()
    user_id = session["user_id"]
    description = request.form["description"]
    if len(description) > 5000 or not image:
        abort(403)
    if not description:
        description = ""
    if len(image) > 5000*5000:
        return "VIRHE: liian suuri kuva"
    items.add_item(user_id, image, description)
    return redirect("/")

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_item.html", item = item)

@app.route("/update_item", methods = ["POST"])
def update_item():
    file = request.files["image"]
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    description = request.form["description"]
    if not file.filename.endswith(".png"):
        return "VIRHE: väärä tiedostomuoto"
    image = file.read()
    if len(description) > 5000 or not image:
        abort(403)
    if not description:
        description = ""
    if len(image) > 1024*1024:
        return "VIRHE: liian suuri kuva"
    items.update_item(item_id, image, description)
    return redirect("/item/" + str(item_id))

@app.route("/remove_item/<int:item_id>", methods = ["GET","POST"])
def remove_item(item_id):

    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_item.html", item = item)

    if request.method == "POST":
        if "remove" in request.form:
            items.remove_item(item_id)
            return redirect("/")
        else:
            return redirect("/item/" + str(item_id))

@app.route("/image/<int:item_id>")
def show_image(item_id):
    image = items.get_image(item_id)
    if not image:
        abort(404)
    response = make_response(image)
    response.headers.set("Content-Type","image/png")
    return response

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    return render_template("show_item.html", item = item)

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

def require_login():
    if "user_id" not in session:
        abort(403)