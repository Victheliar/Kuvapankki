import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM Users")
db.execute("DELETE FROM Items")
db.execute("DELETE FROM Comments")

user_count = 1000
thread_count = 10**5
message_count = 10**6

for i in range(1, user_count + 1):
    db.execute("INSERT INTO Users (username) VALUES (?)",
               ["user" + str(i)])

for i in range(1, thread_count + 1):
    db.execute("INSERT INTO Items (description) VALUES (?)",
               ["thread" + str(i)])

for i in range(1, message_count + 1):
    user_id = random.randint(1, user_count)
    thread_id = random.randint(1, thread_count)
    db.execute("""INSERT INTO Comments (content, user_id, post_id)
                  VALUES (?, ?, ?)""",
               ["message" + str(i), user_id, thread_id])

db.commit()
db.close()