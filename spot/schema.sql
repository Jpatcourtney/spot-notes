DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS spot;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE spot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  note TEXT NOT NULL,
  lat REAL,
  lng REAL,
  local_time TIMESTAMP,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
