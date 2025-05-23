import math
import secrets
import sqlite3

from flask import Flask
from flask import redirect, flash, render_template, request, session, make_response, abort
import markupsafe

import config
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
@app.route("/<int:page>")
def index(page = 1):
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
    return render_template("index.html", images = all_images, items = all_items,
                           classes = classes, page = page, page_count = page_count)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("find_item.html", query = query, results = results)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    posts = users.get_posts(user_id)
    return render_template("user.html", user = user, posts = posts)

@app.route("/add_profile_picture", methods = ["GET", "POST"])
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
            flash("VIRHE: Liian suuri kuva")
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
    if len(image) > 500*1024:
        flash("VIRHE: Liian suuri kuva")
        return redirect("/")

    all_classes = items.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                abort(403)
            if value not in all_classes[title]:
                abort(403)
            classes.append((title, value))
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

    all_classes = items.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = []
    for entry in items.get_classes(item_id):
        classes[entry["title"]].append(entry["value"])

    return render_template("edit_item.html", item = item, all_classes = all_classes,
                           classes = classes)

@app.route("/update_item", methods = ["POST"])
def update_item():
    require_login()
    check_csrf()
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    description = request.form["description"]
    if len(description) > 5000:
        abort(403)
    if not description:
        description = ""

    all_classes = items.get_all_classes()
    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                abort(403)
            if value not in all_classes[title]:
                abort(403)
            classes.append((title, value))

    items.update_item(item_id, description, classes)
    return redirect("/item/" + str(item_id))

@app.route("/remove_item/<int:item_id>", methods = ["GET", "POST"])
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
    response.headers.set("Content-Type", "image/png")
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
    return render_template("register.html", filled = {})

@app.route("/create", methods = ["POST"])
def create():
    username = request.form["username"]
    if len(username) > 16:
        abort(403)
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        flash("VIRHE: Salasanat eivät täsmää")
        filled = {"username": username}
        return render_template("register.html", filled = filled)

    if not password1 or not password2:
        flash("VIRHE: Salasana ei voi olla tyhjä!")
        filled = {"username": username}
        return render_template("register.html", filled = filled)

    try:
        users.create_user(username, password1)
        flash("Tunnuksen luominen onnistui!")
        return redirect("/")

    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        filled = {"username": username}
        return render_template("register.html", filled = filled)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", next_page = request.referrer)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(next_page)
        else:
            flash("VIRHE: Väärä tunnus tai salasana!")
            return render_template("login.html", next_page = next_page)

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
