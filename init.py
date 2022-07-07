import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")

conn.execute('CREATE TABLE users (username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, salt TEXT NOT NULL)')
conn.execute('CREATE TABLE urls (identifier TEXT UNIQUE NOT NULL, url TEXT NOT NULL, username TEXT NOT NULL, FOREIGN KEY (username) REFERENCES users(username))')

print("Table created successfully")
conn.close()