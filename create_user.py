import hashlib
import sqlite3
import uuid

print("Create user for adding new urls.")

username = input("Type in the username: ")
password = input("Type in the password: ")

salt = uuid.uuid4().hex
hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()

connection = sqlite3.connect('database.db')

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
            (username, hashed_password, salt)
            )

connection.commit()
connection.close()

print("User created!")