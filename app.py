import hashlib
import sqlite3
import uuid
import validators

from flask import Flask, request, Response, render_template, redirect, url_for, abort
import requests

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def checkPassword(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user is not None:
        hashed_password = user["password"]
        salt = user["salt"]

        if hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest() == hashed_password:
            return True
    return False

def addUrl(url, username):
    conn = get_db_connection()
    id = uuid.uuid4()
    while existingIdentifier(id):
        id = uuid.uuid4()
    conn.execute('INSERT INTO urls (identifier, url, username) VALUES (?, ?, ?)', (str(id), str(url), str(username)))
    conn.commit()
    conn.close()
    return id

def getUrl(identifier):
    conn = get_db_connection()
    url = conn.execute('SELECT * FROM urls WHERE identifier = ?', (str(identifier),)).fetchone()
    conn.close()
    if url is not None:
        return url["url"]
    return None

def existingIdentifier(identifier):
    if getUrl(identifier) is not None:
        return True
    return False

@app.route('/')
def index():  # put application's code here
    return redirect(url_for('urlAdd'))

@app.route('/url/add', methods = ['GET', 'POST'])
def urlAdd():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        url = request.form.get('url')

        if checkPassword(username, password):
            if validators.url(url):
                identifier = addUrl(url, username)
                return render_template('urlAdded.html', info="Sucessfully added", url=url_for('urlRelay', identifier=identifier, _external=True))
            return render_template('urlAdded.html', info="Invalid url", url="Invalid url")
        return render_template('urlAdded.html', info="Wrong username/password", url="Wrong username/password")
    elif request.method == 'GET':
        return render_template('urlAdd.html')

@app.route('/url/relay/<identifier>')
def urlRelay(identifier):
    if existingIdentifier(identifier):
        resp = requests.request(
            method=request.method,
            url=getUrl(identifier),
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response
    else:
        abort(404)


if __name__ == '__main__':
    app.run()
