CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE Items (
    id INTEGER PRIMARY KEY,
    description TEXT,
    user_id INTEGER REFERENCES Users,
    images BLOB
);

CREATE TABLE Comments (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES Users,
    post_id INTEGER REFERENCES Items
);