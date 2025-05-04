from werkzeug.security import generate_password_hash, check_password_hash
import db

def get_user(user_id):
    sql = """SELECT id, username,
    profile_picture IS NOT NULL has_pfp
    FROM Users
    WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_posts(user_id):
    sql = """SELECT I.id,
                    I.description,
                    I.images
            FROM Items I, Users U
            WHERE I.user_id = U.id
            AND U.id = ?
            ORDER BY I.id DESC"""
    return db.query(sql, [user_id])

def update_picture(user_id, picture):
    sql = "UPDATE Users SET profile_picture = ? WHERE id = ?"
    db.execute(sql, [picture, user_id])

def get_profile_picture(user_id):
    sql = "SELECT profile_picture FROM Users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None

def create_user(username, password1):
    password_hash = generate_password_hash(password1)
    sql = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM Users WHERE username = ?"
    result = db.query(sql, [username])

    if not result:
        return None
    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None
