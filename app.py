import sqlite3
from flask import Flask
from flask import redirect, flash, render_template, request, session, make_response, abort
import db
import config
import items
import users
import secrets
import math

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    item_count = items.item_count()
    page_count = math.ceil(item_count / page_size)
    page_count = max(page_count, 1)
    
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))
    
    all_images = items.get_images(page, page_size)
    all_items = items.get_items(page, page_size)
    classes = items.get_all_classes()
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("index.html", images = all_images, items = all_items, classes = classes, query = query, 
                           results = results, page=page, page_count=page_count)

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
        check_csrf()
        file = request.files["picture"]
        if not file.filename.endswith(".png"):
            flash("VIRHE: Lähettämäsi tiedosto ei ole png-tiedosto")
            return redirect("/add_profile_picture")

        picture = file.read()
        if len(picture) > 100 * 1024:
            flash("VIRHE: liian suuri kuva")
            return redirect("/add_profile_picture")

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

@app.route("/add_image", methods = ["POST"])
def add_image():
    require_login()
    check_csrf()
    file = request.files["image"]
    if not file.filename.endswith(".png"):
        flash("VIRHE: Lähettämäsi tiedosto ei ole png-tiedosto")
        return redirect("/")
    image = file.read()
    user_id = session["user_id"]
    description = request.form["description"]
    if len(description) > 5000 or not image:
        abort(403)
    if not description:
        description = ""
    description = description.replace("\n", "<br />")
    if len(image) > 1024*1024:
        flash("VIRHE: liian suuri kuva")
        return redirect("/")
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            parts = entry.split(":")
            classes.append((parts[0], parts[1]))
    items.add_item(user_id, image, description, classes)
    flash("Julkaisu onnistui")
    return redirect("/")

@app.route("/add_comment", methods = ["POST"])
def add_comment():
    require_login()
    check_csrf()
    comment = request.form["comment"]
    if len(comment) > 5000 or not comment:
        abort(403)
    comment = comment.replace("\n", "<br />")
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(403)
    user_id = session["user_id"]
    items.add_comment(item_id, user_id, comment)
    return redirect("/item/" + str(item_id))

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
    check_csrf()
    file = request.files["image"]
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    description = request.form["description"]
    if not file.filename.endswith(".png"):
        flash("VIRHE: Lähettämäsi tiedosto ei ole png-tiedosto")
        return redirect("/edit_item/" + str(item_id))
    image = file.read()
    if len(description) > 5000 or not image:
        abort(403)
    if not description:
        description = ""
    description = description.replace("\n", "<br />")
    if len(image) > 1024*1024:
        flash("VIRHE: liian suuri kuva")
        return redirect("/edit_item/" + str(item_id))
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
        check_csrf()
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
    classes = items.get_classes(item_id)
    comments = items.get_comments(item_id)
    return render_template("show_item.html", item = item, classes = classes, comments = comments)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods = ["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        flash("VIRHE: Salasanat eivät täsmää")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        return redirect("/register")
    return redirect("/")

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
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("VIRHE: Väärä tunnus tai salasana!")
            return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)

    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)