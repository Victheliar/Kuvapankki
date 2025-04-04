import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, make_response, abort
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

@app.route("/add_profile_picture", methods=["GET", "POST"])
def add_profile_picture():
    require_login()

    if request.method == "GET":
        return render_template("add_profile_picture.html")

    if request.method == "POST":
        file = request.files["picture"]
        if not file.filename.endswith(".png"):
            return "VIRHE: väärä tiedostomuoto"

        picture = file.read()
        if len(picture) > 100 * 1024:
            return "VIRHE: liian suuri kuva"

        user_id = session["user_id"]
        users.update_picture(user_id, picture)
        return redirect("/user/" + str(user_id))

@app.route("/pfp/<int:user_id>")
def show_profile_picture(user_id):
    picture = users.get_profile_picture(user_id)
    if not picture:
        abort(404)
    response = make_response(bytes(picture))
    response.headers.set("Content-Type", "image/png")
    return response

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
    if len(description) > 100 or not image:
        abort(403)
    if not description:
        description = ""
    if len(image) > 5000*5000:
        return "VIRHE: liian suuri kuva"
    items.add_item(user_id, image, description)
    return redirect("/")

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_item.html", item = item)

@app.route("/update_item", methods = ["POST"])
def update_item():
    require_login()
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
    if len(description) > 100 or not image:
        abort(403)
    if not description:
        description = ""
    if len(image) > 1024*1024:
        return "VIRHE: liian suuri kuva"
    items.update_item(item_id, image, description)
    return redirect("/item/" + str(item_id))

@app.route("/remove_item/<int:item_id>", methods = ["GET","POST"])
def remove_item(item_id):

    require_login()
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

    try:
        users.create_user(username, password1)
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

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

def require_login():
    if "user_id" not in session:
        abort(403)